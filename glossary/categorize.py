#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""categorize.py - 给术语表分组：所属章（主）+ 类型（辅），并统计每个术语出现在哪些章节。

  python glossary/categorize.py

产出两个文件：
  glossary/categories.json   {术语: {"chap": 所属章, "cat": 类型, "by": 类型依据}}   入 git
      by / chap_by = "人工" → 手改过的，重跑不覆盖（用 term.py --set / --set-chap 改）。
      其余自动判定，重跑会重算。
  glossary/term_where.json   {术语: {出处: 次数}} + 章节标题               派生产物，不入 git

分组只是查找用的标签，不影响翻译：取批时术语表永远整份匹配，
剧情句里出现机制词照样命中。

所属章：见 source_label / home_chapter。

类型判定顺序（先命中先得）：
  1. 人工
  2. 英文 wiki 页面分类（先跑 fetch_wiki_categories.py）
  3. 名字规则（Assoc. / Family → 组织势力，Hall → 地点，Golden X → 道具 …）
  4. 游戏数据：术语恰好是某文件某字段的完整值（如 Skills*.json 的 name → 技能）
  5. wiki 的 Enemy Factions → 敌人与怪物（兜底）
  6. 未分类
判为「人物」但不是 wiki 角色、且正文里常以小写普通词出现的（father / thief），改判「称谓泛称」。

查询用根目录的 term.py。
"""

import collections
import hashlib
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from limbus.glossary import Glossary
from limbus.jsonio import load_json, save_json, setup_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
CATEGORIES = os.path.join(HERE, "categories.json")
WHERE = os.path.join(HERE, "term_where.json")
WIKI_CACHE = os.path.join(HERE, "wiki_categories_cache.json")
P_BASELINE = os.path.join(HERE, "p_story_baseline.json")

_P_BASELINE = None


def p_story_baseline():
    """2026-10-05 时已有的人格剧情文件名（不含 .json）。之后新增的不在表里，归第10章。"""
    global _P_BASELINE
    if _P_BASELINE is None:
        _P_BASELINE = set((load_json(P_BASELINE) or {}).get("files", []))
    return _P_BASELINE

MANUAL = "人工"
UNSORTED = "未分类"

# 类别及其展示顺序（term.py 按这个顺序列）
CATS = [
    "人物", "称谓泛称", "组织势力", "地点", "人格与EGO", "异想体与扭曲", "敌人与怪物",
    "技能", "被动", "战斗机制", "道具与饰品", "玩法与活动", "世界观设定", "系统UI", UNSORTED,
]

# ==================== 2. wiki 分类 → 类别 ====================
# 一个页面常有多个分类（Dead Rabbits = Syndicates + Enemy Factions），按本表从上到下取第一个。
# 异想体放最前：「Abnormality with E.G.O」也以 E.G.O 结尾，别被 EGO 规则抢走。
# Distortion / XX Abnormality Logs 放在人物后面：Kromer 这类扭曲过的角色首先是人物。
WIKI_RULES = [
    ("异想体与扭曲", lambda c: ("Abnormalit" in c and not c.endswith("Abnormality Logs"))
                              or c in ("Peccatulum", "Ordeal")),
    ("人格与EGO",   lambda c: c in ("Identities", "E.G.O") or "Identities" in c or c.startswith("E.G.O with")
                              or c.endswith(" E.G.O")),
    ("组织势力",    lambda c: c in ("Syndicates", "Wings", "Five Fingers", "Fixer Office", "Associations",
                              "Factions", "Workshops") or c.endswith(" Corp.")),
    ("人物",        lambda c: c == "Characters" or c.endswith(" Characters")),
    ("异想体与扭曲", lambda c: c == "Distortion" or c.endswith("Abnormality Logs")),
    ("地点",        lambda c: c == "Locations"),
    ("世界观设定",   lambda c: c in ("Lore", "Phenomena", "City Technology")),
    ("战斗机制",    lambda c: c == "Status Effect Pages" or c.endswith(" Affinity")),
    ("玩法与活动",   lambda c: c in ("Mirror Dungeon Events", "Events", "Dungeon", "Mirror Dungeons",
                              "Refraction Railway Lines", "Story Chapters")
                              or "Theme Pack" in c or c.startswith(("Season", "Intervallo", "Episode"))),
    ("敌人与怪物",   lambda c: c in ("Enemy", "Monster", "Monster Species", "Mutant", "Mutant Species",
                              "Boss Enemy", "Mermaid") or c.endswith(" Enemies")),
]
# 「Enemy Factions」= 战斗里遇到的敌方阵营（家具馆、快乐衣橱都在里面），不等于组织。
# 只在游戏数据和名字规则都判不出来时才用它兜底（见 classify）。
WIKI_FALLBACK = [("敌人与怪物", lambda c: c == "Enemy Factions")]

# ==================== 3. 游戏字段 → 类别 ====================
# 根目录文件：(文件名前缀, {字段: 类别})。前缀按顺序匹配，长的写前面。
ROOT_FIELDS = [
    ("Personalities",      {"title": "人格与EGO", "name": "人物"}),
    ("ScenarioModelCodes", {"name": "人物", "nickName": "人物"}),
    ("Egos",               {"name": "人格与EGO"}),
    ("Skills_Ego",         {"name": "人格与EGO"}),
    ("Passive_Ego",        {"name": "被动"}),
    ("AbnormalityGuides",  {"name": "异想体与扭曲"}),
    ("Skills",             {"name": "技能"}),
    ("Bufs",               {"name": "战斗机制"}),
    ("BattleKeywords",     {"name": "战斗机制"}),
    ("UnitKeyword",        {"name": "战斗机制"}),
    ("Passive",            {"name": "被动"}),         # 也覆盖 Passives*
    ("PanicInfo",          {"name": "战斗机制"}),
    ("MentalCondition",    {"name": "战斗机制"}),
    ("EGOgift",            {"name": "道具与饰品"}),
    ("Items",              {"name": "道具与饰品"}),
    ("UserTicket",         {"name": "道具与饰品"}),
    ("IAPProduct",         {"name": "道具与饰品"}),
    ("DungeonStartBuffs",  {"name": "道具与饰品"}),
    ("Enemies",            {"name": "敌人与怪物"}),
    ("DungeonArea",        {"name": "地点"}),
    *[(p, {"name": "玩法与活动", "title": "玩法与活动"}) for p in (
        "AbEvents", "ActionEvents", "ChoiceEvent", "StageNode", "DungeonNode", "StageChapterText",
        "Railway", "MirrorDungeon", "StoryDungeon", "BattlePass", "SeasonTitle", "Walpu", "StoryTheater",
    )],
    ("BattleSpeechBubble", {}),
    ("BattleAnnouncer",    {}),
    ("",                   {"name": "系统UI", "title": "系统UI"}),   # 其余根目录文件兜底
]

RPG_FIELDS = [
    ("rpg-loc-npc",       {"displayName": "人物"}),
    ("rpg-loc-swarm-mob", {"displayName": "敌人与怪物"}),
    ("rpg-loc-location",  {"text": "地点"}),
    ("rpg-loc-item",      {"displayName": "道具与饰品"}),
    ("rpg-loc-quest",     {"title": "玩法与活动", "displayName": "玩法与活动"}),
    ("rpg-loc-dialogue",  {"speaker": "人物"}),
]

STORY_FIELDS = {"teller": "人物", "place": "地点", "title": "组织势力"}
# StoryData 的 title 是说话人的所属（Kromer | Nagel und Hammer、Sonya | Yurodivy），
# 少数是职位（Yuri | Grade 8 Fixer、Gregor | Night Awls Capitano）→ 称谓泛称
TITLE_ROLE_RE = re.compile(
    r"\b(Captain|Capitano|Capo|Fixer|Agent|Nursefather|Apprentice|Owner|Guide|Boss|Hierarch|Member"
    r"|Leader|Director|Chief|Manager|Staff|Researcher|Employee|Proxy|Soldier|Knight|Brother|Sister"
    r"|Father|Mother|Elder|Heir|Successor|Assistant|Interviewer)s?\b[\s\dⅠ]*$")

# 同一个词在游戏里多种身份时的优先级
# 组织势力（剧情 title）排在人物前：「Jia Family」既当说话人也当所属，首先是组织。
GAME_PRIORITY = ["异想体与扭曲", "人格与EGO", "组织势力", "人物", "称谓泛称", "地点", "技能", "战斗机制", "被动",
                 "道具与饰品", "敌人与怪物", "玩法与活动", "系统UI"]

# 这些游戏证据只说明「出现在说话人/标题栏」，名字规则可以推翻
WEAK_GAME_KINDS = {"人物", "称谓泛称", "地点", "玩法与活动", "系统UI"}

# ==================== 4. 名字规则 ====================
NAME_RULES = [
    # 词尾是句号（Assoc.）时 \b 不成立，所以右边界用 (?!\w)
    # 关键词要在词尾（可带方位）：Cinq Assoc. West 算，Xue Family Captain 不算
    ("组织势力", re.compile(r"\b(Assoc\.|Association|Office|Corp\.|Syndicate|Family|Clan|Workshop|Atelier"
                           r"|Gang|Squad|Court|Church|Alliance|Cult)(?:\s+(?:East|West|South|North))?$")),
    ("地点",     re.compile(r"\b(District|Nest|Backstreets?|Outskirts|Temple|Hall|Sector)\b|\b\d+F\b")),
    ("道具与饰品", re.compile(r"^Golden (?!Bough)\w+$")),   # 第10章材料：Golden Resin / Golden Yarn …
]

# 这些字段里的内容不是人读的正文，不统计出处
SKIP_LEAVES = config.NEVER_TRANSLATE | {"key", "abilityID"}


def field_kind(subdir, fn, leaf):
    """(子目录, 去掉 EN_ 的文件名, 叶子字段名) → 类别 或 None"""
    if subdir == "StoryData":
        return STORY_FIELDS.get(leaf)
    table = RPG_FIELDS if subdir == "RPGSystem" else ROOT_FIELDS if subdir == "" else None
    if table is None:
        return None
    for prefix, fields in table:
        if fn.startswith(prefix):
            return fields.get(leaf)
    return None


def source_label(subdir, fn):
    """文件 → 出处标签。以「第N章」「间章N.5」开头的标签参与所属章判定（见 home_chapter）。

    文件名 → 章节（按各系列文件里的地名核对过）：
      S1019B      主线第10章第19节（S103B = 第1章第3节；S999x 是特殊篇）
      3D306B      第3章的副本/支线剧情（1D=4区、3D=11区、5D=裴廓德号、8D=红园…）
      E302B       间章3.5（E{N}xx = 间章 N.5：E3 地狱鸡、E6 WARP 快车、E9 绞丝结线）
      ES300A      间章8.5（全在大观园）
      E0xx        零散活动
      P10715      人格剧情（按罪人编号，不对应章节）；不在 p_story_baseline.json 里的 = 第10章·人格剧情
      PC12B       联动剧情
      RPGSystem   第10章（西西弗百货）
      *-a1c10p1   第10章（机制文本等）
    """
    stem = fn[:-5] if fn.endswith(".json") else fn
    m = re.search(r"a\d+c(\d+)", stem)
    unit = code_unit(m.group(1)) if m else None
    if subdir == "StoryData":
        m = re.match(r"S(\d+)", stem)
        if m:
            d = m.group(1)
            return "主线·特殊篇" if d.startswith("999") else f"第{int(d[:-2])}章"
        m = re.match(r"(\d+)D", stem)
        if m:
            return f"第{m.group(1)}章·副本"
        if stem.startswith("ES"):
            return "间章8.5"
        m = re.match(r"E(\d)", stem)
        if m:
            return "其他活动" if m.group(1) == "0" else f"间章{m.group(1)}.5"
        if stem.startswith("PC"):
            return "联动剧情"
        if stem.startswith("P"):
            # 基线（p_story_baseline.json）之后新增的人格剧情属第10章（N公司/西西弗百货）
            return "人格剧情" if stem in p_story_baseline() else "第10章·人格剧情"
        return "其他剧情"
    if subdir == "RPGSystem":
        return "第10章·RPG"
    if subdir in ("PersonalityVoiceDlg", "EGOVoiceDig"):
        return "语音"
    if subdir == "BattleAnnouncerDlg":
        return "战斗播报"
    if subdir == "BgmLyrics":
        return "歌词"
    if subdir:
        return subdir
    kind = field_kind("", stem, "name")
    if stem.startswith("BattleSpeechBubble"):
        base = "战斗气泡"
    elif kind in ("技能", "被动", "战斗机制", "敌人与怪物", "人格与EGO", "异想体与扭曲"):
        base = "机制文本"
    elif kind == "道具与饰品":
        base = "道具饰品"
    elif kind == "玩法与活动":
        base = "玩法关卡"
    elif stem.startswith(("Personalities", "ScenarioModelCodes")):
        base = "角色资料"
    else:
        base = "系统UI"
    # 带章节号的放前面，才能参与所属章判定
    return f"{unit_name(unit)}·{base}" if unit is not None else base


_CODE_TABLE = None


def code_unit(code):
    """文件名里 a1c<code> 的 code → 章节单位。
      10      → 10            （第10章）
      951     → 5.5           （9N1 = 间章 N.5：951 圣诞礼物工厂、971 LCB 体检）
      9114    → 7.5           （查 StageChapterText 的 id：chapter_p_9114 = 间章V = 7.5；
                               表里没有的 9115 取相邻的较小 id）
    """
    global _CODE_TABLE
    if len(code) <= 2:
        return int(code)
    if re.fullmatch(r"9\d1", code):
        return int(code[1]) + 0.5
    if _CODE_TABLE is None:
        _CODE_TABLE = {}
        for it in (load_json(os.path.join(config.EN_ROOT, "EN_StageChapterText.json")) or {}).get("dataList", []):
            m = re.search(r"_(\d+)$", str(it.get("id", "")))
            num = str(it.get("chapterNumber") or "")
            if m and re.fullmatch(r"\d+(\.5)?", num):
                _CODE_TABLE[int(m.group(1))] = float(num) if "." in num else int(num)
    lower = [c for c in _CODE_TABLE if c <= int(code) and c // 100 == int(code) // 100]
    return _CODE_TABLE[max(lower)] if lower else None


# ==================== 所属章 ====================
# 所属章 = 在主线/间章里出现次数最多的那一章。
# 分散在 3 章以上、且最多的那章占不到一半的（罪人名、都市常用词），归「通用」。
# 主线/间章里一次都没出现的，按其余出处归到下面几组。
GENERAL = "通用"
CHAP_OTHER = ["人格剧情", "联动剧情", "其他剧情", "机制与系统", "未出现"]
_UNIT_RE = re.compile(r"^(?:第(\d+)章|间章(\d+)\.5)")


def chap_unit(label):
    """出处标签 → 章节单位（10 / 8.5），不是章节则 None"""
    m = _UNIT_RE.match(label)
    if not m:
        return None
    return int(m.group(1)) if m.group(1) else int(m.group(2)) + 0.5


def unit_name(u):
    return f"第{u}章" if isinstance(u, int) else f"间章{u}"


def home_chapter(where):
    units = collections.Counter()
    for label, n in where.items():
        u = chap_unit(label)
        if u is not None:
            units[u] += n
    if units:
        (top, n), total = units.most_common(1)[0], sum(units.values())
        # 第10章 + RPG 文本量特别大，罪人名也会在那里过半，所以铺满 8 章以上的直接算通用
        if len(units) >= 8:
            return GENERAL
        if n * 2 >= total or len(units) <= 2:
            return unit_name(top)
        return GENERAL
    labels = set(where)
    if "人格剧情" in labels:
        return "人格剧情"
    if "联动剧情" in labels:
        return "联动剧情"
    if labels & {"其他活动", "其他剧情", "主线·特殊篇"}:
        return "其他剧情"
    return "机制与系统" if labels else "未出现"


def chapter_titles():
    """{"第10章": "凝视之下", "间章6.5": "时间杀人时间 / WARP快车谋杀案"}，取官方中文，缺的用英文。"""
    out = {}
    for root, prefix in ((config.EN_ROOT, "EN_"), (config.ZH_ROOT, "")):   # 中文后读，覆盖英文
        found = collections.defaultdict(list)
        for f in sorted(os.listdir(root)) if os.path.isdir(root) else []:
            if not (f.startswith(prefix + "StageChapterText") and f.endswith(".json")):
                continue
            for it in (load_json(os.path.join(root, f)) or {}).get("dataList", []):
                num, title = str(it.get("chapterNumber") or ""), (it.get("chaptertitle") or "").replace("\n", " ")
                if not re.fullmatch(r"\d+(\.5)?", num) or not title:
                    continue
                key = unit_name(float(num) if "." in num else int(num))
                if title not in found[key]:
                    found[key].append(title)
        out.update({k: " / ".join(v) for k, v in found.items()})
    return out


def chap_sort_key(chap):
    """章节组的排序：第1章, 间章1.5 … 第10章, 通用, 人格剧情 …"""
    m = re.match(r"^(?:第(\d+)章|间章(\d+)\.5)$", chap)
    if m:
        return (0, int(m.group(1)) if m.group(1) else int(m.group(2)) + 0.5)
    rest = [GENERAL] + CHAP_OTHER
    return (1, rest.index(chap) if chap in rest else 99)


def iter_leaves(node, leaf=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from iter_leaves(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from iter_leaves(v, leaf)
    elif isinstance(node, str):
        yield leaf, node


def scan_game(gloss):
    """扫全部 EN 文件。返回
        exact:  {小写完整值: Counter[(类别, "文件前缀.字段")]}
        where:  {术语键: Counter[出处]}
        lower:  {术语键: [小写出现次数, 总次数]}   只统计正文字段
    """
    exact = collections.defaultdict(collections.Counter)
    where = collections.defaultdict(collections.Counter)
    lower = collections.defaultdict(lambda: [0, 0])
    prose = {"content", "dlg", "text", "desc", "description", "eventDesc", "flavor"}
    n_files = 0
    for dirpath, _, files in os.walk(config.EN_ROOT):
        subdir = os.path.relpath(dirpath, config.EN_ROOT)
        subdir = "" if subdir == "." else subdir.replace("\\", "/")
        for f in files:
            if not (f.startswith("EN_") and f.endswith(".json")):
                continue
            fn = f[3:]
            data = load_json(os.path.join(dirpath, f))
            if not isinstance(data, dict):
                continue
            n_files += 1
            label = source_label(subdir, fn)
            parts = fn[:-5].split("-")
            family = "-".join(parts[:3]) if fn.startswith("rpg-") else parts[0]
            for leaf, value in iter_leaves(data.get("dataList", [])):
                if leaf in SKIP_LEAVES or not re.search(r"[A-Za-z]", value):
                    continue
                kind = field_kind(subdir, fn, leaf)
                if kind:
                    norm = " ".join(value.split())   # 「Cinq East\nSection 3」
                    if subdir == "StoryData" and leaf == "title" and TITLE_ROLE_RE.search(norm):
                        kind = "称谓泛称"
                    exact[norm.lower()][(kind, f"{family}.{leaf}")] += 1
                for _, key, _, matched in gloss.finditer(value):
                    where[key][label] += 1
                    if leaf in prose:
                        lc = lower[key]
                        lc[1] += 1
                        # 整串小写才算普通词；开头冠词不算（「the Church of Gears」是专名）
                        body = re.sub(r"^(?:the|a|an)\s+", "", matched, flags=re.I)
                        if body == body.lower():
                            lc[0] += 1
    return exact, where, lower, n_files


def classify(term, wiki, exact, lower):
    bare = term.lstrip("!")
    info = wiki.get(bare) or {}
    for cat, pred in WIKI_RULES:
        hit = next((c for c in info.get("cats", []) if pred(c)), None)
        if hit:
            return cat, f"wiki:{hit}"

    kinds = exact.get(bare.lower())
    best = min(kinds, key=lambda kv: (GAME_PRIORITY.index(kv[0]), -kinds[kv])) if kinds else None

    # 名字规则压过「弱」游戏证据：「Wang Family」在剧情里当说话人出现，但它首先是个组织。
    # 游戏数据明确是技能/被动/机制名的（For the Family、Syndicate Payback）不压。
    # 剧情 title 判出的组织也算弱证据（District 11 也会出现在 title 里）
    if best is None or best[0] in WEAK_GAME_KINDS or best[1].endswith(".title"):
        for cat, rx in NAME_RULES:
            if rx.search(bare):
                return cat, f"rule:{rx.search(bare).group(0)}"

    if best:
        cat, where_ = best
        if cat == "组织势力" and where_.endswith(".title"):
            # 剧情 title 有时是地名（La Manchaland 也出现在 place 栏）
            place = next((w for k, w in kinds if k == "地点"), None)
            if place:
                return "地点", f"game:{place}"
        if cat in ("人物", "组织势力"):
            # 正文里常以小写普通词出现的（father / bodyguard / stranger）是泛称，不是专名
            lc, total = lower.get(term, (0, 0))
            if lc >= 2 and lc >= total * 0.2:
                return "称谓泛称", f"game:{where_}+正文小写{lc}/{total}"
        return cat, f"game:{where_}"

    for cat, pred in WIKI_FALLBACK:
        hit = next((c for c in info.get("cats", []) if pred(c)), None)
        if hit:
            return cat, f"wiki:{hit}"
    return UNSORTED, ""


def glossary_digest():
    with open(config.GLOSSARY, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:12]


def main():
    setup_stdout()
    t0 = time.time()
    gloss = Glossary()
    terms = list(gloss.terms)
    wiki = load_json(WIKI_CACHE) or {}
    if not wiki:
        print("[提示] 没有 wiki 缓存，只按游戏数据和规则分类。先跑 glossary/fetch_wiki_categories.py 效果更好。")
    old = {k: v for k, v in (load_json(CATEGORIES) or {}).items() if not k.startswith("_")}

    print(f"扫描游戏文件 {config.EN_ROOT} …")
    exact, where, lower, n_files = scan_game(gloss)
    print(f"  {n_files} 个文件，{time.time() - t0:.0f}s")

    out = {"_说明": "chap=所属章，cat=类型。by / chap_by 为「人工」的是手改的，重跑 categorize.py 不覆盖"
                    "（用 term.py --set / --set-chap 改）。"
                    f"可用类型：{' / '.join(CATS)}"}
    by_src = collections.Counter()
    changed = []
    for t in terms:
        prev = old.get(t) or {}
        if prev.get("by") == MANUAL:
            cat, by = prev["cat"], MANUAL
        else:
            cat, by = classify(t, wiki, exact, lower)
            if prev and prev.get("cat") != cat:
                changed.append((t, prev.get("cat"), cat))
        by_src[by.split(":")[0] if by else UNSORTED] += 1
        entry = {"chap": home_chapter(where.get(t, {})), "cat": cat, "by": by}
        if prev.get("chap_by") == MANUAL:
            entry.update(chap=prev["chap"], chap_by=MANUAL)
        out[t] = entry
    dropped = [k for k, v in old.items() if k not in gloss.terms]
    save_json(CATEGORIES, out)

    save_json(WHERE, {
        "_glossary": glossary_digest(),
        "_built": time.strftime("%Y-%m-%d %H:%M"),
        "_chapters": chapter_titles(),
        "terms": {t: dict(where[t].most_common()) for t in terms if where.get(t)},
    })

    entries = [v for k, v in out.items() if not k.startswith("_")]
    chaps = collections.Counter(v["chap"] for v in entries)
    print(f"\n完成 → {os.path.relpath(CATEGORIES, config.BASE_DIR)}（{len(terms)} 条）")
    print("按所属章：" + "，".join(f"{c} {chaps[c]}" for c in sorted(chaps, key=chap_sort_key)))
    counts = collections.Counter(v["cat"] for v in entries)
    print("按类型：" + "，".join(f"{c} {counts[c]}" for c in CATS if counts.get(c)))
    print("类型依据：" + "，".join(f"{k} {n}" for k, n in by_src.most_common()))
    unseen = sum(1 for t in terms if not where.get(t))
    print(f"出处索引 → {os.path.relpath(WHERE, config.BASE_DIR)}；当前英文文本里一次都没出现的术语 {unseen} 条")
    if changed:
        print(f"\n与上次相比改判 {len(changed)} 条：")
        for t, a, b in changed[:30]:
            print(f"  {t}: {a} → {b}")
    if dropped:
        print(f"\n术语表里已删除、从分类表移除 {len(dropped)} 条：{', '.join(dropped[:20])}")


if __name__ == "__main__":
    main()
