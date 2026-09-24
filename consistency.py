#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""consistency.py - 全库一致性审计：同一个专名短语在译文里是否有多种写法。

扫 out/progress.json，抽 EN 里的大写名词短语（见 limbus/ourterms.py），
对出现 ≥ --min 次的短语，统计其译文里的中文 n-gram：在这组句子里常见、
在全库里少见的 n-gram 就是该词的候选译法。一个短语有多个候选 → 疑似分裂。

只做提示，不改任何东西。结果写 out/consistency.md。

用法：
  python consistency.py                 # 全库
  python consistency.py --file floor-b1 # 只看 key 含该串的条目
  python consistency.py --min 5 --top 4
"""

import argparse
import math
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from limbus.jsonio import load_json, setup_stdout
from limbus.ourterms import phrases
from limbus.glossary import Glossary

CJK = re.compile(r"[\u4e00-\u9fff]+")
OUT = os.path.join(config.OUT_DIR, "consistency.md")


def ngrams(zh, lo=2, hi=5):
    out = set()
    for run in CJK.findall(zh):
        for n in range(lo, hi + 1):
            for i in range(len(run) - n + 1):
                out.add(run[i:i + n])
    return out


def main():
    setup_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=3, help="短语至少出现次数")
    ap.add_argument("--top", type=int, default=5, help="每个短语列几个候选译法")
    ap.add_argument("--file", help="只看 key 含该串的条目")
    args = ap.parse_args()

    progress = load_json(config.PROGRESS) or {}
    rows = [(k, v["en"], v["zh"]) for k, v in progress.items()
            if isinstance(v, dict) and v.get("en") and v.get("zh")
            and not k.startswith(config.MECH_SCOPE + "/")   # 机制文本另有模板，不在此审
            and (not args.file or args.file in k)]
    gloss = Glossary().terms
    gloss_zh = {k.lstrip("!"): re.split(r"[（(/]", v)[0].strip() for k, v in gloss.items()}

    # 全库 n-gram 文档频率
    df = Counter()
    doc_grams = {}
    for k, en, zh in rows:
        g = ngrams(zh)
        doc_grams[k] = g
        df.update(g)
    n_docs = max(len(rows), 1)

    # 单词短语：全库里小写形式比大写多 → 只是句首大写的普通词（Yeah / Looks / Does）
    all_en = "\n".join(en for _, en, _ in rows)
    lower_cnt = Counter(w for w in re.findall(r"(?<![A-Za-z])[a-z][a-z'\-]+", all_en))

    groups = defaultdict(list)
    for k, en, zh in rows:
        for p in phrases(en):
            # 缩略（It's / I've）和无空格驼峰（OnSucceedAttack）不是专名
            if "'" in p or re.search(r"[a-z][A-Z]", p):
                continue
            base = p[:-1] if p.endswith("s") and p[:-1] in gloss_zh else p   # 复数归并到术语表单数
            if " " not in p and lower_cnt.get(p.lower(), 0) > 0 and base not in gloss_zh:
                continue
            groups[base].append(k)

    report = []
    for p, keys in sorted(groups.items(), key=lambda x: -len(x[1])):
        if len(keys) < args.min:
            continue
        local = Counter()
        for k in keys:
            local.update(doc_grams[k])
        scored = []
        for g, c in local.items():
            cov = c / len(keys)
            # 组内覆盖率 ≥8%，且全库文档频率 <3%（排除 我们/目标 这类通用词）
            if c < 2 or cov < 0.08 or df[g] / n_docs > 0.03:
                continue
            score = cov * math.log(n_docs / df[g])
            scored.append((score, c, g))
        scored.sort(reverse=True)
        # 去掉互为子串的候选（金色线束 / 色线束），保留分数高的
        picked = []
        for score, c, g in scored:
            if any(g in q or q in g for _, _, q in picked):
                continue
            picked.append((score, c, g))
            if len(picked) >= args.top:
                break
        if not picked:
            continue
        # 术语表已定名且 ≥90% 译文都含该译名 → 一致，跳过
        gz = gloss_zh.get(p)
        if gz:
            hit = sum(1 for k in keys if gz in progress[k]["zh"])
            if hit / len(keys) >= 0.9:
                continue
            report.append((p, len(keys), [(0, hit, f"术语表:{gz}")] + picked))
            continue
        # 首选译法覆盖 ≥90% 视为一致
        if picked[0][1] / len(keys) >= 0.9 or len(picked) < 2:
            continue
        report.append((p, len(keys), picked))

    lines = [f"# 一致性审计（短语 ≥{args.min} 次，{len(report)} 条疑似分裂）\n",
             "候选译法 = 该词所在译文里高频、全库低频的中文片段；后面是出现句数/总句数。",
             "只有一个候选的短语不列。人工判断哪些是真分裂。\n"]
    for p, n, picked in report:
        cands = "  ".join(f"`{g}`({c}/{n})" for _, c, g in picked)
        lines.append(f"- **{p}** ×{n}: {cands}")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:60]))
    if len(lines) > 60:
        print(f"…… 共 {len(report)} 条，全文见 {OUT}")


if __name__ == "__main__":
    main()
