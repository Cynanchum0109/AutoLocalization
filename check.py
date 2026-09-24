#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py - 体检 out/progress.json 里的全部译文。

比 batch_merge 的单批校验更全：跨批检查术语/一致性问题。

检查项：
  1. 格式码丢失/多出（硬伤）
  2. 译文残留哨兵、残留成片英文
  3. 同一原文出现多种译法（不一致）
  4. 译文长度相对原文异常（疑似漏译/塞私货）
  5. 译文与原文完全相同

用法：python check.py
"""

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from limbus.fmtcode import (LATIN_WORD_RE, SOFT_TAG_RE, STRICT_KW_RE, has_cjk,
                            keyword_diff, layout_diff, strict_tokens)
from limbus.jsonio import load_json, setup_stdout


def main():
    setup_stdout()
    progress = load_json(config.PROGRESS) or {}
    if not progress:
        print("progress.json 为空。")
        return

    fmt_bad, no_cjk, same, long_en, sentinel = [], [], [], [], []
    tag_lost, tag_added = [], []
    ratio_bad = []
    by_source = defaultdict(set)

    for key, e in progress.items():
        en, zh = e.get("en", ""), e.get("zh", "")
        scope, field = key.split("/", 1)[0], key.rsplit("#", 1)[-1]
        if strict_tokens(en) != strict_tokens(zh):
            fmt_bad.append(key)
        elif config.keyword_brackets(scope, field) and any(keyword_diff(en, zh)):
            fmt_bad.append(key)
        lost, bad_added, _ = layout_diff(en, zh)
        if lost:
            tag_lost.append(key)
        if bad_added:
            tag_added.append(key)
        if "⟦" in zh or "⟧" in zh:
            sentinel.append(key)
        if not has_cjk(zh):
            no_cjk.append(key)
        elif zh == en:
            same.append(key)
        # 中文通常比英文短。译文里出现 >=4 个英文单词，多半是漏译整句。
        # 先剥掉标签与机制关键词 —— [BulletPropellantSpecial] 这种是该保留的 ID，不是漏译。
        residue = STRICT_KW_RE.sub("", zh)
        residue = SOFT_TAG_RE.sub("", residue)
        words = LATIN_WORD_RE.findall(residue)
        if len(words) >= 4:
            long_en.append(key)
        if en and zh:
            r = len(zh) / len(en)
            if r > 1.6 or r < 0.15:
                ratio_bad.append((key, round(r, 2)))
        by_source[en].add(zh)

    inconsistent = {en: zhs for en, zhs in by_source.items()
                    if len(zhs) > 1 and len(en) >= 4}

    def dump(title, items, fmt=lambda x: f"  - {x}", limit=20):
        print(f"\n== {title}：{len(items)}")
        for x in list(items)[:limit]:
            print(fmt(x))
        if len(items) > limit:
            print(f"  …… 另有 {len(items) - limit} 条")

    print(f"译文总数：{len(progress)}")
    dump("强标记不一致（硬伤）：<color> {0} [Keyword] 乱码", fmt_bad)
    dump("排版标签丢失（硬伤）：<i> <b> <u> <s> <size> <ruby> 等", tag_lost)
    dump("擅自新增排版标签（硬伤）", tag_added)
    dump("残留哨兵 ⟦n⟧", sentinel)
    dump("译文不含中文", no_cjk)
    dump("译文与原文相同", same)
    dump("译文里有 >=4 个连续英文单词（疑似漏译）", long_en)
    dump("长度比异常", ratio_bad, fmt=lambda x: f"  - {x[0]}  比值 {x[1]}")
    dump("同一原文多种译法", list(inconsistent.items()),
         fmt=lambda x: f"  - {x[0][:50]!r} → {sorted(x[1])}")

    hard = len(fmt_bad) + len(sentinel) + len(tag_lost) + len(tag_added)
    print(f"\n硬伤合计 {hard} 条。" if hard else "\n没有硬伤。")


if __name__ == "__main__":
    main()
