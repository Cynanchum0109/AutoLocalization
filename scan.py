#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan.py - 扫描 tier0 范围，算出每条文本的状态，并与上次快照对比。

产出：
  out/state.json         待办清单（只含需要处理的条目）
  out/snapshot_new.json  本次 EN 原文指纹
  out/changes/<时间>.md  与 out/snapshot.json 的差异报告

状态：
  todo              ZH 侧根本没有（缺文件 / 缺条目 / 缺字段）
  stale             我们译过，但之后官方改了英文原文 → 需重翻
  outdated_official 官方有中文，但英文原文在上次快照后被改过 → 中文可能已过期
  same_as_en        ZH 与 EN 一模一样（可能是漏翻，也可能本就该保留英文如 LCCB）
  zh_placeholder    ZH 有值且与 EN 不同，但里面根本没有中文 —— 多半是韩文占位
                    （'동부섕크 인격스더미'），也可能本就该保留原样（'LCD?'→'LCD？'）
  ignored           基线（当前 ZH 版本）里就没翻的条目 —— 按约定永久不翻
  ours              我们已译且原文未变
  official          官方已译且原文未变

用法：
  python scan.py                 只扫描并报告，不动基线
  python scan.py --accept        把本次 EN 指纹存为新基线（每次看完变更后用）
  python scan.py --baseline      一次性：把当前 ZH 状态定为基线 —— 现在没翻的
                                 （todo / same_as_en）全部记入 ignore.json，以后不再出现
  python scan.py --show-ignored  报告里附上被忽略的条目统计
"""

import argparse
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from limbus import walk
from limbus.fmtcode import has_cjk
from limbus.jsonio import load_json, save_json, setup_stdout

ACTIONABLE = ("todo", "stale", "outdated_official", "same_as_en", "zh_placeholder")
BASELINE_FREEZE = ("todo", "same_as_en", "zh_placeholder")


def classify(unit, zh_val, prog_entry, snap_hash):
    en_h = walk.src_hash(unit["original"])
    if prog_entry and prog_entry.get("src_hash") == en_h:
        return "ours", en_h
    if prog_entry:
        return "stale", en_h
    if zh_val is None or not isinstance(zh_val, str) or zh_val == "":
        return "todo", en_h
    if zh_val == unit["original"]:
        return "same_as_en", en_h
    if not has_cjk(zh_val):
        # ZH 侧有值但没有一个汉字：官方的韩文占位，或本就不该翻的短串
        return "zh_placeholder", en_h
    if snap_hash is not None and snap_hash != en_h:
        return "outdated_official", en_h
    return "official", en_h


def main():
    setup_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--accept", action="store_true",
                    help="把本次 EN 指纹存为新基线")
    ap.add_argument("--baseline", action="store_true",
                    help="一次性：当前 ZH 里没翻的条目全部记入 ignore.json，永久跳过")
    ap.add_argument("--freeze-old", action="store_true",
                    help="把「基线时就已存在」的待办条目记入 ignore.json，"
                         "基线之后新出现的保持待办（新增检测规则时用）")
    ap.add_argument("--show-ignored", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="还有 outdated_official 没处理时也强行 --accept")
    args = ap.parse_args()

    progress = load_json(config.PROGRESS) or {}
    snapshot = load_json(config.SNAPSHOT) or {}
    ignore   = load_json(config.IGNORE) or {}
    first_run = not snapshot

    hashes    = {}
    actionable = []
    counts    = Counter()
    per_file  = defaultdict(Counter)
    missing_zh_files = []

    targets = list(walk.iter_targets())
    print(f"扫描 {len(targets)} 个文件（tier0: "
          f"{', '.join(s for s, _ in config.TIER0_DIRS)} + 根目录点名文件）...")

    for t in targets:
        en_data = load_json(t.en_path, on_error="warn")
        if en_data is None:
            continue
        zh_data = load_json(t.zh_path) if os.path.exists(t.zh_path) else None
        if zh_data is None and os.path.exists(t.zh_path) is False:
            missing_zh_files.append(t.label)
        zh_index = walk.index_by_id(zh_data) if zh_data else {}

        for unit in walk.iter_units(t, en_data):
            key = unit["key"]
            zh_item = zh_index.get(unit["id"])
            # field 是路径串（levelList[0].coinlist[2].coindescs[4].desc / texts[3].text），
            # 必须按路径取，用 dict.get 会一律读成 None → 把官方已译的条目误判成 todo。
            zh_val  = (walk.get_by_path(zh_item, unit["field"])
                       if isinstance(zh_item, dict) else None)
            status, en_h = classify(unit, zh_val, progress.get(key), snapshot.get(key))
            # 基线里就没翻的条目，只要英文原文没变过，就永久跳过
            if status in BASELINE_FREEZE and ignore.get(key) == en_h:
                status = "ignored"
            hashes[key] = en_h
            counts[status] += 1
            per_file[t.label][status] += 1
            if status in ACTIONABLE:
                actionable.append({
                    "key":      key,
                    "status":   status,
                    "scope":    unit["scope"],
                    "file":     unit["filename"],
                    "id":       unit["id"],
                    "field":    unit["field"],
                    "order":    unit["order"],
                    "original": unit["original"],
                    "zh":       zh_val,
                })

    # ---------- 与上次快照对比 ----------
    added    = sorted(set(hashes) - set(snapshot))
    removed  = sorted(set(snapshot) - set(hashes))
    modified = sorted(k for k in hashes if k in snapshot and snapshot[k] != hashes[k])

    save_json(config.STATE, {
        "generated":  datetime.now().isoformat(timespec="seconds"),
        "counts":     dict(counts),
        "actionable": actionable,
    })
    save_json(os.path.join(config.OUT_DIR, "snapshot_new.json"), hashes, indent=None)

    # ---------- 变更报告 ----------
    os.makedirs(config.CHANGES_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report = os.path.join(config.CHANGES_DIR, f"{stamp}.md")
    lines = [f"# 游戏文本变更报告 {stamp}", ""]
    if first_run:
        lines += ["> 首次扫描，没有可比对的基线。跑 `python scan.py --accept` 建立基线。", ""]
    lines += [
        "## 与上次基线的差异", "",
        f"- 新增文本条目：**{len(added)}**",
        f"- 删除文本条目：**{len(removed)}**",
        f"- 原文被改写：**{len(modified)}**",
        "",
    ]
    for title, keys in (("新增", added), ("原文被改写", modified), ("删除", removed)):
        if not keys:
            continue
        by_file = defaultdict(list)
        for k in keys:
            by_file[k.rsplit("#", 2)[0]].append(k)
        lines += [f"### {title}（{len(keys)} 条，{len(by_file)} 个文件）", ""]
        for f in sorted(by_file)[:200]:
            lines.append(f"- `{f}` — {len(by_file[f])} 条")
        if len(by_file) > 200:
            lines.append(f"- …… 另有 {len(by_file) - 200} 个文件")
        lines.append("")

    lines += ["## 当前状态统计", "", "| 状态 | 条数 |", "|---|---|"]
    for s in ("todo", "stale", "outdated_official", "same_as_en",
              "zh_placeholder", "ours", "official", "ignored"):
        lines.append(f"| {s} | {counts.get(s, 0)} |")
    lines.append("")

    todo_files = sorted(
        ((f, c) for f, c in per_file.items()
         if c["todo"] or c["stale"] or c["outdated_official"]),
        key=lambda x: -(x[1]["todo"] + x[1]["stale"] + x[1]["outdated_official"]),
    )
    if todo_files:
        lines += ["## 需要动手的文件", "", "| 文件 | todo | stale | 官方过期 |", "|---|---|---|---|"]
        for f, c in todo_files[:100]:
            lines.append(f"| `{f}` | {c['todo']} | {c['stale']} | {c['outdated_official']} |")
        lines.append("")
    if missing_zh_files:
        lines += [f"## ZH 侧缺失的整个文件（{len(missing_zh_files)}）", ""]
        lines += [f"- `{f}`" for f in missing_zh_files[:100]]
        lines.append("")

    with open(report, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))

    # ---------- 控制台摘要 ----------
    print()
    for s in ("todo", "stale", "outdated_official", "same_as_en",
              "zh_placeholder", "ours", "official", "ignored"):
        print(f"  {s:20} {counts.get(s, 0):8}")
    print()
    print(f"  与基线对比：新增 {len(added)} / 改写 {len(modified)} / 删除 {len(removed)}")
    print(f"  待办清单 → {config.STATE}（{len(actionable)} 条）")
    print(f"  变更报告 → {report}")

    if args.freeze_old:
        frozen = dict(ignore)
        n = 0
        for x in actionable:
            if x["status"] in BASELINE_FREEZE and x["key"] in snapshot:
                frozen[x["key"]] = hashes[x["key"]]
                n += 1
        save_json(config.IGNORE, frozen, indent=None)
        print(f"  已冻结 {n} 条基线期就存在的条目 → {config.IGNORE}"
              f"（共 {len(frozen)} 条永久跳过）")
        print("  基线之后新出现的条目仍在待办里。重跑 python scan.py 查看。")
        return

    if args.baseline:
        frozen = dict(ignore)
        for x in actionable:
            if x["status"] in BASELINE_FREEZE:
                frozen[x["key"]] = hashes[x["key"]]
        save_json(config.IGNORE, frozen, indent=None)
        save_json(config.SNAPSHOT, hashes, indent=None)
        print(f"  已定基线：{len(frozen)} 条永久跳过 → {config.IGNORE}")
        print(f"  已更新 EN 指纹 → {config.SNAPSHOT}")
        print("  （这些条目只有在官方改写英文原文后才会重新出现）")
    elif args.accept:
        # 闸门：outdated_official 是「官方有中文、但英文原文被改过」。--accept 会把
        # snapshot 刷成当前指纹，这些条目下轮就判回 official —— 默认取批
        # （todo,stale）又取不到它们，两头一夹就永久丢失。
        stuck = counts.get("outdated_official", 0)
        if stuck and not args.force:
            print(f"\n[拒绝推进基线] 还有 {stuck} 条 outdated_official 没处理。")
            print("  先 python batch_next.py --status outdated_official 翻掉，")
            print("  或确认这些官方译文不用跟进，再跑 python scan.py --accept --force。")
            sys.exit(1)
        save_json(config.SNAPSHOT, hashes, indent=None)
        print(f"  已更新基线 → {config.SNAPSHOT}")
    else:
        print("  （未更新基线。确认看过变更后跑 python scan.py --accept）")


if __name__ == "__main__":
    main()
