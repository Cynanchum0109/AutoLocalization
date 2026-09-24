#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rebuild_glossary.py - 术语表自动区重建（一键，无需 API）

流程：
  1. 备份当前 glossary.json
  2. 保护区（第 1 条至 "Udjat"）原样保留，不做任何改动
  3. 全量扫描 EN/ZH 对照文件，用 term_rules 的准入规则重新提取自动区
     - 双语值（中文\\n英文）自动拆分只取中文
     - 句子/标题/碎片/格式残留在入口拒收，不再事后清洗
     - 复合词不删除（引擎是子串匹配，复合条目直接命中更可靠）
  4. 写出新 glossary.json + rebuild_report.md（新增/丢弃/拒收统计）
  5. 重置 glossary_progress.json，后续 update_glossary.py 增量更新接着用
"""

import os
import sys
from collections import Counter
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from json_io import load_json, save_json
from term_rules import split_bilingual, admit_term

# ==================== 路径配置 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EN_ROOT = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en"
ZH_ROOT = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN"
GLOSSARY_PATH = os.path.join(BASE_DIR, "glossary.json")           # 只读（现役术语表）
OUTPUT_PATH   = os.path.join(BASE_DIR, "glossary_rebuilt.json")   # 重建结果写这里，人工审查后手动替换
PROGRESS_PATH = os.path.join(BASE_DIR, "glossary_progress.json")
REPORT_PATH   = os.path.join(BASE_DIR, "rebuild_report.md")

PROTECT_PIVOT = "Udjat"   # 保护区结束键（含）

TERM_FIELDS = ["teller", "name", "nickName", "place", "title"]

SCAN_SUBDIRS = [
    None,
    "BattleAnnouncerDlg",
    "BgmLyrics",
    "EGOVoiceDig",
    "PersonalityVoiceDlg",
    "StoryData",
]


def iter_file_pairs():
    """遍历所有 (en_path, zh_path, 标签)。"""
    for subdir in SCAN_SUBDIRS:
        en_dir = os.path.join(EN_ROOT, subdir) if subdir else EN_ROOT
        zh_dir = os.path.join(ZH_ROOT, subdir) if subdir else ZH_ROOT
        if not os.path.isdir(en_dir):
            continue
        for en_fn in sorted(os.listdir(en_dir)):
            if not (en_fn.startswith('EN_') and en_fn.endswith('.json')):
                continue
            zh_path = os.path.join(zh_dir, en_fn[3:])
            if os.path.exists(zh_path):
                yield os.path.join(en_dir, en_fn), zh_path, (subdir or "根目录")


def extract_pair(en_path, zh_path, existing, collected, reject_stats):
    """提取一对文件的候选术语，写入 collected。"""
    en_data = load_json(en_path)
    zh_data = load_json(zh_path)
    if not (isinstance(en_data, dict) and isinstance(zh_data, dict)):
        return
    if 'dataList' not in en_data or 'dataList' not in zh_data:
        return

    zh_map = {item['id']: item for item in zh_data['dataList']
              if isinstance(item, dict) and 'id' in item}

    for en_item in en_data['dataList']:
        if not isinstance(en_item, dict):
            continue
        zh_item = zh_map.get(en_item.get('id'))
        if not isinstance(zh_item, dict):
            continue
        for field in TERM_FIELDS:
            en_val = en_item.get(field)
            zh_val = zh_item.get(field)
            if not isinstance(en_val, str) or not isinstance(zh_val, str):
                continue
            en_val = en_val.strip()
            if not en_val or en_val in existing or en_val in collected:
                continue
            zh_clean = split_bilingual(zh_val)
            if zh_clean is None:
                reject_stats['bilingual_unsplittable'] += 1
                continue
            ok, reason = admit_term(en_val, zh_clean)
            if ok:
                collected[en_val] = zh_clean
            else:
                reject_stats[reason] += 1


def main():
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("Limbus Company 术语表自动区重建")
    print(f"运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    glossary = load_json(GLOSSARY_PATH)
    if not glossary:
        print(f"[错误] 无法读取 {GLOSSARY_PATH}")
        sys.exit(1)

    keys = list(glossary.keys())
    if PROTECT_PIVOT not in glossary:
        print(f"[错误] 保护区结束键 {PROTECT_PIVOT!r} 不在术语表中，中止")
        sys.exit(1)
    pivot_idx = keys.index(PROTECT_PIVOT)
    protected = {k: glossary[k] for k in keys[:pivot_idx + 1]}
    old_auto  = {k: glossary[k] for k in keys[pivot_idx + 1:]}
    print(f"当前术语表 {len(glossary)} 条：保护区 {len(protected)} 条，自动区 {len(old_auto)} 条")


    # 全量扫描重建自动区
    collected = {}
    reject_stats = Counter()
    file_count = 0
    progress_files = {}
    print("\n[扫描中...]")
    for en_path, zh_path, label in iter_file_pairs():
        extract_pair(en_path, zh_path, protected, collected, reject_stats)
        file_count += 1
        try:
            mtime = max(os.path.getmtime(en_path), os.path.getmtime(zh_path))
        except OSError:
            mtime = 0
        rel = os.path.relpath(en_path, EN_ROOT).replace('\\', '/')
        progress_files[rel] = mtime

    print(f"扫描 {file_count} 对文件，自动区收录 {len(collected)} 条，拒收 {sum(reject_stats.values())} 条")

    # 旧自动区中本次扫描不到的条目（历史语料来源）：能过准入规则的保留
    retained = {}
    for k, v in old_auto.items():
        if k not in collected and admit_term(k, v)[0]:
            retained[k] = v
    if retained:
        print(f"旧自动区保留 {len(retained)} 条（语料中已扫描不到但通过准入规则）")

    # 写出到侧文件，现役 glossary.json 不动；人工审查后手动替换：
    #   copy glossary_rebuilt.json glossary.json
    new_glossary = {**protected, **collected, **retained}
    save_json(OUTPUT_PATH, new_glossary, indent=2)
    print(f"重建结果已写出 → {os.path.basename(OUTPUT_PATH)}：{len(new_glossary)} 条（现役 glossary.json 未动）")

    # 进度记录（替换生效后 update_glossary.py 增量更新从当前状态接续）
    save_json(PROGRESS_PATH, {
        "processed": progress_files,
        "last_run": datetime.now().isoformat(),
        "note": "由 rebuild_glossary.py 重置",
    }, indent=2)

    # 报告
    dropped = {k: v for k, v in old_auto.items() if k not in collected and k not in retained}
    added   = {k: v for k, v in collected.items() if k not in old_auto}
    changed = {k: (old_auto[k], collected[k]) for k in collected
               if k in old_auto and old_auto[k] != collected[k]}

    lines = [
        "# 术语表自动区重建报告",
        f"\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n| 项目 | 数量 |",
        f"|---|---|",
        f"| 保护区（未动） | {len(protected)} |",
        f"| 旧自动区 | {len(old_auto)} |",
        f"| 新自动区（本次扫描收录） | {len(collected)} |",
        f"| 历史保留（扫描不到但过准入） | {len(retained)} |",
        f"| 新增（旧自动区没有） | {len(added)} |",
        f"| 丢弃（未通过准入规则） | {len(dropped)} |",
        f"| 译文变化（同键不同值） | {len(changed)} |",
        "\n## 拒收原因统计\n",
        "| 原因 | 次数 |",
        "|---|---|",
    ]
    for reason, n in reject_stats.most_common():
        lines.append(f"| {reason} | {n} |")

    def _section(title, mapping, limit=100):
        lines.append(f"\n## {title}（前 {min(limit, len(mapping))} 条，共 {len(mapping)} 条）\n")
        lines.append("| EN | ZH |")
        lines.append("|---|---|")
        for k, v in list(mapping.items())[:limit]:
            lines.append(f"| `{k}` | `{v}` |")

    _section("新增条目", added)
    _section("丢弃条目", dropped)
    if changed:
        lines.append(f"\n## 译文变化（共 {len(changed)} 条）\n")
        lines.append("| EN | 旧 ZH | 新 ZH |")
        lines.append("|---|---|---|")
        for k, (old, new) in list(changed.items())[:100]:
            lines.append(f"| `{k}` | `{old}` | `{new}` |")

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"报告已写出 → {os.path.basename(REPORT_PATH)}")


if __name__ == "__main__":
    main()
