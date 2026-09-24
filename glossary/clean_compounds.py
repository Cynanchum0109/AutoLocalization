#!/usr/bin/env python3
"""
clean_compounds.py — 术语表复合条目清洗（统一脚本，替代 phase3/3b/4/5）

执行顺序（自动迭代至收敛）：
  1. EN键含 \n：拆分为独立术语，提取有效部件加入词典，删除复合条目
  2. ZH值含 \n（EN干净）：归一化（"::\n"→"::"，其余"\n"→" "）
  3. 编号变体移除：EN = "[基础术语] [数字/罗马数字]"，且 ZH = base_zh + numeral
  4. 等级变体移除：EN 末尾为 "+"/"++"，且 ZH 末尾为 "+"/"++"，且基础 EN 在词典中
  5. 序数词变体移除：EN = "[序数词] [基础术语]"，且 ZH = ordinal_zh + base_zh
  6. 核心词包含检测：自动区条目 EN键含前264条 EN 词组，或 ZH值含前264条 ZH 子串 → 删除
  7. 复合条目检测，迭代至收敛：
     a. EN 2段/3段拆分 + ZH精确验证（分隔符：空格/无/破折号/短横线）
     b. ZH递归分解（空格 / " - "，处理 EN 为缩写的情况；地支字符作为合法右侧分量）
"""

import sys, functools, re
from pathlib import Path
from datetime import datetime
from itertools import product
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# 根目录共享模块（本脚本在 glossary/ 子目录运行，需手动加父目录到 path）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from json_io import load_json, save_json

BASE          = Path(r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Lang\tempworkplace")
GLOSSARY_PATH = BASE / "glossary.json"
REPORT_PATH   = BASE / "clean_compounds_report.md"
PROTECTED_KEY = "Udjat"

# 核心机制词，即使可分解也不删除
HARD_PROTECT  = {"Slash", "Pierce", "Blunt", "Random", "Keywordless", "Right Arm", "Left Arm"}

# ZH三字前缀去重跳过组（不同概念偶然共享前缀）
SKIP_DEDUP_PREFIXES = frozenset({'感应度', '阶段封'})

# ZH拼接分隔符尝试顺序：空格 > 无分隔 > 破折号（含无空格短横线）
SEPS = [" ", "", " - ", "-"]

# 编号后缀正则（EN键末尾，空格隔开）
_NUMERAL = re.compile(
    r'^(.+?) '
    r'([IVX]+|[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+|[ⅠⅤ]{1,5}|\d+)$'
)

# 地支字符（允许作为 " - " 右侧的合法单字分量，即使不在 zh_set 中）
EARTHLY_BRANCHES = frozenset('子丑寅卯辰巳午未申酉戌亥')

# 英文序数词 → 中文序数前缀
_ORDINAL_EN_ZH: dict[str, str] = {
    'First': '第一', 'Second': '第二', 'Third': '第三',
    'Fourth': '第四', 'Fifth': '第五', 'Sixth': '第六',
    'Seventh': '第七', 'Eighth': '第八', 'Ninth': '第九',
    'Tenth': '第十', 'Eleventh': '第十一', 'Twelfth': '第十二',
    'Thirteenth': '第十三', 'Fourteenth': '第十四', 'Fifteenth': '第十五',
    'Sixteenth': '第十六', 'Seventeenth': '第十七', 'Eighteenth': '第十八',
    'Nineteenth': '第十九', 'Twentieth': '第二十',
}


# ─── 工具 ──────────────────────────────────────────────────────

def load_glossary(path):
    # 保留原行为：读失败直接抛异常
    return load_json(str(path), on_error="raise")

def save_glossary(path, data):
    save_json(str(path), data, indent=2)


# ─── 步骤 1：换行符条目处理 ────────────────────────────────────

def align_newline_parts(en_key: str, zh_val: str) -> list[tuple[str, str]]:
    """
    将 EN/ZH 按 \n 拆分并对齐，返回 [(en_part, zh_part), ...]。
    对部件数不等的情况应用专项策略：
      EN=2, ZH=3 (R Corp. 4th Pack 系列)：合并前 2 个 ZH 段
      EN=3, ZH=2 (Full Moon 系列)：合并前 2 个 EN 段
      EN=3, ZH=2 (E.G.O:: / W Corp. L4 系列)：合并后 2 个 EN 段
    """
    ep = [p.strip() for p in en_key.split('\n') if p.strip()]
    zp = [p.strip() for p in zh_val.split('\n') if p.strip()]
    en_n, zh_n = len(ep), len(zp)

    if en_n == zh_n:
        return list(zip(ep, zp))

    if en_n == 2 and zh_n == 3:
        merged_zh = [' '.join(zp[:zh_n - en_n + 1])] + zp[zh_n - en_n + 1:]
        return list(zip(ep, merged_zh))

    if en_n == 3 and zh_n == 2:
        if ep[0].startswith('Full Moon'):
            merged_en = [' '.join(ep[:en_n - zh_n + 1])] + ep[en_n - zh_n + 1:]
        else:
            merged_en = ep[:zh_n - 1] + [' '.join(ep[zh_n - 1:])]
        return list(zip(merged_en, zp))

    # 未知情形：截断至较短一侧
    return list(zip(ep, zp))


def handle_newline_entries(glossary: dict, protected_keys: set) -> tuple[dict, dict]:
    """
    处理所有换行符条目，返回 (新词典, 统计信息)。
    统计信息包含: removed, added, zh_fixed, conflicts
    """
    compound_keys = set()
    new_terms: dict[str, str] = {}
    conflicts: list[tuple] = []
    added: list[tuple] = []
    zh_fixed = 0

    for key in list(glossary.keys()):
        if key in protected_keys:
            continue
        zh = glossary[key]

        if '\n' in key:
            compound_keys.add(key)
            for en_part, zh_part in align_newline_parts(key, zh):
                if not en_part or not zh_part:
                    continue
                if en_part in protected_keys:
                    continue
                if en_part in glossary:
                    if glossary[en_part] != zh_part:
                        conflicts.append((en_part, zh_part, glossary[en_part]))
                elif en_part in new_terms:
                    if new_terms[en_part] != zh_part:
                        conflicts.append((en_part, zh_part, new_terms[en_part]))
                else:
                    new_terms[en_part] = zh_part
                    added.append((en_part, zh_part))

        elif '\n' in zh:
            glossary[key] = zh.replace('::\n', '::').replace('\n', ' ')
            zh_fixed += 1

    # 保留非复合条目，末尾追加新术语
    result = {k: v for k, v in glossary.items() if k not in compound_keys}
    for en, zh in added:
        if en not in result:
            result[en] = zh

    return result, {
        'removed': len(compound_keys),
        'added': len(added),
        'zh_fixed': zh_fixed,
        'conflicts': conflicts,
    }


# ─── 步骤 2：编号变体移除 ──────────────────────────────────────

def remove_numbered_variants(glossary: dict, protected_keys: set) -> tuple[dict, list]:
    """
    移除 EN = "[基础术语] [数字/罗马数字]" 且 ZH = base_zh + numeral（直接拼接，
    不含或含单一空格）的条目。
    例：'Brutality II' → '破坏力II'  （base='Brutality'→'破坏力'，num='II'）
        'Resilient IX' → '强韧IX'
        'Thrashing to Hatch Ⅰ' → '为破卵而出的挣扎Ⅰ'
    """
    removed = []
    for key, zh in list(glossary.items()):
        if key in protected_keys or key in HARD_PROTECT:
            continue
        m = _NUMERAL.match(key)
        if not m:
            continue
        base, num = m.group(1), m.group(2)
        if base not in glossary:
            continue
        base_zh = glossary[base]
        if zh in (base_zh + num, base_zh + ' ' + num):
            removed.append((key, zh, base, base_zh, num))

    for key, *_ in removed:
        del glossary[key]

    return glossary, removed


# ─── 步骤 3：等级变体移除（+/++）─────────────────────────────────

def remove_tier_variants(glossary: dict, protected_keys: set) -> tuple[dict, list]:
    """
    移除升级等级变体：EN 末尾含 "+" 或 "++"，ZH 末尾相同后缀，且基础 EN 在词典中。
    例：'Devil's Share+' → '魔鬼所享+'  （base='Devil's Share'→'魔鬼所享'）
        'Devil's Share++' → '魔鬼所享++'
    """
    removed = []
    for key, zh in list(glossary.items()):
        if key in protected_keys or key in HARD_PROTECT:
            continue
        for suffix in ('++', '+'):           # 先检测更长的后缀
            if key.endswith(suffix) and zh.endswith(suffix):
                base_en = key[:-len(suffix)]
                base_zh = zh[:-len(suffix)]
                if base_en in glossary and glossary[base_en] == base_zh:
                    removed.append((key, zh, base_en, base_zh, suffix))
                    break

    for key, *_ in removed:
        del glossary[key]

    return glossary, removed


# ─── 步骤 4：序数词变体移除 ────────────────────────────────────

def remove_ordinal_variants(glossary: dict, protected_keys: set) -> tuple[dict, list, list]:
    """
    移除序数词变体，两种模式：
      A. 基础术语已在词典：EN="[序数词] [基础术语]"，ZH=ordinal_zh+base_zh
      B. 基础术语不在词典：对同一基础词的 ≥2 个变体，若所有 ZH 均以对应序数前缀开头
         且剩余后缀完全一致，则推断 base_en → zh_suffix 并加入词典，再删除所有变体

    例：'First Note'→'第一页纸' … 'Twelfth Note'→'第十二页纸'
        → 推断 'Note'→'页纸'，删除全部12条变体
    """
    removed = []
    newly_added: list[tuple[str, str]] = []

    # 按基础词分组
    groups: dict[str, list] = defaultdict(list)
    for key, zh in glossary.items():
        if key in protected_keys or key in HARD_PROTECT:
            continue
        parts = key.split(' ', 1)
        if len(parts) == 2 and parts[0] in _ORDINAL_EN_ZH:
            groups[parts[1]].append((key, zh, parts[0], _ORDINAL_EN_ZH[parts[0]]))

    for base_en, entries in groups.items():
        # 模式 A：基础术语已在词典
        if base_en in glossary:
            base_zh = glossary[base_en]
            for key, zh, ord_w, ord_zh in entries:
                if zh in (ord_zh + base_zh, ord_zh + ' ' + base_zh,
                          base_zh + ord_zh, base_zh + ' ' + ord_zh):
                    removed.append((key, zh, base_en, base_zh, ord_w, ord_zh))
            continue

        # 模式 B：基础术语不在词典，从序列推断
        if len(entries) < 2:
            continue
        suffixes: set = set()
        for key, zh, ord_w, ord_zh in entries:
            suffixes.add(zh[len(ord_zh):] if zh.startswith(ord_zh) else None)
        if len(suffixes) == 1 and None not in suffixes:
            zh_suffix = suffixes.pop()
            if zh_suffix:  # 后缀非空
                glossary[base_en] = zh_suffix
                newly_added.append((base_en, zh_suffix))
                for key, zh, ord_w, ord_zh in entries:
                    removed.append((key, zh, base_en, zh_suffix, ord_w, ord_zh))

    for key, *_ in removed:
        if key in glossary:
            del glossary[key]

    return glossary, removed, newly_added


# ─── 步骤 5a：EN超过5词删除 ───────────────────────────────────

def remove_long_en_entries(glossary: dict, protected_keys: set,
                            max_words: int = 5) -> tuple[dict, list]:
    """
    删除自动区中 EN键单词数超过 max_words 的条目。
    长句/长标题不适合作为术语表参考词，对翻译引导无实际价值。
    """
    removed = []
    for key, zh in list(glossary.items()):
        if key in protected_keys or key in HARD_PROTECT:
            continue
        if len(key.split()) > max_words:
            removed.append((key, zh))
    for key, _ in removed:
        del glossary[key]
    return glossary, removed


# ─── 步骤 5b：EN含/符号处理 ───────────────────────────────────

def handle_slash_entries(glossary: dict, protected_keys: set) -> tuple[dict, list, list]:
    """
    处理自动区中 EN键含 '/' 的条目：
      - 若斜线两侧均为 ≤2 词的短词组，且 ZH值也可对应拆分 → 拆分为独立条目并追加
      - 所有含 '/' 的条目均删除（斜线并列形式不适合作独立术语）
    """
    to_add: dict[str, str] = {}
    deleted: list[tuple] = []

    for key, zh in list(glossary.items()):
        if key in protected_keys or key in HARD_PROTECT or '/' not in key:
            continue
        sep_en = ' / ' if ' / ' in key else '/'
        sep_zh = ' / ' if ' / ' in zh  else '/'
        parts_en = [p.strip() for p in key.split(sep_en, 1)]
        parts_zh = [p.strip() for p in zh.split(sep_zh,  1)]

        if (len(parts_en) == 2 and len(parts_zh) == 2
                and len(parts_en[0].split()) <= 2
                and len(parts_en[1].split()) <= 2):
            for ek, zv in zip(parts_en, parts_zh):
                if ek not in glossary and ek not in to_add:
                    to_add[ek] = zv

        deleted.append((key, zh))

    for key, _ in deleted:
        if key in glossary:
            del glossary[key]

    newly_added = []
    for en, zh in to_add.items():
        if en not in glossary:
            glossary[en] = zh
            newly_added.append((en, zh))

    return glossary, deleted, newly_added


# ─── 步骤 6：核心词包含检测 ────────────────────────────────────

N_CORE = 264   # 前 N 条视为核心词（用户指定）

def remove_protected_compounds(glossary: dict, n_core: int = N_CORE) -> tuple[dict, list]:
    """
    删除自动区中文本含有前 n_core 条核心词内容的条目：
      EN：auto条目的EN键中，以词/词组为单位出现了某核心EN键（长度≥3字符）
      ZH：auto条目的ZH值包含某核心ZH值（子串，长度≥2字符）
    满足EN或ZH任一条件即删除。
    """
    all_items = list(glossary.items())
    core      = dict(all_items[:n_core])
    auto_from = n_core   # 自动区起始索引

    core_en = sorted(core.keys(),   key=len, reverse=True)
    core_zh = sorted(set(core.values()), key=len, reverse=True)

    def en_hit(en_key: str) -> str | None:
        words = re.split(r'[\s/]+', en_key.replace(' - ', ' '))
        wset  = set(words)
        for pt in core_en:
            if len(pt) < 3:
                continue
            pt_words = pt.split()
            n = len(pt_words)
            if n == 1:
                if pt in wset:
                    return pt
            else:
                for i in range(len(words) - n + 1):
                    if words[i:i+n] == pt_words:
                        return pt
        return None

    def zh_hit(zh_val: str) -> str | None:
        for pz in core_zh:
            if len(pz) < 2:
                continue
            if pz in zh_val and zh_val != pz:
                return pz
        return None

    removed = []
    for en, zh in all_items[auto_from:]:
        he = en_hit(en)
        hz = zh_hit(zh)
        if he or hz:
            removed.append((en, zh, he, hz))

    remove_keys = {r[0] for r in removed}
    final = {k: v for k, v in glossary.items() if k not in remove_keys}
    return final, removed


# ─── 步骤 7：ZH首字前缀去重 ────────────────────────────────────

def remove_zh_prefix_duplicates(glossary: dict, n_core: int = N_CORE,
                                 min_prefix: int = 3) -> tuple[dict, list]:
    """
    对自动区（第 n_core 条之后）按 ZH值 的 CJK 前缀分组去重：
      - 提取 ZH值中所有 CJK 字符（忽略数字/标点），取前 min_prefix 字作为分组键
      - 若核心区（前 n_core 条）已有相同前缀 → 删除全部自动区同前缀条目
      - 否则同前缀 ≥2 条 → 保留 EN键最短（同长取先出现）的条目，删除其余
      - 跳过 SKIP_DEDUP_PREFIXES 中的前缀（不同概念偶然共享）
    """
    all_items = list(glossary.items())
    core_items = all_items[:n_core]
    auto_items = all_items[n_core:]

    def cjk_prefix(s: str) -> str:
        cjk = re.sub(r'[^\u4e00-\u9fff\u3400-\u4dbf]', '', s)
        return cjk[:min_prefix] if len(cjk) >= min_prefix else ''

    # 核心区前缀集合（作为参照）
    core_prefixes: set[str] = set()
    for _, zh in core_items:
        p = cjk_prefix(zh)
        if p:
            core_prefixes.add(p)

    # 自动区按前缀分组
    prefix_groups: dict[str, list] = defaultdict(list)
    for i, (en, zh) in enumerate(auto_items):
        p = cjk_prefix(zh)
        if p:
            prefix_groups[p].append((i, en, zh))

    delete_set: set[int] = set()
    removed: list[tuple] = []

    for prefix, entries in prefix_groups.items():
        if prefix in SKIP_DEDUP_PREFIXES:
            continue
        if prefix in core_prefixes:
            # 核心区已有此前缀 → 删除所有自动区同前缀条目
            for orig_idx, en, zh in entries:
                if orig_idx not in delete_set:
                    delete_set.add(orig_idx)
                    removed.append((en, zh, prefix, '[核心区]'))
        elif len(entries) >= 2:
            # 全自动区同前缀 → 保留最短EN（同长取先）
            sorted_entries = sorted(entries, key=lambda x: (len(x[1]), x[0]))
            for orig_idx, en, zh in sorted_entries[1:]:
                if orig_idx not in delete_set:
                    delete_set.add(orig_idx)
                    removed.append((en, zh, prefix, sorted_entries[0][1]))

    final = dict(core_items)
    for i, (en, zh) in enumerate(auto_items):
        if i not in delete_set:
            final[en] = zh

    return final, removed


# ─── 步骤 8：复合条目检测 ──────────────────────────────────────

def make_can_decompose(zh_set: frozenset):
    """
    构造带缓存的 ZH 递归分解函数。
    叶节点：zh 在 zh_set 中且长度 >= min_len。
    ' - ' 右侧 min_len=1（允许短人名如"莲"），空格两侧 min_len=2。
    """
    @functools.lru_cache(maxsize=None)
    def can(zh: str, min_len: int = 2) -> bool:
        if zh in zh_set:
            return len(zh) >= min_len
        # 允许地支字符作为 " - " 右侧的合法单字分量（min_len=1 时）
        if min_len <= 1 and len(zh) == 1 and zh in EARTHLY_BRANCHES:
            return True
        if ' - ' in zh:
            l, _, r = zh.partition(' - ')
            if can(l, 2) and can(r, 1):
                return True
        if ' ' in zh:
            ws = zh.split(' ')
            for i in range(1, len(ws)):
                l, r = ' '.join(ws[:i]), ' '.join(ws[i:])
                if len(l) >= 2 and len(r) >= 2 and can(l, 2) and can(r, 2):
                    return True
        return False
    return can


def zh_is_compound(zh: str, can) -> bool:
    """ZH值能否分解为 ≥2 个有意义部分（自身不作为叶节点）。"""
    if ' - ' in zh:
        l, _, r = zh.partition(' - ')
        if can(l, 2) and can(r, 1):
            return True
    if ' ' in zh:
        ws = zh.split(' ')
        for i in range(1, len(ws)):
            l, r = ' '.join(ws[:i]), ' '.join(ws[i:])
            if len(l) >= 2 and len(r) >= 2 and can(l, 2) and can(r, 2):
                return True
    return False


def try_en_split(en_key: str, zh_val: str, en_set: set, en_to_zh: dict):
    """
    尝试将 EN键 拆分为 2 或 3 段，验证各段 ZH 的拼接是否等于 zh_val。
    返回 (matched, method, parts_en, parts_zh, seps)。
    """
    words = en_key.split()

    # 2段：空格词边界
    for i in range(1, len(words)):
        A, B = ' '.join(words[:i]), ' '.join(words[i:])
        if A in en_set and B in en_set:
            Az, Bz = en_to_zh[A], en_to_zh[B]
            for sep in SEPS:
                if Az + sep + Bz == zh_val:
                    return True, "EN-2", [A, B], [Az, Bz], [sep]

    # 2段：EN键本身含 " - " 分隔符
    if ' - ' in en_key:
        A, _, B = en_key.partition(' - ')
        if A in en_set and B in en_set:
            Az, Bz = en_to_zh[A], en_to_zh[B]
            for sep in SEPS:
                if Az + sep + Bz == zh_val:
                    return True, "EN-2", [A, B], [Az, Bz], [sep]

    # 3段：空格词边界
    if len(words) >= 3:
        for i in range(1, len(words)):
            A = ' '.join(words[:i])
            if A not in en_set:
                continue
            Az = en_to_zh[A]
            for j in range(i + 1, len(words)):
                B, C = ' '.join(words[i:j]), ' '.join(words[j:])
                if B in en_set and C in en_set:
                    Bz, Cz = en_to_zh[B], en_to_zh[C]
                    for s1, s2 in product(SEPS, SEPS):
                        if Az + s1 + Bz + s2 + Cz == zh_val:
                            return True, "EN-3", [A, B, C], [Az, Bz, Cz], [s1, s2]

    return False, "", [], [], []


def detect_one_pass(glossary: dict, protected_keys: set) -> list:
    """单轮复合条目检测，返回结果列表 [(key, zh, method, p_en, p_zh, seps)]。"""
    en_set = set(glossary.keys())
    zh_set = frozenset(glossary.values())
    can    = make_can_decompose(zh_set)

    results = []
    seen    = set()

    for key, zh in glossary.items():
        if key in protected_keys or key in HARD_PROTECT or key in seen:
            continue

        matched, method, p_en, p_zh, seps = try_en_split(key, zh, en_set, glossary)
        if matched:
            results.append((key, zh, method, p_en, p_zh, seps))
            seen.add(key)
            continue

        if zh_is_compound(zh, can):
            results.append((key, zh, "ZH-rec", [], [], []))
            seen.add(key)

    return results


# ─── 主函数 ────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("术语表复合条目清洗")
    print(f"运行时间：{datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 60)

    glossary     = load_glossary(GLOSSARY_PATH)
    all_keys     = list(glossary.keys())
    pivot        = all_keys.index(PROTECTED_KEY)
    protected    = set(all_keys[:pivot + 1])
    total_before = len(glossary)

    print(f"\n读入：{total_before} 条（保护区 {len(protected)}，自动区 {total_before - len(protected)}）")

    # ── 步骤 1：换行符处理 ───────────────────────────────────
    print("\n[1] 换行符条目处理...")
    glossary, nl = handle_newline_entries(glossary, protected)
    print(f"    移除 EN\\n 复合：{nl['removed']}  新增独立术语：{nl['added']}  归一化 ZH\\n：{nl['zh_fixed']}")
    if nl['conflicts']:
        print(f"    ZH冲突（已跳过，保留现有）：{len(nl['conflicts'])} 条")

    # ── 步骤 2：编号变体移除 ─────────────────────────────────
    print("\n[2] 编号变体移除...")
    glossary, numbered_removed = remove_numbered_variants(glossary, protected)
    print(f"    移除：{len(numbered_removed)} 条")
    for key, zh, base, base_zh, num in sorted(numbered_removed)[:10]:
        print(f"      {key!r} → {zh!r}  (base={base!r}→{base_zh!r})")
    if len(numbered_removed) > 10:
        print(f"      ... 还有 {len(numbered_removed)-10} 条")

    # ── 步骤 3：等级变体移除（+/++）──────────────────────────
    print("\n[3] 等级变体移除（+/++）...")
    glossary, tier_removed = remove_tier_variants(glossary, protected)
    print(f"    移除：{len(tier_removed)} 条")
    for key, zh, base_en, base_zh, suffix in sorted(tier_removed)[:10]:
        print(f"      {key!r} → {zh!r}  (base={base_en!r}→{base_zh!r})")
    if len(tier_removed) > 10:
        print(f"      ... 还有 {len(tier_removed)-10} 条")

    # ── 步骤 4：序数词变体移除 ───────────────────────────────
    print("\n[4] 序数词变体移除...")
    glossary, ordinal_removed, ordinal_added = remove_ordinal_variants(glossary, protected)
    print(f"    移除：{len(ordinal_removed)} 条  新增基础术语：{len(ordinal_added)} 条")
    for base_en, base_zh in ordinal_added:
        print(f"      [新增] {base_en!r} → {base_zh!r}")
    for key, zh, base_en, base_zh, ord_w, ord_zh in sorted(ordinal_removed):
        print(f"      {key!r} → {zh!r}  (base={base_en!r}→{base_zh!r}，序数={ord_w}→{ord_zh})")

    # ── 步骤 5a：EN超过5词删除 ────────────────────────────────────
    print("\n[5a] EN超过5词条目删除...")
    glossary, long_removed = remove_long_en_entries(glossary, protected)
    print(f"    移除：{len(long_removed)} 条")
    for key, zh in sorted(long_removed)[:10]:
        print(f"      [{len(key.split())}词] {key!r} → {zh!r}")
    if len(long_removed) > 10:
        print(f"      ... 还有 {len(long_removed)-10} 条")

    # ── 步骤 5b：EN含/符号处理 ────────────────────────────────────
    print("\n[5b] EN含/符号条目处理...")
    glossary, slash_removed, slash_added = handle_slash_entries(glossary, protected)
    print(f"    删除：{len(slash_removed)} 条  拆分新增：{len(slash_added)} 条")
    for key, zh in sorted(slash_removed):
        print(f"      del {key!r} → {zh!r}")
    for en, zh in slash_added:
        print(f"      add {en!r} → {zh!r}")

    # ── 步骤 6：核心词包含检测 ────────────────────────────────
    print(f"\n[6] 核心词包含检测（前{N_CORE}条）...")
    glossary, core_removed = remove_protected_compounds(glossary, N_CORE)
    by_mode = {'EN+ZH': 0, 'EN仅': 0, 'ZH仅': 0}
    for _, _, he, hz in core_removed:
        if he and hz: by_mode['EN+ZH'] += 1
        elif he:      by_mode['EN仅']  += 1
        else:         by_mode['ZH仅']  += 1
    print(f"    移除：{len(core_removed)} 条  "
          f"（EN+ZH:{by_mode['EN+ZH']}  EN仅:{by_mode['EN仅']}  ZH仅:{by_mode['ZH仅']}）")
    for en, zh, he, hz in sorted(core_removed)[:10]:
        tag = f"EN={he!r}" if he else f"ZH={hz!r}"
        print(f"      [{tag}] {en!r} -> {zh!r}")
    if len(core_removed) > 10:
        print(f"      ... 还有 {len(core_removed)-10} 条")

    # ── 步骤 7：ZH首字前缀去重 ──────────────────────────────
    print(f"\n[7] ZH首字前缀去重（前缀≥{3}汉字，范围：第{N_CORE}条之后）...")
    glossary, prefix_removed = remove_zh_prefix_duplicates(glossary, N_CORE)
    print(f"    移除：{len(prefix_removed)} 条")
    for en, zh, prefix, kept_en in sorted(prefix_removed, key=lambda x: x[2])[:10]:
        print(f"      [{prefix}] {en!r} -> {zh!r}  (保留: {kept_en!r})")
    if len(prefix_removed) > 10:
        print(f"      ... 还有 {len(prefix_removed)-10} 条")

    # ── 步骤 8：复合条目迭代检测 ─────────────────────────────
    print("\n[8] 复合条目检测（迭代至收敛）...")
    all_results   = []
    total_removed = 0
    iteration     = 0

    while True:
        iteration += 1
        results = detect_one_pass(glossary, protected)
        if not results:
            print(f"    第{iteration}轮：0 条，已收敛。")
            break

        by_m = {}
        for r in results:
            by_m.setdefault(r[2], []).append(r)
        detail = "  ".join(f"{m}:{len(rs)}" for m, rs in sorted(by_m.items()))
        print(f"    第{iteration}轮：{len(results)} 条  [{detail}]")

        remove = {r[0] for r in results}
        glossary = {k: v for k, v in glossary.items() if k not in remove}
        total_removed += len(remove)
        all_results.extend(results)

    # ── 保存 ────────────────────────────────────────────────
    save_glossary(GLOSSARY_PATH, glossary)

    print(f"\n{'='*60}")
    print(f"原始条目：{total_before}")
    print(f"  换行复合移除：{nl['removed']}  新增：{nl['added']}  ZH归一化：{nl['zh_fixed']}")
    print(f"  编号变体移除：{len(numbered_removed)}")
    print(f"  等级变体移除：{len(tier_removed)}")
    print(f"  序数词变体移除：{len(ordinal_removed)}  基础术语新增：{len(ordinal_added)}")
    print(f"  EN超过5词移除：{len(long_removed)}")
    print(f"  /符号删除：{len(slash_removed)}  拆分新增：{len(slash_added)}")
    print(f"  核心词包含移除：{len(core_removed)}")
    print(f"  ZH前缀去重移除：{len(prefix_removed)}")
    print(f"  组合复合移除：{total_removed}（共 {iteration-1} 轮检测）")
    print(f"最终条目：{len(glossary)}")
    print(f"词典已保存 → {GLOSSARY_PATH}")

    # ── 报告 ────────────────────────────────────────────────
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    by_m = {}
    for r in all_results:
        by_m.setdefault(r[2], []).append(r)

    lines = [
        "# 术语表复合条目清洗报告\n\n",
        f"> 生成时间：{ts}\n\n",
        "---\n\n## 概览\n\n",
        f"| 类别 | 数量 |\n|------|------|\n",
        f"| 原始条目 | {total_before} |\n",
        f"| 移除 EN\\n 复合 | {nl['removed']} |\n",
        f"| 新增独立术语 | {nl['added']} |\n",
        f"| 归一化 ZH\\n | {nl['zh_fixed']} |\n",
        f"| 移除编号变体 | {len(numbered_removed)} |\n",
        f"| 移除等级变体（+/++） | {len(tier_removed)} |\n",
        f"| 移除序数词变体 | {len(ordinal_removed)} |\n",
        f"| 新增序数词基础术语 | {len(ordinal_added)} |\n",
        f"| 移除EN超过5词条目 | {len(long_removed)} |\n",
        f"| 移除/符号条目 | {len(slash_removed)} |\n",
        f"| 拆分/符号新增条目 | {len(slash_added)} |\n",
        f"| 移除核心词包含条目 | {len(core_removed)} |\n",
        f"| 移除ZH前缀重复条目 | {len(prefix_removed)} |\n",
        f"| 移除组合复合（EN-2） | {len(by_m.get('EN-2', []))} |\n",
        f"| 移除组合复合（EN-3） | {len(by_m.get('EN-3', []))} |\n",
        f"| 移除组合复合（ZH-rec） | {len(by_m.get('ZH-rec', []))} |\n",
        f"| **最终条目** | **{len(glossary)}** |\n",
        "\n---\n\n## 移除的编号变体\n\n",
        "| EN键 | ZH值 | 基础术语 |\n|------|------|----------|\n",
    ]
    for key, zh, base, base_zh, num in sorted(numbered_removed):
        lines.append(f"| `{key[:55]}` | `{zh[:40]}` | `{base}`→`{base_zh}` |\n")

    lines += [
        "\n---\n\n## 移除的等级变体（+/++）\n\n",
        "| EN键 | ZH值 | 基础术语 |\n|------|------|----------|\n",
    ]
    for key, zh, base_en, base_zh, suffix in sorted(tier_removed):
        lines.append(f"| `{key[:55]}` | `{zh[:40]}` | `{base_en}`→`{base_zh}` |\n")

    if ordinal_removed:
        lines += [
            "\n---\n\n## 移除的序数词变体\n\n",
            "| EN键 | ZH值 | 基础术语 | 序数词 |\n|------|------|----------|--------|\n",
        ]
        for key, zh, base_en, base_zh, ord_w, ord_zh in sorted(ordinal_removed):
            lines.append(f"| `{key[:55]}` | `{zh[:40]}` | `{base_en}`→`{base_zh}` | {ord_w}→{ord_zh} |\n")
    if ordinal_added:
        lines += [
            "\n#### 新增序数词基础术语\n\n",
            "| EN键 | ZH值 |\n|------|------|\n",
        ]
        for base_en, base_zh in sorted(ordinal_added):
            lines.append(f"| `{base_en}` | `{base_zh}` |\n")

    lines += [
        "\n---\n\n## 移除的核心词包含条目\n\n",
        "| EN键 | ZH值 | EN命中 | ZH命中 |\n|------|------|--------|--------|\n",
    ]
    for en, zh, he, hz in sorted(core_removed):
        lines.append(f"| `{en[:50]}` | `{zh[:35]}` | {he or ''} | {hz or ''} |\n")

    lines += [
        "\n---\n\n## 移除的ZH前缀重复条目\n\n",
        "| EN键 | ZH值 | 共享前缀 | 保留条目 |\n|------|------|----------|----------|\n",
    ]
    for en, zh, prefix, kept_en in sorted(prefix_removed, key=lambda x: x[2]):
        lines.append(f"| `{en[:50]}` | `{zh[:35]}` | {prefix} | `{kept_en[:40]}` |\n")

    lines += [
        "\n---\n\n## 移除的组合复合条目\n\n",
        "| EN键 | ZH值 | 方法 | 分解路径 |\n|------|------|------|----------|\n",
    ]
    for key, zh, method, p_en, p_zh, seps in sorted(all_results):
        if method != "ZH-rec":
            path = " + ".join(f"`{e}`({z})" for e, z in zip(p_en, p_zh))
        else:
            path = "ZH递归分解"
        lines.append(f"| `{key[:50]}` | `{zh[:40]}` | {method} | {path[:60]} |\n")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"报告已保存 → {REPORT_PATH}")
    print("\n完成。")


if __name__ == "__main__":
    main()
