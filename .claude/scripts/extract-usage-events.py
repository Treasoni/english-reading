#!/usr/bin/env python3
"""Extract per-call LLM usage events from the current Claude Code session transcript.

Runs automatically from the SessionEnd hook in .claude/settings.json. Reads the
SessionEnd hook input from stdin (JSON with a `session_id` field), locates the
matching transcript under ~/.claude/projects/, parses `assistant` messages, and
appends one event per call to .llm/prompt-cache/events/<session_id>.jsonl.

Notes on field provenance (do not treat these as equal):
- token / cache / latency numbers are REAL values copied from the transcript.
- `request_type` / `template_id` are APPROXIMATE, inferred from the user text
  that preceded each assistant turn (keyword match on the vault's skill
  triggers). They exist only to group telemetry; the platform never logs them.

Never logs raw user input, model output, or secrets.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Skill trigger keywords -> (request_type, template_id)
SKILL_TRIGGERS = [
    (("translate", "翻译"), "translate", "skill:translate"),
    (("format-article", "排版"), "format_article", "skill:format-article"),
    (("organize-grammar", "语法整理", "整理零散"), "organize_grammar", "skill:organize-grammar"),
    (("analyze-sentence", "长难句"), "analyze_sentence", "skill:analyze-sentence"),
    (("compile-note", "整合", "综合笔记"), "compile_note", "skill:compile-note"),
    (("extract-vocabulary", "生词", "词汇表"), "extract_vocabulary", "skill:extract-vocabulary"),
    (("summarize-grammar", "语法总结", "汇总语法"), "summarize_grammar", "skill:summarize-grammar"),
    (("vocab-diff", "易混淆", "单词辨析"), "vocab_diff", "skill:vocab-diff"),
    (("generate-reading-note", "精读工作流", "批量生成考研"), "generate_reading_note", "skill:generate-reading-note"),
]

DEFAULT_TYPE = "claude_code_chat"
DEFAULT_TEMPLATE = "unclassified"


def infer_type(user_text: str):
    """Best-effort mapping from a user message to (request_type, template_id)."""
    text = user_text or ""
    for keywords, request_type, template_id in SKILL_TRIGGERS:
        if any(kw in text for kw in keywords):
            return request_type, template_id
    return DEFAULT_TYPE, DEFAULT_TEMPLATE


def parse_ts(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def user_text_of(o: dict) -> str:
    content = (o.get("message") or {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text" and c.get("text"):
                parts.append(c["text"])
        return " ".join(parts)
    return ""


def locate_transcript(session_id: str):
    base = Path.home() / ".claude" / "projects"
    if session_id:
        for d in base.glob("*/"):
            cand = d / f"{session_id}.jsonl"
            if cand.exists():
                return cand
    # Fallback: newest transcript whose content carries this cwd (robust to the
    # platform's opaque directory-name encoding for non-ASCII paths).
    cwd_marker = f'"{Path.cwd()}"'
    best, best_mtime = None, 0.0
    for d in base.glob("*/"):
        files = sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            continue
        f = files[0]
        mtime = f.stat().st_mtime
        if mtime <= best_mtime:
            continue
        try:
            head = f.read_text(encoding="utf-8", errors="ignore")[:200000]
        except Exception:
            continue
        if cwd_marker in head:
            best, best_mtime = f, mtime
    return best


def extract_events(transcript: Path):
    events = []
    seen = set()
    pending_user_text = None
    pending_user_ts = None
    for line in transcript.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        t = o.get("type")
        if t == "user":
            text = user_text_of(o)
            if text.strip():
                pending_user_text = text
                pending_user_ts = parse_ts(o.get("timestamp"))
        elif t == "assistant":
            msg = o.get("message") or {}
            usage = msg.get("usage") or {}
            if not usage:
                continue
            msg_id = msg.get("id")
            if msg_id and msg_id in seen:
                continue
            seen.add(msg_id)
            in_tok = usage.get("input_tokens")
            out_tok = usage.get("output_tokens")
            if in_tok is None and out_tok is None:
                continue
            request_type, template_id = infer_type(pending_user_text)
            ts = parse_ts(o.get("timestamp"))
            latency_ms = None
            if ts and pending_user_ts:
                latency_ms = max(0, int((ts - pending_user_ts).total_seconds() * 1000))
            event = {
                "timestamp": (ts or datetime.now(timezone.utc)).isoformat(),
                "request_type": request_type,
                "template_id": template_id,
                "template_version": "v1",
                "model": msg.get("model") or "unknown",
                "input_tokens": in_tok if in_tok is not None else 0,
                "output_tokens": out_tok if out_tok is not None else 0,
                "latency_ms": latency_ms if latency_ms is not None else 0,
                "input_reference": f"transcript:{transcript.stem}",
                "metadata": {
                    "source": "claude-code-session-end",
                    "message_id": msg_id or "",
                },
            }
            # cache fields: include ONLY when the provider returned them.
            cache_read = usage.get("cache_read_input_tokens")
            cache_write = usage.get("cache_creation_input_tokens")
            if cache_read is not None:
                event["cache_read_tokens"] = cache_read
            if cache_write is not None:
                event["cache_write_tokens"] = cache_write
            events.append(event)
    return events


def main() -> int:
    hook_input = {}
    try:
        raw = sys.stdin.read()
        if raw.strip():
            hook_input = json.loads(raw)
    except Exception:
        pass
    session_id = hook_input.get("session_id")

    transcript = locate_transcript(session_id)
    if transcript is None:
        sys.stderr.write("extract-usage-events: no transcript found\n")
        return 1

    events = extract_events(transcript)
    if not events:
        sys.stderr.write(f"extract-usage-events: no usage events in {transcript.name}\n")
        return 0

    out_dir = Path(".llm") / "prompt-cache" / "events"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{transcript.stem}.jsonl"

    # Idempotent append: skip message ids already written.
    existing = set()
    if out_file.exists():
        for line in out_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                existing.add((json.loads(line).get("metadata") or {}).get("message_id", ""))
            except Exception:
                pass
    fresh = [ev for ev in events if ev["metadata"]["message_id"] not in existing]
    if fresh:
        with out_file.open("a", encoding="utf-8") as f:
            for ev in fresh:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    print(f"extract-usage-events: wrote {len(fresh)} events to {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
