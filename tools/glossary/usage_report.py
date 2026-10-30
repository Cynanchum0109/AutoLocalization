#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""usage_report.py - 一词多义术语的官方用法分布（只读）

对每个词，把官方 EN/ZH 对照里的出现分三种看：
  短条    整条文本 ≤4 个词且含该词（说话人名、技能名、状态名、标题）→ 官方整条译文的分布
  句中大写 长文本里句中大写出现（多半是专名用法）→ 术语译名命中数 + 未命中样例
  小写     长文本里小写出现（多半是普通词）→ 同上
用来决定术语值要不要加「仅…时；其他按语境」的说明（参考 !Rain、!Mentor）。

用法：
  python tools/glossary/usage_report.py Boss Sister Clan
  python tools/glossary/usage_report.py --tsv glossary/common_words_review.tsv   # 取表里「英文」列
输出 glossary/usage_report.md
"""

import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from case_audit import SENT_START_RE, WORD_RE, iter_pairs, zh_core
from limbus.jsonio import load_json

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "glossary")  # 术语数据目录
OUT = os.path.join(HERE, "usage_report.md")
N_SAMPLES = 3


def one_line(s, n):
    s = re.sub(r"<[^>]+>", "", s).replace("\n", " ")
    return s[:n] + ("…" if len(s) > n else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words", nargs="*")
    ap.add_argument("--tsv")
    args = ap.parse_args()

    words = list(args.words)
    if args.tsv:
        with open(args.tsv, encoding="utf-8-sig") as f:
            words += [r["英文"].strip() for r in csv.DictReader(f, delimiter="\t") if r.get("英文")]
    gloss = load_json(os.path.join(HERE, "glossary.json"))
    by_bare = {k.lstrip("!").lower(): (k, v) for k, v in gloss.items()}
    targets = {}
    for w in words:
        k, v = by_bare.get(w.lower(), (w, ""))
        targets[w.lower()] = (k, zh_core(v), v)

    short = defaultdict(Counter)
    short_en = defaultdict(dict)
    sent = defaultdict(lambda: defaultdict(Counter))      # wl -> kind -> {hit, n}
    miss = defaultdict(lambda: defaultdict(list))
    for en, zh in iter_pairs():
        toks = WORD_RE.findall(en)
        present = {t.lower() for t in toks} & targets.keys()
        if not present:
            continue
        for wl in present:
            term_zh = targets[wl][1]
            if len(toks) <= 4:
                z = one_line(zh, 30)
                short[wl][z] += 1
                short_en[wl].setdefault(z, one_line(en, 40))
                continue
            kinds = set()
            for m in WORD_RE.finditer(en):
                if m.group(0).lower() != wl:
                    continue
                if m.group(0)[0].islower():
                    kinds.add("小写")
                elif not SENT_START_RE.search(en[:m.start()]):
                    kinds.add("句中大写")
            for kind in kinds:
                hit = bool(term_zh) and term_zh in zh
                sent[wl][kind]["n"] += 1
                sent[wl][kind]["hit"] += hit
                if not hit and len(miss[wl][kind]) < N_SAMPLES:
                    # 只截取词附近的英文，中文整句前段
                    i = re.search(r"\b%s\b" % re.escape(wl), en, re.I).start()
                    miss[wl][kind].append((one_line(en[max(0, i - 50):i + 60], 110), one_line(zh, 60)))

    lines = ["# 一词多义术语：官方用法分布", "",
             "短条 = 整条 ≤4 词（说话人名/技能名/状态名/标题），列官方整条译文。",
             "句中大写/小写 = 长文本，看官方是否用了术语译名，附未命中样例。", ""]
    for wl, (key, core, full) in targets.items():
        lines.append(f"## {key}　→　{full or '（不在术语表）'}")
        if short[wl]:
            top = short[wl].most_common(8)
            lines.append("- 短条：" + "；".join(f"{z}×{n}（{short_en[wl][z]}）" for z, n in top))
        for kind in ("句中大写", "小写"):
            s = sent[wl][kind]
            if not s["n"]:
                continue
            lines.append(f"- {kind}：命中 {s['hit']}/{s['n']}")
            for e, z in miss[wl][kind]:
                lines.append(f"  - ✗ {e}　｜　{z}")
        lines.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{len(targets)} 个词 → {OUT}")


if __name__ == "__main__":
    main()
