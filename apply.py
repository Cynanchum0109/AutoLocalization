#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""apply.py - 把 out/progress.json 的译文写进成品文件。

输出到 Workplace/translated/**（不直接动游戏目录），确认后手动拷贝到：
  ...\LimbusCompany_Data\Lang\LLC_zh-CN\

规则：
  - **复制原文件再原地改**：整份复制 EN 原文件当底稿，只动我们翻过的那些字段，
    其余字段、条目顺序、顶层其他键一律原样保留 —— 不重建结构，避免遗漏没考虑到的东西
  - 官方 ZH 已有的译文会原样盖到底稿上（同 id 同字段以 ZH 为准），不覆盖人家的成果
  - 双语拼接由本脚本机械完成：中文译文 + 换行 + 空格 + 英文原文（config.BILINGUAL）。
    progress.json 里存的始终是纯中文，贴原文这一步不经过 LLM
  - 游戏目录只读不写，产物一律落在 Workplace/translated/
  - 只覆盖 progress 里有译文的字段，其余原样保留
  - 只输出真正有改动的文件
  - 格式对齐官方：utf-8 无 BOM、LF、indent=2

用法：
  python apply.py
  python apply.py --clean    先清空 Workplace/translated 再生成
"""

import argparse
import copy
import hashlib
import json
from datetime import datetime
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from limbus import walk
from limbus.fmtcode import has_cjk
from limbus.jsonio import load_json, save_json, setup_stdout


def main():
    setup_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--install", action="store_true",
                    help="产出后直接拷进游戏 LLC_zh-CN 目录（覆盖前自动备份到 Workplace/backup_<时间>/）")
    ap.add_argument("--force", action="store_true",
                    help="忽略指纹缓存，强制重写所有文件（危险：会覆盖 Workplace/translated 里的任何手改）")
    ap.add_argument("--file", help="只输出指定文件名或 scope/文件名，例如 RPGSystem/rpg-loc-dialogue-floor-5-b.json")
    args = ap.parse_args()

    progress = load_json(config.PROGRESS) or {}
    if not progress:
        print("progress.json 为空，没有可写出的译文。")
        return

    apply_state = load_json(config.APPLY_STATE) or {}

    if args.clean and os.path.isdir(config.WORK_ROOT):
        shutil.rmtree(config.WORK_ROOT)

    # key -> (译文, 英文原文)，按文件分组
    by_file = {}
    for key, entry in progress.items():
        head, item_id, field = key.rsplit("#", 2)
        by_file.setdefault(head, {})[(item_id, field)] = (entry["zh"], entry.get("en", ""))

    written = 0
    skipped = 0
    total_fields = 0
    for t in walk.iter_targets():
        label = t.label
        if args.file and args.file not in (label, os.path.basename(label)):
            continue
        edits = by_file.get(label)
        if not edits:
            continue

        # 指纹 = 这个文件所有 (id, field) -> (zh, en) 的内容，任何一条变了指纹就变。
        # 指纹没变 且 产物文件已经在磁盘上 → 跳过，不重写，保留 Workplace/translated 里可能存在的手改。
        fingerprint = hashlib.sha256(
            json.dumps(sorted(edits.items()), ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        if not args.force and apply_state.get(label) == fingerprint and os.path.exists(t.out_path):
            skipped += 1
            continue

        en_data = load_json(t.en_path, on_error="warn")
        if en_data is None:
            continue

        # 底稿：整份复制 EN 原文件，条目顺序、字段、顶层其他键全部照搬。
        # 之所以不拿官方 ZH 当底稿：ZH 侧可能是残缺的占位文件
        # （P10616.json 就只有 67 条，大半是空对象 {}），照抄会留一堆垃圾条目。
        data = copy.deepcopy(en_data)
        items = walk.data_list(data)
        index = walk.index_by_id(data)
        en_index = walk.index_by_id(en_data)

        # 官方 ZH 已有的译文盖上来，别把人家的成果覆盖掉。
        # 只盖**真的是中文**的字段：ZH 侧存在大量韩文占位（'동부섕크 인격스더미'），
        # 无脑 update 会把 EN 里的真台词换成这种垃圾。
        zh_data = load_json(t.zh_path) if os.path.exists(t.zh_path) else None
        zh_index = walk.index_by_id(zh_data) if zh_data else {}
        for zid, zitem in zh_index.items():
            if not isinstance(zitem, dict):
                continue
            if zid in index:
                target = index[zid]
                # 按路径深合并：技能文件的正文全在 levelList[].coinlist[] 里，
                # 只比对顶层字段会把官方已译的技能整条丢掉。
                for path, v in walk.iter_string_paths(zitem):
                    if has_cjk(v) and isinstance(walk.get_by_path(target, path), str):
                        walk.set_by_path(target, path, v)
                # 顶层的非字符串字段，底稿里没有的补上
                for k, v in zitem.items():
                    if not isinstance(v, str) and k not in target:
                        target[k] = copy.deepcopy(v)
            else:
                # ZH 有、EN 已经没有的条目：留在末尾，不主动删
                # （官方删条目由变更报告人工确认）
                items.append(copy.deepcopy(zitem))
                index[zid] = items[-1]

        applied = 0
        for (item_id, field), (zh, en) in sorted(edits.items()):
            item = index.get(item_id)
            if item is None:
                # 底稿里没有这条（官方新增的条目）：从 EN 文件整条搬过来再改
                en_item = en_index.get(item_id)
                if en_item is None:
                    print(f"  [跳过] {label}#{item_id}：EN/底稿里都找不到这条")
                    continue
                item = copy.deepcopy(en_item)
                items.append(item)
                index[item_id] = item

            # 英文原文优先取 EN 文件当前值，回退到合批时记下的原文
            en_item = en_index.get(item_id)
            src = walk.get_by_path(en_item, field) if en_item else None
            if not isinstance(src, str) or not src:
                src = en
            value = (zh + config.BILINGUAL_JOIN + src
                     if config.BILINGUAL and src else zh)
            try:
                walk.set_by_path(item, field, value)
            except (KeyError, IndexError, TypeError):
                # 底稿里没有这条路径（官方 ZH 结构与 EN 不一致）：整条换成 EN 的再写
                if en_item is None:
                    print(f"  [跳过] {label}#{item_id}#{field}：底稿里没有这个路径")
                    continue
                fixed = copy.deepcopy(en_item)
                idx = items.index(item)
                items[idx] = fixed
                index[item_id] = fixed
                item = fixed
                walk.set_by_path(item, field, value)
            applied += 1

        save_json(t.out_path, data, indent=2)
        apply_state[label] = fingerprint
        written += 1
        total_fields += applied
        print(f"  {label}  ({applied} 字段) -> {os.path.relpath(t.out_path, config.BASE_DIR)}")

    save_json(config.APPLY_STATE, apply_state, indent=1)
    print(f"\n写出 {written} 个文件，跳过 {skipped} 个未变化的文件，共应用 {total_fields} 处译文。")
    print(f"产物目录：{config.WORK_ROOT}")

    if not args.install:
        print("确认无误后拷贝到 LimbusCompany_Data/Lang/LLC_zh-CN/")
        print("（或直接跑 python apply.py --install 自动拷贝）")
        return

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = os.path.join(config.BASE_DIR, "Workplace", "backup_" + stamp)
    copied = backed = 0
    for root, _, files in os.walk(config.WORK_ROOT):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, config.WORK_ROOT)
            dst = os.path.join(config.ZH_ROOT, rel)
            if os.path.exists(dst):
                bak = os.path.join(backup_root, rel)
                os.makedirs(os.path.dirname(bak), exist_ok=True)
                shutil.copy2(dst, bak)
                backed += 1
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
            print(f"  -> {dst}")
    print(f"\n已拷贝 {copied} 个文件到 {config.ZH_ROOT}")
    if backed:
        print(f"覆盖前的 {backed} 个原文件已备份到 {backup_root}")


if __name__ == "__main__":
    main()
