#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan.py - 扫描 tier0 范围，算出每条文本的状态，并与上次快照对比。

产出：
  out/state.json         待办清单（只含需要处理的条目）
  out/snapshot_new.json  本次 EN 原文指纹
  out/changes/<时间>.md  与 out/snapshot.json 的差异报告

规则：只翻「中文没有、英文有」的部分。StoryData / PersonalityVoiceDlg 按文件判断，
其余按 JSON 条目判断（config.FILE_LEVEL_SCOPES）。只有 todo 进队列。

状态：
  todo              要翻：ZH 缺整个文件（文件级 scope）/ 缺这个条目（条目级 scope）
  ours              我们译过（英文原文之后改了也不重翻）
  official          ZH 已有中文
  has_zh            ZH 已有该文件/条目，只是缺这个字段 —— 按规则不补
  same_as_en        ZH 已有，但与 EN 一模一样 —— 按规则不翻，仅作统计。
                    例外：同一条目的其他字段是我们译的（ZH 里是装进游戏的我们的产出，
                    英文是当时没覆盖到的字段），算 todo
  zh_placeholder    ZH 已有，但没有一个汉字（韩文占位等）—— 按规则不翻，仅作统计
  ignored           记在 ignore.json 里的 todo，永久跳过

用法：
  python tools/scan.py                 只扫描并报告，不动基线
  python tools/scan.py --accept        把本次 EN 指纹存为新基线（每次看完变更后用）
  python tools/scan.py --baseline      一次性：当前所有 todo 记入 ignore.json，以后不再出现
  python tools/scan.py --show-ignored  报告里附上被忽略的条目统计
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

ACTIONABLE = ("todo",)
STATUSES = ("todo", "ours", "official", "has_zh", "same_as_en", "zh_placeholder", "ignored")


def classify(unit, zh_file_exists, zh_item, zh_val, prog_entry, our_item=False):
    en_h = walk.src_hash(unit["original"])
    if prog_entry:
        return "ours", en_h
    if unit["scope"] in config.FILE_LEVEL_SCOPES:
        missing = not zh_file_exists
    else:
        missing = zh_item is None
    if missing:
        return "todo", en_h
    if zh_val is None or not isinstance(zh_val, str) or zh_val == "":
        return "has_zh", en_h
    if zh_val == unit["original"]:
        return ("todo" if our_item else "same_as_en"), en_h
    if not has_cjk(zh_val):
        return "zh_placeholder", en_h
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
    args = ap.parse_args()

    progress = load_json(config.PROGRESS) or {}
    snapshot = load_json(config.SNAPSHOT) or {}
    ignore   = load_json(config.IGNORE) or {}
    first_run = not snapshot

    # 我们译过其他字段的条目：ZH 那份是装进游戏的我们的产出，同条目里剩下的英文是当时
    # 没覆盖到的字段（如事件选项），不是官方保留原文。按条目而非按文件，免得把官方
    # 有意留英文的条目（Announcer 里的司书名等）也翻出来。
    our_items = {k.rsplit("#", 1)[0] for k in progress}
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
        zh_file_exists = os.path.exists(t.zh_path)
        zh_data = load_json(t.zh_path) if zh_file_exists else None
        if not zh_file_exists:
            missing_zh_files.append(t.label)
        zh_index = walk.index_by_id(zh_data) if zh_data else {}

        for unit in walk.iter_units(t, en_data):
            key = unit["key"]
            zh_item = zh_index.get(unit["id"])
            # field 是路径串（levelList[0].coinlist[2].coindescs[4].desc / texts[3].text），
            # 必须按路径取，用 dict.get 会一律读成 None。
            zh_val  = (walk.get_by_path(zh_item, unit["field"])
                       if isinstance(zh_item, dict) else None)
            status, en_h = classify(unit, zh_file_exists, zh_item, zh_val, progress.get(key),
                                   f"{t.label}#{unit['id']}" in our_items)
            if status == "todo" and ignore.get(key) == en_h:
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
        lines += ["> 首次扫描，没有可比对的基线。跑 `python tools/scan.py --accept` 建立基线。", ""]
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
    for s in STATUSES:
        lines.append(f"| {s} | {counts.get(s, 0)} |")
    lines.append("")

    todo_files = sorted(((f, c) for f, c in per_file.items() if c["todo"]),
                        key=lambda x: -x[1]["todo"])
    if todo_files:
        lines += ["## 需要动手的文件", "", "| 文件 | todo |", "|---|---|"]
        for f, c in todo_files[:100]:
            lines.append(f"| `{f}` | {c['todo']} |")
        lines.append("")
    if missing_zh_files:
        lines += [f"## ZH 侧缺失的整个文件（{len(missing_zh_files)}）", ""]
        lines += [f"- `{f}`" for f in missing_zh_files[:100]]
        lines.append("")

    with open(report, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))

    # ---------- 控制台摘要 ----------
    print()
    for s in STATUSES:
        print(f"  {s:20} {counts.get(s, 0):8}")
    print()
    print(f"  与基线对比：新增 {len(added)} / 改写 {len(modified)} / 删除 {len(removed)}")
    print(f"  待办清单 → {config.STATE}（{len(actionable)} 条）")
    print(f"  变更报告 → {report}")

    if args.freeze_old:
        frozen = dict(ignore)
        n = 0
        for x in actionable:
            if x["key"] in snapshot:
                frozen[x["key"]] = hashes[x["key"]]
                n += 1
        save_json(config.IGNORE, frozen, indent=None)
        print(f"  已冻结 {n} 条基线期就存在的条目 → {config.IGNORE}"
              f"（共 {len(frozen)} 条永久跳过）")
        print("  基线之后新出现的条目仍在待办里。重跑 python tools/scan.py 查看。")
        return

    if args.baseline:
        frozen = dict(ignore)
        for x in actionable:
            frozen[x["key"]] = hashes[x["key"]]
        save_json(config.IGNORE, frozen, indent=None)
        save_json(config.SNAPSHOT, hashes, indent=None)
        print(f"  已定基线：{len(frozen)} 条永久跳过 → {config.IGNORE}")
        print(f"  已更新 EN 指纹 → {config.SNAPSHOT}")
        print("  （这些条目只有在官方改写英文原文后才会重新出现）")
    elif args.accept:
        save_json(config.SNAPSHOT, hashes, indent=None)
        print(f"  已更新基线 → {config.SNAPSHOT}")
    else:
        print("  （未更新基线。确认看过变更后跑 python tools/scan.py --accept）")


if __name__ == "__main__":
    main()
