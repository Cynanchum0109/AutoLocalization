#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""格式码识别与校验。

标签名是**穷举硬编码**的，不做模式推断。清单来自把整个 Localize/en 与
LLC_zh-CN 扫一遍统计出的全部标签名（见 FORMAT_TAGS.md）。
发现新标签就往下面的元组里加一条，不要改成正则通配。

为什么必须穷举：游戏用尖括号当心声/通讯的引号，`<Clash>`、`<Bloodfiend>`、
`<Uh...>` 都是要翻译的台词。用 `<[^>]+>` 通配会把它们当标签保护起来，
译者就翻不动了。只有在下面这张表里的名字才是真标签。
"""

import re
from collections import Counter

# ==================== 硬编码的标签清单 ====================

# 强标记：丢一个游戏就显示错乱 → 数量不符拒绝合批
STRICT_TAGS = (
    "color",     # <color=#dc3531>…</color>  着色
    "style",     # <style=…>                 样式预设
    "mark",      # <mark=…>                  高亮
    "noparse",   # <noparse>…</noparse>      禁止解析
)

# 排版标记：**一个不许丢，也不许自己加**。
#   官方译者会随手丢 <i>（tier0 实测丢弃 590 处，中文不用斜体强调），
#   我们不学 —— 丢失是硬错误。自作主张新增同样是硬错误。
#   唯一的例外见 ALLOWED_ADDED_TAGS。
SOFT_TAGS = (
    "i", "b", "u", "s",          # 斜体 / 粗体 / 下划线 / 删除线
    "size", "voffset", "width",  # 字号 / 垂直偏移 / 宽度
    "ruby",                      # 注音
    "link",                      # 链接
    "font",                      # 字体
)

# 允许译文比原文**多出**的排版标签，穷举。
#   目前只有良秀的注音：EN "Yoshihide..." → ZH "<ruby=Yoshihide>良秀</ruby>……"
#   开标签每多一个，就同时放行一个 </ruby> 闭合。
#   其余任何新增（<size> <voffset> <i> …）都算硬错误。
ALLOWED_ADDED_TAGS = (
    "<ruby=Yoshihide>",
)
ALLOWED_ADDED_CLOSER = "</ruby>"

# 运行时数值占位符，全部穷举（整个 Localize/en 只有这些形态）
PLACEHOLDERS = (
    "{}", "{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{0:F1}",
    "{n}", "{amount}", "{stack}", "{target}", "{targets}", "{affectedTarget}",
    "{conditions}", "{conditional}", "{reward}", "{buffName}", "{waveNum}",
    "{hpAmount}", "{mpAmount}",
)

# ==================== 由清单拼出的正则 ====================

def _tag_re(names):
    """匹配 <name> </name> <name=…> </name=…> 以及 <name attr=…> 三种写法。

    游戏里三种都有：<color=#fff>、</color=#fff>（畸形闭合）、
    <mark color=#ff000040>（属性带空格）。带空格那种必须要求后面有 "="，
    否则 <Mark, please...> 这类台词会被误判成标签。
    """
    return (r"</?(?:" + "|".join(names) +
            r")(?:=[^<>]*|\s+[A-Za-z-]+=[^<>]*)?>")

# 乱码序列：#&#(!@&$ 这种。不是标签，但官方也原样保留，算强标记。
_GARBLED = r"[#@$%&*!()^~]*[#@$&*^][#@$%&*!()^~]{3,}"

_PLACEHOLDER_RE = "|".join(re.escape(p) for p in PLACEHOLDERS)

# [Sinking] [WhenUse] 这类单个英文词的方括号：
#   机制文本里是关键词 ID（不译）；剧情/语音里是音效标注（要译，
#   如 [Activating] → [启动声]）。由 config.KEYWORD_BRACKET_SCOPES 决定。
_KEYWORD_BRACKET = r"\[[A-Za-z][A-Za-z0-9_]*\]"

KEYWORD_BRACKET_RE = re.compile(_KEYWORD_BRACKET)

_STRICT_BASE = _tag_re(STRICT_TAGS) + "|" + _PLACEHOLDER_RE + "|" + _GARBLED

STRICT_RE    = re.compile(_STRICT_BASE, re.IGNORECASE)
STRICT_KW_RE = re.compile(_STRICT_BASE + "|" + _KEYWORD_BRACKET, re.IGNORECASE)
SOFT_TAG_RE  = re.compile(_tag_re(SOFT_TAGS), re.IGNORECASE)

NEWLINE_RE = re.compile("\r\n|\n|" + re.escape(chr(92) + "n"))

# 不在标签表里的 <…> 就是当引号用的尖括号：内容要翻，尖括号保留
_ALL_TAGS = STRICT_TAGS + SOFT_TAGS
ANGLE_QUOTE_RE = re.compile(
    r"<(?![/])(?!(?:" + "|".join(_ALL_TAGS) + r")(?:[=>]|\s+[A-Za-z-]+=))[^<>]*>",
    re.IGNORECASE)
BRACKET_QUOTE_RE = re.compile(r"\[[^\[\]]*\]")

CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
LATIN_WORD_RE = re.compile(r"[A-Za-z]{2,}")
KOREAN_RE = re.compile(r"[\uac00-\ud7a3]")


# ==================== 接口 ====================

def strict_tokens(text: str, keyword_brackets: bool = False) -> Counter:
    """必须一一对应的标记。keyword_brackets=True 时把 [SingleWord] 也算进来。"""
    rx = STRICT_KW_RE if keyword_brackets else STRICT_RE
    return Counter(rx.findall(text or ""))


def keyword_diff(en: str, zh: str):
    """机制关键词 [Xxx] 的比对，返回 (丢失集合, 凭空多出的集合)。

    只看「有没有」，不看出现几次：官方译文常把重复提及合并成一次
    （EN "At more than 6 [X], gain Power for every excess [X] Stack" 出现两次，
    官方中文写成「若[X]层数高于6层，则每超过1层…」只出现一次），
    这是更顺的中文，不该算错。整个关键词消失才是错。
    """
    a = set(KEYWORD_BRACKET_RE.findall(en or ""))
    b = set(KEYWORD_BRACKET_RE.findall(zh or ""))
    return a - b, b - a


def soft_tokens(text: str) -> Counter:
    """可增删的排版标签。"""
    return Counter(SOFT_TAG_RE.findall(text or ""))


def layout_diff(en: str, zh: str):
    """比对排版标签，返回 (丢失, 违规新增, 已放行的新增)。

    丢失和违规新增都是硬错误；已放行的只有良秀注音那一种。
    """
    a, b = soft_tokens(en), soft_tokens(zh)
    lost  = a - b
    added = b - a

    allowed = Counter()
    allowance = 0
    for tok in ALLOWED_ADDED_TAGS:
        n = added.get(tok, 0)
        if n:
            allowed[tok] = n
            del added[tok]
            allowance += n
    if allowance:
        n = min(allowance, added.get(ALLOWED_ADDED_CLOSER, 0))
        if n:
            allowed[ALLOWED_ADDED_CLOSER] = n
            added[ALLOWED_ADDED_CLOSER] -= n
            if added[ALLOWED_ADDED_CLOSER] == 0:
                del added[ALLOWED_ADDED_CLOSER]

    return lost, added, allowed


def soft_count(text: str) -> int:
    """换行数（真换行与字面 \n 都算）。"""
    return len(NEWLINE_RE.findall(text or ""))


def fmt_list(text: str, keyword_brackets: bool = False) -> list:
    """给译者看的「必须原样保留」清单（去重保序）。"""
    rx = STRICT_KW_RE if keyword_brackets else STRICT_RE
    seen, out = set(), []
    for tok in rx.findall(text or ""):
        if tok not in seen:
            seen.add(tok)
            out.append(tok)
    return out


def quote_notes(text: str, keyword_brackets: bool = False) -> list:
    """提醒译者：这些括号是引号，里面的内容要翻，括号保留。"""
    keep = set(fmt_list(text, keyword_brackets))
    notes = []
    for m in ANGLE_QUOTE_RE.findall(text or ""):
        notes.append(f"{m} ← 尖括号是心声/通讯的引号，内容要翻，尖括号保留")
    for m in BRACKET_QUOTE_RE.findall(text or ""):
        if m in keep:
            continue          # 机制关键词 ID，已经在 keep_verbatim 里
        notes.append(f"{m} ← 方括号是广播/系统音/音效的标注，内容要翻，方括号保留")
    return notes


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text or ""))


def has_latin_word(text: str) -> bool:
    """含长度 >=2 的拉丁字母串 → 需要翻译。

    排除 teller 里 '@!($&$2w!' 这类乱码（只有单个字母）。
    """
    return bool(LATIN_WORD_RE.search(text or ""))


def is_korean(text: str) -> bool:
    return bool(KOREAN_RE.search(text or ""))
