#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""batch_next.py - 从 state.json 取下一批待译文本，写成 out/batch_pending.json。

翻译由 Claude Code 在会话里完成：读 batch_pending.json，逐条填 translation，
存成 out/batch_answers.json，再跑 batch_merge.py。

用法：
  python batch_next.py                        默认 60 条，状态 todo+stale
  python batch_next.py --size 120
  python batch_next.py --file P10705.json     只取某个文件（可重复）
  python batch_next.py --scope StoryData
  python batch_next.py --status todo,stale,outdated_official,same_as_en
"""

import argparse
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from limbus import walk
from limbus.fmtcode import fmt_list, has_cjk, quote_notes, soft_tokens
from limbus.glossary import Glossary
from limbus.ourterms import OurTerms
from limbus import lock
from limbus import tm as tmlib
from limbus.jsonio import load_json, save_json, setup_stdout

CONTEXT_SPAN = 3          # 前后各取几条相邻对话做上下文


def _line(item, zh_item, idx=None):
    """把一个条目（或它 texts[] 里的一行）渲染成 "说话人：正文"。优先官方中文。"""
    if not isinstance(item, dict):
        return None
    if idx is None:
        paths = (("content", "teller"), ("dlg", "teller"),
                 ("texts[0].text", "texts[0].speaker"))
    else:
        paths = ((f"texts[{idx}].text", f"texts[{idx}].speaker"),)
    for tp, sp in paths:
        text = walk.get_by_path(item, tp)
        if not (isinstance(text, str) and text.strip()):
            continue
        who = walk.get_by_path(item, sp) or ""
        # 同一路径官方译过就用中文，没译就退回英文
        if isinstance(zh_item, dict):
            zt = walk.get_by_path(zh_item, tp)
            if isinstance(zt, str) and has_cjk(zt):
                text = zt
                zw = walk.get_by_path(zh_item, sp)
                if isinstance(zw, str) and zw.strip():
                    who = zw
        text = text.replace("\n", " / ")
        return f"{who}：{text}" if isinstance(who, str) and who else text
    return None


def build_context(en_items, en_ids, zh_index, order, field, span=CONTEXT_SPAN):
    """取上下文邻句。

    RPG 的对话行在同一条目的 texts[] 数组里（field 形如 texts[3].text），
    邻句要在**数组内部**取；其余文件在相邻条目之间取。
    """
    m = re.fullmatch(r"texts\[(\d+)\]\.text", field or "")
    item = en_items[order] if order < len(en_items) else None
    zh_item = zh_index.get(en_ids[order]) if order < len(en_ids) else None

    if m and isinstance(item, dict) and isinstance(item.get("texts"), list):
        i = int(m.group(1))
        n = len(item["texts"])
        prev = [r for j in range(max(0, i - span), i)
                if (r := _line(item, zh_item, j))]
        nxt = [r for j in range(i + 1, min(n, i + 1 + span))
               if (r := _line(item, zh_item, j))]
        return prev, nxt

    prev, nxt = [], []
    for i in range(max(0, order - span), order):
        r = _line(en_items[i], zh_index.get(en_ids[i]))
        if r:
            prev.append(r)
    for i in range(order + 1, min(len(en_items), order + 1 + span)):
        r = _line(en_items[i], zh_index.get(en_ids[i]))
        if r:
            nxt.append(r)
    return prev, nxt


def main():
    setup_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=60)
    ap.add_argument("--file", action="append",
                    help="点名要包的文件（可重复）。不给就自动挑一个没人包的文件")
    ap.add_argument("--scope", action="append", help="限定 scope，如 StoryData / _root")
    ap.add_argument("--status", default="todo,stale",
                    help="要取的状态，逗号分隔")
    ap.add_argument("--no-claim", action="store_true",
                    help="不走认领表（确认只有你一个 agent 在干活时用）")
    ap.add_argument("--files", type=int, default=1,
                    help="自动挑几个文件包下来（默认 1，整份翻完再换下一个）")
    ap.add_argument("--abandon", action="store_true",
                    help="放弃本 slot 已认领但没合批的条目，放回池子给别人")
    args = ap.parse_args()

    if args.abandon:
        lock.release_all()
        print(f"[并行] 已释放 slot {config.SLOT} 的全部认领")
        return

    state = load_json(config.STATE)
    if not state:
        print("[错误] 没有 out/state.json，先跑 python scan.py")
        sys.exit(1)

    wanted_status = {s.strip() for s in args.status.split(",") if s.strip()}
    items = [x for x in state["actionable"] if x["status"] in wanted_status]

    # state.json 是上次 scan 的快照，progress.json 才是实时真相：
    # 合批后没重新 scan 就取批，会把已经翻好的条目再发一遍（白翻 + 浪费 token）。
    prog = load_json(config.PROGRESS) or {}
    if prog:
        n0 = len(items)
        items = [x for x in items
                 if not (isinstance(prog.get(x["key"]), dict)
                         and prog[x["key"]].get("src_hash") == walk.src_hash(x["original"]))]
        if len(items) != n0:
            print(f"[过滤] state.json 已过期：{n0 - len(items)} 条其实已合批，跳过"
                  f"（想让统计准确就跑 python scan.py 刷新）")
    total_remaining = len(items)


    if args.scope:
        want = set(args.scope)
        items = [x for x in items if x["scope"] in want]

    # ---- 按文件分工 ----
    # 整个文件包给一个 agent：同一段对话必须由同一个人从头翻到尾，
    # 否则称谓、语气、代词指代对不上。认领表只是保险，防止两边点到同一个文件。
    def label(x):
        return f'{x["scope"]}/{x["file"]}'

    if args.no_claim:
        taken, held = set(), set()
    else:
        taken, held = lock.claimed_by_others(), lock.mine()

    if args.file:
        want = set(args.file)
        picked = {label(x) for x in items
                  if x["file"] in want or label(x) in want}
        blocked = picked & taken
        if blocked:
            print(f"[并行] 这些文件已被别的 agent 包走，跳过：{sorted(blocked)}")
        picked -= blocked
    else:
        # 优先接着翻自己手上没翻完的文件，再挑待译最多的无主文件
        remaining = Counter(label(x) for x in items)
        picked = {f for f in held if remaining.get(f)}
        if not picked:
            free = [(n, f) for f, n in remaining.items() if f not in taken]
            free.sort(key=lambda t: (-t[0], t[1]))
            picked = {f for _, f in free[: max(1, args.files)]}

    if not picked:
        print("没有可包的文件（要么翻完了，要么都被别的 agent 包着）。")
        save_json(config.PENDING, [])
        return

    if not args.no_claim:
        got = lock.claim(picked)
        if got != picked:
            print(f"[并行] 抢锁时被人先占了：{sorted(picked - got)}")
        picked = got
        if not picked:
            save_json(config.PENDING, [])
            return

    items = [x for x in items if label(x) in picked]
    file_remaining = Counter(label(x) for x in items)

    # 按 文件 → 条目顺序 → 数组下标 → 字段 排序，让同一段对话按原顺序落在同一批里。
    # 下标必须按数字比，按 key 字符串排会排成 texts[1]、texts[10]、texts[2]。
    field_order = {"title": 0, "place": 1, "teller": 2, "desc": 3,
                   "name": 4, "nickName": 5, "content": 6, "dlg": 7}

    def sort_key(scope, filename, order, field):
        idx = tuple(int(n) for n in re.findall(r"\[(\d+)\]", field))
        leaf = field.split(".")[-1].split("[")[0]
        return (scope, filename, order, idx, field_order.get(leaf, 9), field)

    items.sort(key=lambda x: sort_key(x["scope"], x["file"], x["order"], x["field"]))
    batch = items[: args.size]

    if not batch:
        print("没有符合条件的待译条目。")
        save_json(config.PENDING, [])
        return

    gloss = Glossary()
    ours = OurTerms()
    if ours.inflight:
        print(f"[并行] 已读入其他 agent 未合批的 {ours.inflight} 条译文，供 ours 字段对齐")
    tm = tmlib.load()
    tm_amb = tmlib.ambiguous_set()

    # 按文件分组，每个文件只读一次 EN/ZH
    by_file = defaultdict(list)
    for x in batch:
        by_file[(x["scope"], x["file"])].append(x)

    targets = {(t.scope, t.filename): t for t in walk.iter_targets()}

    out = []
    for (scope, filename), group in by_file.items():
        t = targets.get((scope, filename))
        if t is None:
            continue
        en_data = load_json(t.en_path, on_error="warn")
        en_items = walk.data_list(en_data)
        en_ids = walk.item_ids(en_data)
        zh_index = walk.index_by_id(load_json(t.zh_path)) if os.path.exists(t.zh_path) else {}
        for x in group:
            prev, nxt = build_context(en_items, en_ids, zh_index, x["order"], x["field"])
            item = en_items[x["order"]] if x["order"] < len(en_items) else {}
            entry = {
                "key":      x["key"],
                "file":     f"{scope}/{filename}",
                "id":       x["id"],
                "field":    x["field"],
                "hint":     config.FIELD_HINT.get(
                                x["field"].split(".")[-1].split("[")[0], ""),
                "status":   x["status"],
                "speaker":  (walk.get_by_path(item, x["field"].rsplit(".", 1)[0] + ".speaker")
                             if "." in x["field"] else None)
                            or item.get("teller") or item.get("model") or "",
                "prev":     prev,
                "next":     nxt,
                "glossary": gloss.hits(x["original"]),
                "original": x["original"],
                "translation": "",
            }
            kw = config.keyword_brackets(scope, x["field"])
            prior = ours.lookup(x["original"], exclude_key=x["key"])
            if prior:
                entry["ours"] = prior
                entry["ours_note"] = "同一专名我们在别处译过，例句见上；除非明显错译，沿用同一译法"
            pend = ours.pending_hits(x["original"])
            if pend:
                entry["pending_terms"] = pend
                entry["pending_note"] = "待定术语：译名未拍板，先沿用现译写法，保持一致"
            sess = ours.session_hits(x["original"])
            if sess:
                entry["agreed_terms"] = sess
                entry["agreed_note"] = ("另一个 agent 本轮已经把这些词定死了"
                                        "（glossary/session_terms.json），必须照用")
            official = tm.get(x["original"])
            if official:
                entry["official_zh"] = official
                entry["official_note"] = (
                    "官方在别处译过这句原文。**多种译法并存，请判断本处该用哪个**"
                    if x["original"] in tm_amb else
                    "官方在别处译过这句原文，照抄即可（保持一致）"
                )
            fmt = fmt_list(x["original"], kw)
            if fmt:
                entry["keep_verbatim"] = fmt
            notes = quote_notes(x["original"], kw)
            if notes:
                entry["quote_brackets"] = notes
            soft = sorted(soft_tokens(x["original"]))
            if soft:
                entry["layout_tags"] = soft
            if x["status"] in ("stale", "outdated_official") and x.get("zh"):
                entry["previous_zh"] = x["zh"]
            out.append(entry)

    order_of = {x["key"]: sort_key(x["scope"], x["file"], x["order"], x["field"])
                for x in batch}
    out.sort(key=lambda e: order_of[e["key"]])
    save_json(config.PENDING, out, indent=1)
    if not args.no_claim:
        lock.touch(picked)       # 续租，别让长批次翻到一半被别人抢走

    print(f"slot            : {config.SLOT}")
    print(f"本 agent 包的文件 : {', '.join(sorted(picked))}")
    for f in sorted(picked):
        done = file_remaining.get(f, 0) - sum(1 for e in out if e["file"] == f)
        print(f"    {f}：本批后还剩 {done} 条")
    print(f"待译总数（{args.status}）: {total_remaining}")
    print(f"本批            : {len(out)} 条 -> {config.PENDING}")
    comp = defaultdict(int)
    for e in out:
        comp[e["file"]] += 1
    print("本批构成：")
    for k, v in sorted(comp.items(), key=lambda x: -x[1]):
        print(f"    {v:>4}  {k}")
    print()
    print(f"下一步：读 {config.PENDING}，填好 translation，")
    print(f"        存成 {config.ANSWERS}，然后 python batch_merge.py")


if __name__ == "__main__":
    main()
