#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""term.py - 术语查找（按章节 / 类型 / 出处 / 中英互查）。

  python term.py Faust                 中英互查（子串，不分大小写）：译名、所属章、类型、出现在哪
  python term.py 浮士德
  python term.py --chap                各章条数（带章名）
  python term.py --chap 10             第10章的术语，按类型分组（也可写 8.5 / 间章8.5 / 通用 / 人格剧情）
  python term.py --cat                 各类型条数
  python term.py --cat 组织            某类型全部术语，按章节分组（类型名写一部分即可）
  python term.py --chap 10 --cat 人物  条件可以叠加
  python term.py --where 第10章        在某出处出现过的（不只看所属章），按次数排
  python term.py --set Kaki 组织势力   手动改类型（记为 人工，重跑分类不覆盖）
  python term.py --set-chap Kaki 10    手动改所属章
  python term.py --check               术语表 / 分类表 / 出处索引是否对得上

所属章 = 该词在主线/间章里出现最多的那章；铺满多章的归「通用」。
数据由 glossary/categorize.py 生成；术语表或游戏文本更新后重跑它。
也会查 glossary/session_terms.json（本轮新定）和 pending_terms.json（待定）。
"""

import argparse
import collections
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "glossary"))

import config
from categorize import (CATEGORIES, CATS, CHAP_OTHER, GENERAL, MANUAL, UNSORTED, WHERE,
                        chap_sort_key, glossary_digest)
from limbus.jsonio import load_json, save_json, setup_stdout

SESSION = os.path.join(BASE, "glossary", "session_terms.json")
PENDING = os.path.join(BASE, "glossary", "pending_terms.json")


class DB:
    def __init__(self):
        self.gloss = load_json(config.GLOSSARY) or {}
        self.cats = {k: v for k, v in (load_json(CATEGORIES) or {}).items() if not k.startswith("_")}
        self.where_all = load_json(WHERE) or {}
        self.where = self.where_all.get("terms", {})
        self.titles = self.where_all.get("_chapters", {})

    def cat(self, k):
        return self.cats.get(k, {}).get("cat", UNSORTED)

    def chap(self, k):
        return self.cats.get(k, {}).get("chap", "未出现")

    def chap_title(self, chap):
        t = self.titles.get(chap)
        return f"{chap}「{t}」" if t else chap


def resolve_cat(name):
    if name in CATS:
        return name
    hits = [c for c in CATS if name in c]
    if len(hits) == 1:
        return hits[0]
    sys.exit(f"类型「{name}」{'不明确：' + ' / '.join(hits) if hits else '不存在'}。可用：{' / '.join(CATS)}")


def resolve_chap(name):
    """10 / 第10章 / 8.5 / 间章8.5 / 通用 / 人格剧情 …"""
    if name in [GENERAL] + CHAP_OTHER:
        return name
    m = re.fullmatch(r"(?:第|间章)?(\d+)(\.5)?章?", name)
    if not m:
        sys.exit(f"看不懂章节「{name}」。写 10 / 8.5 / {GENERAL} / {' / '.join(CHAP_OTHER)}")
    return f"间章{m.group(1)}.5" if m.group(2) else f"第{int(m.group(1))}章"


def fmt_where(w, top=6):
    if not w:
        return "（当前英文文本里没出现）"
    items = list(w.items())
    s = "，".join(f"{k}×{n}" for k, n in items[:top])
    return s + (f" …等 {len(items)} 处" if len(items) > top else "")


def cmd_lookup(db, q):
    ql = q.lower()
    rows = []
    for k, zh in db.gloss.items():
        en = k.lstrip("!")
        if ql in en.lower() or q in zh:
            rows.append((not (en.lower() == ql or zh == q), len(en), k, zh))
    rows.sort()
    for _, _, k, zh in rows[:30]:
        c = db.cats.get(k, {})
        print(f"{k.lstrip('!')} = {zh}" + (" [区分大小写]" if k.startswith("!") else ""))
        if not c:
            print("    （未建分类，跑 glossary/categorize.py）")
        else:
            print(f"    所属：{db.chap_title(c['chap'])}" + ("（人工）" if c.get("chap_by") == MANUAL else "")
                  + f"    类型：{c['cat']}" + (f"  ← {c['by']}" if c.get("by") else ""))
        print(f"    出处：{fmt_where(db.where.get(k))}")
    if len(rows) > 30:
        print(f"… 共 {len(rows)} 条，只显示最接近的 30 条")

    found = bool(rows)
    for k, v in (load_json(SESSION) or {}).items():
        if not k.startswith("_") and isinstance(v, dict) and (ql in k.lower() or q in v.get("zh", "")):
            found = True
            print(f"{k} = {v.get('zh')}  [本轮新定，by {v.get('by')}]  {v.get('note', '')}")
    for k, v in (load_json(PENDING) or {}).get("unresolved", {}).items():
        if ql in k.lower() or q in v:
            found = True
            print(f"{k}  [待定] {v}")
    if not found:
        print(f"没找到「{q}」。")


def cmd_counts(db, by):
    cnt = collections.Counter((db.chap if by == "chap" else db.cat)(k) for k in db.gloss)
    keys = sorted(cnt, key=chap_sort_key) if by == "chap" else [c for c in CATS if c in cnt]
    for k in keys:
        print(f"  {cnt[k]:>5}  {db.chap_title(k) if by == 'chap' else k}")
    print(f"  {sum(cnt.values()):>5}  合计")


def cmd_list(db, cat=None, chap=None, place=None):
    rows = []
    for k, zh in db.gloss.items():
        if cat and db.cat(k) != cat or chap and db.chap(k) != chap:
            continue
        n = sum(v for lab, v in db.where.get(k, {}).items() if place in lab) if place else 0
        if place and not n:
            continue
        rows.append((k, zh, n))

    if place:   # 按次数排，所属章和类型写在行尾
        for k, zh, n in sorted(rows, key=lambda r: -r[2]):
            print(f"  {k.lstrip('!')} = {zh}  ×{n}  〔{db.chap(k)} · {db.cat(k)}〕")
    else:
        # 选了章 → 章内按类型分组；否则按章分组
        group = (lambda k: db.cat(k)) if chap else (lambda k: db.chap(k))
        order = (lambda g: CATS.index(g) if g in CATS else 99) if chap else chap_sort_key
        groups = collections.defaultdict(list)
        for k, zh, _ in rows:
            groups[group(k)].append((k, zh))
        for g in sorted(groups, key=order):
            if not (chap and cat):
                print(f"\n## {g if chap else db.chap_title(g)}（{len(groups[g])}）")
            for k, zh in groups[g]:
                print(f"  {k.lstrip('!')} = {zh}")
    what = " + ".join(x for x in (db.chap_title(chap) if chap else None, cat,
                                  f"出处含「{place}」" if place else None) if x)
    print(f"\n{what}：{len(rows)} 条")


def find_key(db, term):
    for k in (term, "!" + term):
        if k in db.gloss:
            return k
    k = next((k for k in db.gloss if k.lstrip("!").lower() == term.lower()), None)
    if k is None:
        sys.exit(f"术语表里没有「{term}」。")
    return k


def cmd_set(db, term, value, field):
    key = find_key(db, term)
    raw = load_json(CATEGORIES) or {}
    entry = raw.setdefault(key, {"chap": "未出现", "cat": UNSORTED, "by": ""})
    if field == "cat":
        old, entry["cat"], entry["by"] = entry.get("cat"), resolve_cat(value), MANUAL
    else:
        old, entry["chap"], entry["chap_by"] = entry.get("chap"), resolve_chap(value), MANUAL
    save_json(CATEGORIES, raw)
    print(f"{key.lstrip('!')}：{old} → {entry[field]}（人工）")


def cmd_check(db):
    ok = True
    miss = [k for k in db.gloss if k not in db.cats]
    extra = [k for k in db.cats if k not in db.gloss]
    if miss:
        ok = False
        print(f"术语表里有、分类表里没有 {len(miss)} 条（跑 glossary/categorize.py）：{', '.join(miss[:15])}")
    if extra:
        ok = False
        print(f"分类表里有、术语表已删 {len(extra)} 条（跑 glossary/categorize.py 清掉）：{', '.join(extra[:15])}")
    if db.where_all.get("_glossary") != glossary_digest():
        ok = False
        print(f"出处索引建于 {db.where_all.get('_built', '?')}，之后术语表改过 → 跑 glossary/categorize.py")
    uns = sum(1 for k in db.gloss if db.cat(k) == UNSORTED)
    unseen = [k.lstrip("!") for k in db.gloss if k not in db.where]
    print(f"类型未分类 {uns} 条（python term.py --cat 未分类 查看，--set 手动归类）")
    print(f"当前英文文本里没出现的术语 {len(unseen)} 条：{', '.join(unseen[:20])}")
    if ok:
        print("术语表、分类表、出处索引一致。")


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description="术语查找", formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("query", nargs="?", help="英文或中文，子串匹配")
    ap.add_argument("--chap", nargs="?", const="", help="按所属章列出；不带值则显示各章条数")
    ap.add_argument("--cat", nargs="?", const="", help="按类型列出；不带值则显示各类型条数")
    ap.add_argument("--where", help="按出处筛选（任何出现都算），如 第10章 / 间章8.5 / 人格剧情 / 语音")
    ap.add_argument("--set", nargs=2, metavar=("术语", "类型"), help="手动改类型")
    ap.add_argument("--set-chap", nargs=2, metavar=("术语", "章"), help="手动改所属章")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    db = DB()
    if a.set:
        cmd_set(db, *a.set, "cat")
    elif a.set_chap:
        cmd_set(db, *a.set_chap, "chap")
    elif a.check:
        cmd_check(db)
    elif a.chap == "" and a.cat is None and not a.where:
        cmd_counts(db, "chap")
    elif a.cat == "" and a.chap is None and not a.where:
        cmd_counts(db, "cat")
    elif a.chap or a.cat or a.where:
        cmd_list(db, resolve_cat(a.cat) if a.cat else None, resolve_chap(a.chap) if a.chap else None, a.where)
    elif a.query:
        cmd_lookup(db, a.query)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
