import argparse
from pathlib import Path

from .extract import extract_reading_passages, write_passage_json
from .grammar import detect_grammar, render_grammar_notes
from .io import read_source
from .markdown import render_formatted_article
from .sentence_analysis import find_complex_sentences, render_sentence_prompt
from .workflow import build_from_exam


def main() -> None:
    parser = argparse.ArgumentParser(prog="kaoyan-reading", description="考研英语阅读真题提取与精读笔记生成")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser("extract", help="从电子版真题中提取阅读文章和题目")
    extract_parser.add_argument("source", help="真题文件，支持 .txt/.md/.docx/.pdf")
    extract_parser.add_argument("--year", help="年份，如 2010")
    extract_parser.add_argument("--out", default="extracted", help="输出目录")

    workflow_parser = subparsers.add_parser("init-workflow", help="提取真题并初始化 Obsidian 精读工作流")
    workflow_parser.add_argument("source", help="真题文件，支持 .txt/.md/.docx/.pdf")
    workflow_parser.add_argument("--year", help="年份，如 2010")
    workflow_parser.add_argument("--out", default="intermediate", help="输出目录")
    workflow_parser.add_argument("--sentence-limit", type=int, default=8, help="每篇长难句候选数量")

    sentence_parser = subparsers.add_parser("sentences", help="从文章中筛选长难句候选并生成分析任务")
    sentence_parser.add_argument("source", help="文章文件，支持 .txt/.md/.docx/.pdf")
    sentence_parser.add_argument("--topic", required=True, help="主题名")
    sentence_parser.add_argument("--out", required=True, help="输出 markdown 文件")
    sentence_parser.add_argument("--limit", type=int, default=8, help="候选句数量")

    grammar_parser = subparsers.add_parser("grammar", help="从文章中扫描语法现象并生成 grammar-notes.md 草稿")
    grammar_parser.add_argument("source", help="文章文件，支持 .txt/.md/.docx/.pdf")
    grammar_parser.add_argument("--topic", required=True, help="主题名")
    grammar_parser.add_argument("--source-label", default="考研英语真题", help="frontmatter sources 字段")
    grammar_parser.add_argument("--out", required=True, help="输出 markdown 文件")

    args = parser.parse_args()
    if args.command == "extract":
        _cmd_extract(args)
    elif args.command == "init-workflow":
        count = build_from_exam(args.source, args.out, year=args.year, sentence_limit=args.sentence_limit)
        print(f"Initialized {count} passage workflow folder(s) under {args.out}")
    elif args.command == "sentences":
        text = read_source(args.source)
        candidates = find_complex_sentences(text, limit=args.limit)
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_sentence_prompt(candidates, topic=args.topic), encoding="utf-8")
        print(f"Wrote {len(candidates)} sentence candidate(s) to {output}")
    elif args.command == "grammar":
        text = read_source(args.source)
        grouped = detect_grammar(text)
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_grammar_notes(grouped, topic=args.topic, source=args.source_label), encoding="utf-8")
        total = sum(len(items) for items in grouped.values())
        print(f"Wrote {total} grammar item(s) to {output}")


def _cmd_extract(args: argparse.Namespace) -> None:
    text = read_source(args.source)
    passages = extract_reading_passages(text, year=args.year)
    base = Path(args.out)
    for passage in passages:
        topic = f"{args.year or 'exam'}-text{passage.index}"
        target = base / topic
        write_passage_json(passage, target / "reading.json")
        (target / "formatted-article.md").write_text(
            render_formatted_article(passage, topic=topic, source=args.source),
            encoding="utf-8",
        )
    print(f"Extracted {len(passages)} passage(s) to {base}")


if __name__ == "__main__":
    main()

