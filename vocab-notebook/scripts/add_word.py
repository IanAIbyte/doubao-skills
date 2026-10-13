#!/usr/bin/env python3
"""向本地「英语单词本.md」追加一个单词条目（H1 段落式 Markdown），自动查重。

条目格式：
# word

概述句。

- 词性：...
- 音标：英 /.../，美 /.../
- 常见搭配：
  - ...
- 例句：...
"""
import argparse
import json
import os
import re


def build_entry(args) -> str:
    lines = [f"# {args.word}", "", args.summary, ""]
    lines.append(f"- 词性：{args.pos}")
    phon = []
    if args.phonetic_uk:
        phon.append(f"英 {args.phonetic_uk}")
    if args.phonetic_us:
        phon.append(f"美 {args.phonetic_us}")
    if phon:
        lines.append(f"- 音标：{'，'.join(phon)}")
    if args.collocation:
        lines.append("- 常见搭配：")
        for c in args.collocation:
            lines.append(f"  - {c}")
    lines.append(f"- 例句：{args.example}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="英语单词本.md 的路径")
    ap.add_argument("--word", required=True)
    ap.add_argument("--summary", required=True, help="概述句，如：最常见的意思是……")
    ap.add_argument("--pos", required=True, help="如：副词 (adv.)")
    ap.add_argument("--phonetic-uk", default="")
    ap.add_argument("--phonetic-us", default="")
    ap.add_argument("--collocation", action="append", default=[], help="常见搭配，可重复传入")
    ap.add_argument("--example", required=True, help="英文例句.（中文译文。）")
    args = ap.parse_args()

    target = os.path.abspath(args.file)
    entry = build_entry(args)

    # 文件不存在：新建（直接以单词 H1 开头）
    if not os.path.exists(target):
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(entry + "\n")
        print(json.dumps({"status": "created", "file": target}, ensure_ascii=False))
        return

    with open(target, "r", encoding="utf-8") as f:
        content = f.read()

    # 查重：是否已存在该单词的 H1 标题
    pattern = r"(?m)^#\s+" + re.escape(args.word.strip()) + r"\s*$"
    if re.search(pattern, content, re.IGNORECASE):
        print(json.dumps({"status": "duplicate", "word": args.word, "file": target}, ensure_ascii=False))
        return

    content = content.rstrip() + "\n\n" + entry + "\n"
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)

    print(json.dumps({"status": "added", "file": target}, ensure_ascii=False))


if __name__ == "__main__":
    main()
