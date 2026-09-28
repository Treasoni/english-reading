#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P9 全局汇总：把 2016-passage4 的语法 / 固定搭配内容增量合并进两个根笔记。"""
import re
import sys

ROOT = "/Users/zhqznc/Documents/考研英语阅读"
G = f"{ROOT}/语法总结笔记.md"
C = f"{ROOT}/固定搭配与词组笔记.md"
SRC_G = f"{ROOT}/intermediate/2016-passage4-young-americans-success/grammar-notes.md"
SRC_C = f"{ROOT}/intermediate/2016-passage4-young-americans-success/固定搭配与词组笔记.md"
HDR = f"{ROOT}/workspace/tmp-p9-g-header.md"
LNK = f"{ROOT}/workspace/tmp-p9-g-linkage.md"
TAG = "（来源：2016-passage4-young-americans-success）"
DATE = "2026-09-28"
SLUG = "2016-passage4-young-americans-success"

DRY = "--apply" not in sys.argv


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def rep1(text, old, new, label):
    n = text.count(old)
    assert n == 1, f"[{label}] anchor count={n}: {old[:60]!r}"
    return text.replace(old, new)


def head_tag(block, prefix=None):
    """给块的第一行标题补来源标注；prefix 用于替换原标题。"""
    lines = block.split("\n")
    assert lines[0].startswith("#"), lines[0][:40]
    lines[0] = ((prefix or lines[0].rstrip()) + TAG)
    return "\n".join(lines)


def blocks_of(src_path, start_pred, drop_h2=False):
    raw = read(src_path).split("\n")
    start = next(i for i, l in enumerate(raw) if start_pred(l))
    body = raw[start:]
    while body and (body[-1].strip() == "" or body[-1].strip() == "---"
                    or body[-1].startswith("_本文件为")):
        body.pop()
    if drop_h2:
        body = [l for l in body if not l.startswith("## ")]
    text = "\n".join(body).strip("\n")
    blocks = [b.strip("\n") for b in re.split(r"\n---\n", text)]
    return [b for b in blocks if b.strip()]


# ---------------- 语法总结笔记.md ----------------
gb = blocks_of(SRC_G, lambda l: l.startswith("### "), drop_h2=True)
clauses, nonfinite, prep, tail = [], [], [], []
for b in gb:
    h = b.split("\n")[0]
    if h.startswith("### 从句："):
        clauses.append(b)
    elif h.startswith("### 非谓语："):
        nonfinite.append(b)
    elif h.startswith("### 介词与连词："):
        prep.append(b)
    elif h.startswith("### 跨节联动复习"):
        continue  # 由手写的 `### 联动复习：2016 Passage 4 …` 取代
    else:
        tail.append(b)

print("grammar blocks:", len(gb), "=> 从句", len(clauses), "非谓语", len(nonfinite),
      "介词", len(prep), "尾部", len(tail))
for b in clauses + nonfinite + prep + tail:
    print("   -", b.split("\n")[0][:80])

assert len(clauses) == 10 and len(nonfinite) == 5 and len(prep) == 2 and len(tail) == 14

g = read(G)
if not DRY:
    g = rep1(g, "updated: 2026-09-26", f"updated: {DATE}", "g.updated")
    g = rep1(g, "total_sources: 63", "total_sources: 64", "g.total_sources")
    g = rep1(
        g,
        f'  - "intermediate/2016-passage3-deep-reading/grammar-notes.md | 2026-09-26 | processed"',
        f'  - "intermediate/2016-passage3-deep-reading/grammar-notes.md | 2026-09-26 | processed"\n'
        f'  - "intermediate/{SLUG}/grammar-notes.md | {DATE} | processed"',
        "g.processed_sources",
    )
    g = rep1(g, "下 63 篇单篇语法笔记", "下 64 篇单篇语法笔记", "g.usage_count")

    g = rep1(
        g,
        " | 35 | ★★★★★ |",
        "；**2016 P4**：what 介词宾语从句（agree on what constitutes the finish line）、while 让步 / 对比状从、who 限制性定从、"
        "省略 that 与不省略 that 的宾语从句、suggest / maintain / agree that、嵌套定语从句（priorities and expectations that …）、"
        "now that、even though + when、it 形式主语的比较结构、be struck that 补足 | 36 | ★★★★★ |",
        "g.row_clause",
    )
    g = rep1(
        g,
        " | 31 | ★★★★★ |",
        "；**2016 P4**：动名词并列作介词宾语（including getting married … / by regularly changing jobs / in reaching）、"
        "现在分词作后置定语（those starting out in life）与状语（Looking back）、五重并列不定式、"
        "不定式作宾语与目的状语（struggle to find / afford to pay / to make that happen） | 32 | ★★★★★ |",
        "g.row_nonfinite",
    )
    g = rep1(
        g,
        " | 36 | ★★★★ |",
        "；**2016 P4**：范围与路径（From career to community and family／from consumer preferences to housing patterns to politics）、"
        "框架状语与固定搭配（against a backdrop of / in the aftermath of / across generational lines / converge on / on one's own）"
        " | 37 | ★★★★ |",
        "g.row_prep",
    )
    g = rep1(
        g,
        " | 48 | ★★★ |",
        "；**2016 P4**：those 指人代词与 the young / the old 名词化、一般现在 vs 现在进行、现在完成 vs 过去完成、"
        "一般过去与 could 的过去能力、被动语态与副词最高级（are best served by）、系表结构（is struck）、"
        "情态动词（should / could / can't）、否定前移、并列结构与 such … as …、冒号与引述性引号、多层嵌套长难句、构词法、熟词生义"
        " | 49 | ★★★ |",
        "g.row_more",
    )

    for anchor, bs in (
        ("## 非谓语动词 (Non-finite Verbs)", clauses),
        ("## 介词与连词 (Prepositions & Conjunctions)", nonfinite),
        ("## 倒装与强调 (Inversion & Emphasis)", prep),
    ):
        ins = "---\n\n" + "\n\n---\n\n".join(head_tag(b) for b in bs) + "\n\n"
        g = rep1(g, anchor, ins + anchor, f"g.insert:{anchor}")

    tail_text = read(HDR).rstrip("\n") + "\n\n---\n\n"
    tail_text += "\n\n---\n\n".join(head_tag(b) for b in tail)
    tail_text += "\n\n---\n\n" + read(LNK).rstrip("\n")
    g = g.rstrip("\n") + "\n\n" + tail_text + "\n"
    write(G, g)
    print("grammar written, bytes:", len(g.encode("utf-8")))

# ---------------- 固定搭配与词组笔记.md ----------------
cb = blocks_of(SRC_C, lambda l: l.startswith("## "))
print("colloc blocks:", len(cb))
for b in cb:
    print("   -", b.split("\n")[0][:80])
assert len(cb) == 7

c = read(C)
if not DRY:
    c = rep1(c, "updated: 2026-09-26", f"updated: {DATE}", "c.updated")
    c = rep1(c, "total_sources: 63", "total_sources: 64", "c.total_sources")
    c = rep1(
        c,
        '  - "intermediate/2016-passage3-deep-reading/固定搭配与词组笔记.md | 2026-09-26 | processed"',
        '  - "intermediate/2016-passage3-deep-reading/固定搭配与词组笔记.md | 2026-09-26 | processed"\n'
        f'  - "intermediate/{SLUG}/固定搭配与词组笔记.md | {DATE} | processed"',
        "c.processed_sources",
    )
    c = rep1(
        c,
        "）。每条例句均标注来源篇章",
        "；**2016 P4**：a road map to success、a backdrop of drastic changes、population structure、generational lines、"
        "the traditional milestones of a successful life、the finish line of a fulfilling life、personal fulfillment、"
        "a faster pace of life、financial security、the searing Great Recession、consumer preferences、housing patterns、"
        "overwhelming majorities、the prospects for、signpost achievements、a good-paying job、affordable housing、"
        "an auto technician、mortgage payments、the upper middle class、get started in life；熟词生义 prize / constitute / favor / "
        "maintain / serve / secure / struck / climb / signpost；易混辨析 prize / appreciate / value / cherish、"
        "milestone / landmark / breakthrough / watershed、constitute / compose / comprise / consist of、"
        "maintain / claim / assert / contend、secure / obtain / acquire / attain、aftermath / consequence / fallout / result、"
        "virtually / almost / practically / literally、converge / coincide / agree、prospect / perspective / outlook / expectation、"
        "affordable / reasonable / economical / cheap、mortgage / loan / credit / debt、suburb / outskirts / countryside / downtown、"
        "capable / able / competent / qualified、optimistic / hopeful / positive / sanguine"
        "）。每条例句均标注来源篇章",
        "c.abstract",
    )
    c = rep1(
        c,
        "（含 11 组易混辨析） | 3 | ★★★★ |",
        "（含 11 组易混辨析）；Passage 4：a road map to success、across generational lines、a faster pace of life、"
        "the searing Great Recession、overwhelming majorities、signpost achievements、a good-paying job、affordable housing、"
        "on one's own、be capable of、be best served by、such … as …、converge on、rent sth. out；"
        "熟词生义 prize / constitute / favor / maintain / serve / secure / struck / climb / signpost；"
        "易混辨析 prize / appreciate / value / cherish、milestone / landmark / breakthrough / watershed、"
        "constitute / compose / comprise / consist of、maintain / claim / assert / contend、secure / obtain / acquire / attain、"
        "aftermath / consequence / fallout / result、virtually / almost / practically / literally、converge / coincide / agree、"
        "prospect / perspective / outlook / expectation、affordable / reasonable / economical / cheap、"
        "mortgage / loan / credit / debt、suburb / outskirts / countryside / downtown、capable / able / competent / qualified、"
        "optimistic / hopeful / positive / sanguine | 4 | ★★★★ |",
        "c.row_2016",
    )

    def c_head(b):
        lines = b.split("\n")
        m = re.match(r"^## [一二三四五六七八九十]+、(.+)$", lines[0])
        assert m, lines[0]
        lines[0] = f"### 2016 Passage 4：{m.group(1)}{TAG}"
        return "\n".join(lines)

    def c_sub(b):
        # 内层 `### N.` 降一级为 `#### N.`
        return "\n".join(("#" + l) if l.startswith("### ") else l for l in b.split("\n"))

    parts = []
    for b in cb:
        b = c_sub(b)  # 先把内层 `### N.` 降为 `#### N.`
        b = c_head(b)  # 再把类别标题改写为 `### 2016 Passage 4：…`
        parts.append(b)
    c = c.rstrip("\n") + "\n\n---\n\n" + "\n\n---\n\n".join(parts) + "\n\n" + TAG + "\n"
    write(C, c)
    print("colloc written, bytes:", len(c.encode("utf-8")))

print("DRY RUN" if DRY else "APPLIED")