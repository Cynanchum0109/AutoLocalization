#!/usr/bin/env python3
"""
update_glossary.py - 增量更新术语表

功能：
1. 扫描中英文对照文件（以 JSON ID 为键匹配）
2. 提取 teller / name / nickName / place / title 字段的中英文直接映射
3. 将新发现的术语追加至 glossary.json
4. 使用文件修改时间跟踪已处理文件，支持增量更新（只处理自上次运行后有变化的文件）

说明：
- 此脚本只做字段级别的直接对应提取（不调用 AI 翻译）
- 提取到的术语已有明确的中文对应，可以直接加入术语表
- 若术语已存在于 glossary.json 中则跳过
- 运行后会打印所有新增术语，便于审查
"""

import os
import sys
import re
from datetime import datetime

# 根目录共享模块（本脚本在 glossary/ 子目录运行，需手动加父目录到 path）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from json_io import load_json as _load_json, save_json
from term_rules import split_bilingual, admit_term

# ==================== 路径配置 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EN_ROOT = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en"
ZH_ROOT = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN"
GLOSSARY_PATH = os.path.join(BASE_DIR, "glossary.json")
PROGRESS_PATH = os.path.join(BASE_DIR, "glossary_progress.json")

# ==================== 配置 ====================
# 提取术语的字段（这些字段通常包含人名、地名、职位等）
TERM_FIELDS = ["teller", "name", "nickName", "place", "title"]

# 扫描的目录（包含人工审校目录，因为我们只提取名词，不需要翻译）
SCAN_SUBDIRS = [
    None,               # 根目录（830+ 个文件）
    "BattleAnnouncerDlg",
    "BgmLyrics",
    "EGOVoiceDig",
    "PersonalityVoiceDlg",
    "StoryData",
]

# 单个术语的最大长度限制（过长的可能是句子，不是术语）
MAX_EN_TERM_LEN = 80
MAX_ZH_TERM_LEN = 40

# ==================== 工具函数 ====================

def has_chinese(text: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in text)

def has_english(text: str) -> bool:
    return bool(re.search(r'[a-zA-Z]', text))

def is_valid_term(en_text: str, zh_text: str) -> bool:
    """判断是否为有效的术语映射"""
    if not en_text or not zh_text:
        return False
    en_text = en_text.strip()
    zh_text = zh_text.strip()
    if not en_text or not zh_text:
        return False
    if not has_english(en_text):
        return False
    if not has_chinese(zh_text):
        return False
    if '??' in en_text or '??' in zh_text:
        return False
    # 排除过长的文本（可能是句子而非术语）
    if len(en_text) > MAX_EN_TERM_LEN or len(zh_text) > MAX_ZH_TERM_LEN:
        return False
    # 排除全大写的代码式字符串（如 VERY_HIGH、TRUE 等）
    if re.match(r'^[A-Z0-9_,().\s]+$', en_text):
        return False
    return True

def load_json(path: str):
    """加载 JSON 文件，自动处理 BOM 和编码"""
    return _load_json(path)

def get_file_key(en_path: str) -> str:
    """生成文件的唯一标识（用于进度跟踪）"""
    rel = os.path.relpath(en_path, EN_ROOT)
    return rel.replace('\\', '/')

def extract_terms_from_pair(en_path: str, zh_path: str, existing: dict) -> dict:
    """
    从一对 EN/ZH 文件中提取新术语。
    以 ID 为键匹配 EN 和 ZH 中的同一条目，提取指定字段的映射。
    """
    en_data = load_json(en_path)
    zh_data = load_json(zh_path)

    if not en_data or not zh_data:
        return {}
    if 'dataList' not in en_data or 'dataList' not in zh_data:
        return {}

    # 以 ID 为键建立 ZH 映射
    zh_map = {}
    for item in zh_data.get('dataList', []):
        if 'id' in item:
            zh_map[item['id']] = item

    new_terms = {}
    for en_item in en_data.get('dataList', []):
        item_id = en_item.get('id')
        if item_id is None:
            continue
        zh_item = zh_map.get(item_id, {})

        for field in TERM_FIELDS:
            en_val = en_item.get(field)
            zh_val = zh_item.get(field)

            if not isinstance(en_val, str) or not isinstance(zh_val, str):
                continue

            en_val = en_val.strip()

            # 跳过已存在的术语
            if en_val in existing or en_val in new_terms:
                continue

            # 双语值（中文\n英文）只取中文行
            zh_clean = split_bilingual(zh_val)
            if zh_clean is None:
                continue

            ok, _reason = admit_term(en_val, zh_clean)
            if ok:
                new_terms[en_val] = zh_clean

    return new_terms

# ==================== 主函数 ====================

def main():
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("Limbus Company 术语表增量更新工具")
    print(f"运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 加载现有术语表
    glossary = load_json(GLOSSARY_PATH) or {}
    print(f"当前术语表条目数：{len(glossary)}")

    # 加载进度记录（存储每个文件上次处理时的修改时间）
    progress = load_json(PROGRESS_PATH) or {"processed": {}, "last_run": ""}
    processed_files = progress.get("processed", {})  # {file_key: mtime}

    all_new_terms = {}
    processed_count = 0
    skipped_count = 0
    missing_zh_count = 0

    print("\n[扫描中...]\n")

    for subdir in SCAN_SUBDIRS:
        if subdir is None:
            en_dir = EN_ROOT
            zh_dir = ZH_ROOT
            label = "根目录"
        else:
            en_dir = os.path.join(EN_ROOT, subdir)
            zh_dir = os.path.join(ZH_ROOT, subdir)
            label = subdir

        if not os.path.exists(en_dir):
            continue

        dir_new_count = 0
        for en_fn in sorted(os.listdir(en_dir)):
            if not (en_fn.startswith('EN_') and en_fn.endswith('.json')):
                continue

            zh_fn = en_fn[3:]  # 去掉 EN_ 前缀
            en_path = os.path.join(en_dir, en_fn)
            zh_path = os.path.join(zh_dir, zh_fn)

            if not os.path.exists(zh_path):
                missing_zh_count += 1
                continue

            file_key = get_file_key(en_path)

            # 检查文件是否有更新（比较修改时间）
            try:
                en_mtime = os.path.getmtime(en_path)
                zh_mtime = os.path.getmtime(zh_path)
                max_mtime = max(en_mtime, zh_mtime)
            except OSError:
                max_mtime = 0

            last_mtime = processed_files.get(file_key, 0)

            if max_mtime <= last_mtime:
                skipped_count += 1
                continue  # 文件未更新，跳过

            # 提取新术语（传入已有术语+本次发现的术语，避免重复）
            combined_existing = {**glossary, **all_new_terms}
            new_terms = extract_terms_from_pair(en_path, zh_path, combined_existing)

            if new_terms:
                all_new_terms.update(new_terms)
                dir_new_count += len(new_terms)
                print(f"  [{label}] {en_fn}: 发现 {len(new_terms)} 个新术语")

            # 更新进度记录（使用文件修改时间作为版本标记）
            processed_files[file_key] = max_mtime
            processed_count += 1

        if dir_new_count > 0:
            print(f"  └── {label} 小计：{dir_new_count} 个新术语\n")

    # ==================== 结果输出 ====================
    print("=" * 60)
    print(f"扫描完成")
    print(f"  已处理（有更新）：{processed_count} 个文件")
    print(f"  已跳过（无更新）：{skipped_count} 个文件")
    print(f"  无对应中文文件：{missing_zh_count} 个文件")
    print(f"  发现新术语：{len(all_new_terms)} 个")
    print("=" * 60)

    if all_new_terms:
        # 更新术语表
        glossary.update(all_new_terms)
        save_json(GLOSSARY_PATH, glossary, indent=2)
        print(f"\n术语表已更新：共 {len(glossary)} 个条目（本次新增 {len(all_new_terms)} 个）")

        print("\n本次新增术语：")
        for en, zh in all_new_terms.items():
            print(f"  {en!r:40s} -> {zh!r}")
    else:
        print("\n无新术语，术语表无需更新。")

    # 保存进度
    progress["processed"] = processed_files
    progress["last_run"] = datetime.now().isoformat()
    save_json(PROGRESS_PATH, progress, indent=2)
    print(f"\n进度已保存至 {PROGRESS_PATH}")
    print("下次运行时将只处理有更新的文件（增量模式）。")

if __name__ == "__main__":
    main()
