#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""config.py - 全局配置：路径、翻译范围、字段规则。

所有脚本从这里取配置，不再各自硬编码绝对路径。
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 游戏目录 ====================

EN_ROOT = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en"
KR_ROOT = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\kr"
ZH_ROOT = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN"

# ==================== 工作区 ====================

OUT_DIR      = os.path.join(BASE_DIR, "out")
WORK_ROOT    = os.path.join(BASE_DIR, "Workplace", "translated")  # apply.py 产出，手动拷进游戏
PROGRESS     = os.path.join(OUT_DIR, "progress.json")             # 我们自己的译文库（唯一真相）
SNAPSHOT     = os.path.join(OUT_DIR, "snapshot.json")             # 上次 accept 的 EN 原文指纹
IGNORE       = os.path.join(OUT_DIR, "ignore.json")                # 基线里就没翻的条目，永久跳过
STATE        = os.path.join(OUT_DIR, "state.json")                # scan 产出的全量状态
# 多 agent 并行：每个 agent 一个 slot（环境变量 LIMBUS_SLOT，默认 a），
# 批次文件各放各的目录，互不覆盖。progress/state/snapshot 仍然是全局唯一真相。
SLOT         = (os.environ.get("LIMBUS_SLOT") or "a").strip() or "a"
SLOT_DIR     = os.path.join(OUT_DIR, "slots", SLOT)
PENDING      = os.path.join(SLOT_DIR, "batch_pending.json")
ANSWERS      = os.path.join(SLOT_DIR, "batch_answers.json")
APPLY_STATE  = os.path.join(OUT_DIR, "apply_state.json")           # 每个输出文件上次 apply 时的译文指纹，未变则不重写
CHANGES_DIR  = os.path.join(OUT_DIR, "changes")
GLOSSARY     = os.path.join(BASE_DIR, "glossary", "glossary.json")

# ==================== 翻译范围（tier 0：现在就翻） ====================
# scope 是 key 的第一段。子目录用目录名，根目录文件用 "_root"。

ROOT_SCOPE = "_root"

# (scope, 相对 EN_ROOT 的子目录 或 None)
TIER0_DIRS = [
    ("StoryData",          "StoryData"),
    ("PersonalityVoiceDlg", "PersonalityVoiceDlg"),
    ("RPGSystem",          "RPGSystem"),  # 未发布的 RPG 玩法：floor-1~4/b1/b2/route-a/theater 对话、NPC、任务、物品、地点文本
]

# 根目录下点名要翻的文件（ZH 侧文件名，不带 EN_ 前缀）
TIER0_ROOT_FILES = [
    "ScenarioModelCodes-AutoCreated.json",
    "BattleSpeechBubbleDlg.json",
    "RPGSuicideBoxUI.json",  # RPG 自杀贩卖机 UI
]
# 气泡文件有多个变体（BattleSpeechBubbleDlg2.json 等），按前缀自动纳入
TIER0_ROOT_PREFIXES = [
    "BattleSpeechBubbleDlg",
]

# 机制文本（技能/被动/Buff/关键词）。单独一个 scope，因为这里的 [Sinking] 这类
# 单词方括号是关键词 ID，必须原样保留英文 —— 与剧情里的音效标注规则相反。
MECH_SCOPE = "_mech"
TIER0_MECH_FILES = [
    "Skills_Abnormality-BossRaid.json",
    "Passives-BossRaid.json",
    "Bufs-BossRaid.json",
    "BattleKeywords-BossRaid.json",
    "BossRaidUI-4.json",
    # a1c10p1（第10章）技能文本，官方中文尚未跟进
    "Skills_Abnormality-a1c10p1.json",
    "Skills_Enemy-a1c10p1.json",
    "Skills_personality-04.json",
    "Skills_personality-08.json",
    # a1c10p2（第10章后续）RPG 技能、敌人与机制文本
    "Skills_Abnormality-a1c10p2.json",
    "Skills_Assist-a1c10p2.json",
    "Passives_Abnormality-a1c10p2.json",
    "Passives_Assist-a1c10p2.json",
    "Bufs-a1c10p2.json",
    "BattleKeywords-a1c10p2.json",
    "Enemies-a1c10p2.json",
    "PanicInfo-a1c10p2.json",
]

# ==================== 双语输出 ====================
# apply.py 在译文后面贴上英文原文：中文译文 + 换行 + 一个空格 + 英文原文。
# 这一步由脚本机械拼接，不经过 LLM —— progress.json 里存的始终是纯中文译文。
BILINGUAL = True
BILINGUAL_JOIN = "\n "


# ==================== 字段规则 ====================

# 只有白名单里的字段会被翻译。
TRANSLATE_FIELDS = {
    "content",   # 对话正文 / 旁白
    "dlg",       # 语音台词、气泡台词
    "title",     # 章节名 / 场景标题
    "teller",    # 说话人显示名
    "place",     # 地点名
    "desc",      # 语音条目说明（PersonalityVoiceDlg 为英文，气泡文件为韩文→自动跳过）
    "name",      # ScenarioModelCodes / 技能名 / Buff 名
    "nickName",  # ScenarioModelCodes
    "summary",   # Buff / 关键词的简短说明
    "flavor",    # 被动的风味文本
    # ---- RPGSystem 专用（条目用 "key" 当 id，不是扁平 content/title 结构）----
    "text",         # 对话行 texts[].text / 选项文本 / UI 提示 / 地点名
    "displayName",  # NPC / 物品的显示名
    "description",  # 物品说明 / 任务说明
    "speaker",      # 对话行 texts[].speaker，这里是英文显示名（不是 StoryData 那种韩文内部ID），要翻
    "statText",     # 物品词条效果说明
    "goalDescription1", "goalDescription2", "goalDescription3",
    "goalDescription4", "goalDescription5", "goalDescription6",  # 任务步骤目标说明
}

# 明确不翻的字段（列出来是为了自我说明，逻辑上白名单已经排除它们）
NEVER_TRANSLATE = {
    "id",
    "model",     # StoryData 里的立绘/角色标识，官方 ZH 保持韩文原样
    "d",
    "level", "voicefile", "voiceFile", "personalityid", "usage",
}

# [SingleWord] 方括号当作「机制关键词 ID，不翻」的 scope。
# 剧情/语音里 [Activating] 这类是音效标注，官方译成 [启动声]，所以 tier0 全部不在此列。
# 以后做 Skills / Passives / BattleKeywords 时把对应 scope 加进来。
KEYWORD_BRACKET_SCOPES = {MECH_SCOPE}

# 只有这些字段里的 [Xxx] 才是关键词 ID。
# name 字段里的方括号是名字的一部分，要翻：
#   'Shade of Reflection [Rouge]' → '映射[红色]'
#   'Sword of the Homeland [Sal] - Reassume Stance' → '本国剑[肉]-重整态势'
KEYWORD_BRACKET_FIELDS = {"desc", "summary", "flavor"}


def keyword_brackets(scope: str, field: str = None) -> bool:
    if scope not in KEYWORD_BRACKET_SCOPES:
        return False
    if field is None:
        return True
    leaf = field.split(".")[-1].split("[")[0]
    return leaf in KEYWORD_BRACKET_FIELDS


# 字段类型 → 给译者的提示
FIELD_HINT = {
    "content":  "对话或旁白正文。保持角色语气与戏剧张力，自然口语，勿书面化。",
    "dlg":      "角色台词。短促有力，符合该人格的说话方式。",
    "title":    "标题/章节名/场景名。简洁。",
    "teller":   "说话人显示名。人名或身份称谓，从术语表取，保持全局一致。",
    "place":    "地点名。",
    "desc":     "条目说明（如“获得人格”“早间问候”），简短名词短语。",
    "name":     "名称（角色名 / 技能名 / Buff 名）。机制文本里的技能名要简洁有力。",
    "summary":  "机制说明的简短版，与 desc 用词保持一致。",
    "flavor":   "风味文本，可以有文学性，但不要脱离原意。",
    "nickName": "角色别名/称号。",
}

