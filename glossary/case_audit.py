#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case_audit.py - 常见词术语的大小写审计（只读，不改 glossary.json）

问题：术语表默认不分大小写匹配，Wing（组织「翼」）会把小写 wing（翅膀）也提示成「翼」。
办法：用官方译文当裁判。对每个单词术语，在 EN/ZH 对照的每条文本里看：
  - 只出现「句中大写」形式的文本，官方中文里有没有术语译名 → 大写命中率
  - 只出现「小写」形式的文本，官方中文里有没有术语译名     → 小写命中率
（句首大写不算专名证据，单独计数；同一条里大小写都有的不计，免得混淆。）

按命中率给建议：
  敏感  大写命中高、小写命中低 → 加 !，只认大写
  留    大小写都命中高         → 不分大小写也没问题
  删    大小写都命中低         → 官方不按这个译名走，留着只会误导
  改译名 大写多但命中低        → 可能是专名但译名和官方不一致，看「官方样例」
  人工  其余 / 样本太少

输出 glossary/case_audit.tsv（UTF-8 BOM，Excel 可开）。用法：
  python glossary/case_audit.py               # 审单词术语，小写出现 ≥10 次的
  python glossary/case_audit.py --min 5
"""

import argparse
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from limbus.jsonio import load_json

HERE = os.path.dirname(os.path.abspath(__file__))
GLOSSARY = os.path.join(HERE, "glossary.json")
OUT = os.path.join(HERE, "case_audit.tsv")
EN_ROOT = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en"
ZH_ROOT = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN"

WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-]*")
SENT_START_RE = re.compile(r"(^|[.!?…:\"“'‘\n\[(]\s*)$")


def zh_core(zh):
    """术语值里的注释（全角括号起）去掉，只拿译名本体比对。"""
    return re.split(r"[（(]", zh, 1)[0].strip()


def iter_pairs():
    """遍历 EN/ZH 对照的字符串对。"""
    def walk(e, z):
        if isinstance(e, str) and isinstance(z, str):
            yield e, z
        elif isinstance(e, dict) and isinstance(z, dict):
            for k in e:
                if k in z:
                    yield from walk(e[k], z[k])
        elif isinstance(e, list) and isinstance(z, list):
            if all(isinstance(x, dict) and "id" in x for x in e):
                zm = {}
                for y in z:
                    if isinstance(y, dict):
                        zm.setdefault(str(y.get("id")), y)
                for x in e:
                    y = zm.get(str(x["id"]))
                    if y is not None:
                        yield from walk(x, y)
            elif len(e) == len(z):
                for x, y in zip(e, z):
                    yield from walk(x, y)

    for root, _, files in os.walk(EN_ROOT):
        for fn in files:
            if not (fn.startswith("EN_") and fn.endswith(".json")):
                continue
            rel = os.path.relpath(root, EN_ROOT)
            zp = os.path.join(ZH_ROOT, "" if rel == "." else rel, fn[3:])
            if not os.path.exists(zp):
                continue
            e, z = load_json(os.path.join(root, fn)), load_json(zp)
            if e is not None and z is not None:
                yield from walk(e, z)


def classify_occurrences(text, word_lc):
    """返回该文本里此词出现的形式集合：cap（句中大写）/ start（句首大写）/ lower。"""
    kinds = set()
    for m in WORD_RE.finditer(text):
        w = m.group(0)
        if w.lower() != word_lc:
            continue
        if w[0].islower():
            kinds.add("lower")
        elif SENT_START_RE.search(text[:m.start()]):
            kinds.add("start")
        else:
            kinds.add("cap")
    return kinds


def suggest(cap_n, cap_hit, low_n, low_hit):
    cr = cap_hit / cap_n if cap_n else None
    lr = low_hit / low_n if low_n else None
    if cap_n < 3 and low_n < 3:
        return "人工", "样本太少"
    if cr is not None and cap_n >= 3 and cr >= 0.6:
        if lr is None or low_n < 3 or lr < 0.4:
            return "敏感", "大写多按此译，小写不是"
        if lr >= 0.6:
            return "留", "大小写都按此译"
    if (cr is None or cap_n < 3 or cr < 0.3) and (lr is None or low_n < 3 or lr < 0.3):
        if cap_n >= 10:
            return "改译名", "大写常见但官方不用此译名"
        return "删", "官方基本不用此译名"
    return "人工", "命中率居中"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=10, help="小写出现次数下限")
    args = ap.parse_args()

    gloss = load_json(GLOSSARY)
    # 单词术语（含已加 ! 的，一并复核）
    terms = {}
    for k, v in gloss.items():
        bare = k.lstrip("!")
        if re.fullmatch(r"[A-Za-z][A-Za-z\-]*", bare):
            terms[bare.lower()] = (k, zh_core(v))

    stats = defaultdict(Counter)          # word_lc -> {cap_n, cap_hit, low_n, low_hit, start_n}
    samples = defaultdict(dict)           # word_lc -> {"cap": (en, zh), "lower": (en, zh)}
    for en, zh in iter_pairs():
        words = {w.lower() for w in WORD_RE.findall(en)} & terms.keys()
        for wl in words:
            kinds = classify_occurrences(en, wl)
            if not kinds:
                continue
            hit = terms[wl][1] in zh
            s = stats[wl]
            if kinds == {"start"}:
                s["start_n"] += 1
                continue
            kinds.discard("start")
            if len(kinds) != 1:
                continue
            kind = kinds.pop()
            s[kind + "_n"] += 1
            s[kind + "_hit"] += hit
            if not hit and kind not in samples[wl]:
                samples[wl][kind] = (en.replace("\n", " ")[:80], zh.replace("\n", " ")[:40])

    rows = []
    for wl, (key, zh) in terms.items():
        s = stats[wl]
        if s["lower_n"] < args.min:
            continue
        sug, why = suggest(s["cap_n"], s["cap_hit"], s["lower_n"], s["lower_hit"])
        if key.startswith("!") and sug == "敏感":
            sug, why = "已敏感", "现状正确"
        pct = lambda h, n: f"{h}/{n}" if n else "-"
        smp = samples[wl].get("cap") or samples[wl].get("lower") or ("", "")
        rows.append((sug, key, zh, pct(s["cap_hit"], s["cap_n"]), pct(s["lower_hit"], s["lower_n"]),
                     s["start_n"], why, smp[0], smp[1]))

    order = {"改译名": 0, "删": 1, "敏感": 2, "人工": 3, "留": 4, "已敏感": 5}
    rows.sort(key=lambda r: (order[r[0]], r[1].lstrip("!").lower()))
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        f.write("建议\t术语键\t译名\t句中大写命中\t小写命中\t句首次数\t理由\t未命中样例EN\t样例官方ZH\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print(f"{len(rows)} 条 → {OUT}")
    print("  " + "，".join(f"{k} {v}" for k, v in Counter(r[0] for r in rows).most_common()))


if __name__ == "__main__":
    main()
