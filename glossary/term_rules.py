#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
term_rules.py - 术语准入规则（共享）

设计原则：脏数据在“入口”拦截，而不是入库后再清洗。
原清洗规则 R1/R2/R7/R8/R9/R11 在这里前移为准入条件：
  R1  全大写章节标题句     -> all_caps_title
  R2  叙述性标题句         -> narrative_title
  R7  对话/剧情句子        -> sentence_pronoun / sentence_punct
  R8  格式残留/韩文/HTML   -> korean / html / placeholder
  R9  截断碎片             -> ellipsis
  R11 换行拼接             -> split_bilingual() 拆双语值 + en_newline 拒收
"""

import re

MAX_EN_TERM_LEN = 80
MAX_ZH_TERM_LEN = 40

_NARRATIVE_RE = re.compile(r'^(The Tale of|A Tale of|In Which|Of the|Wherein|Of How)\b', re.IGNORECASE)
_PRONOUN_RE   = re.compile(r'\b(you|your|yours|we|our|ours|my|mine|me|us)\b', re.IGNORECASE)
_KOREAN_RE    = re.compile(r'[가-힣ᄀ-ᇿ㄰-㆏]')
# 允许出现在术语末尾的缩写点
_ABBREV_ENDINGS = ('Corp.', 'Assoc.', 'Inc.', 'Co.', 'Ltd.', 'Jr.', 'Sr.')


def has_chinese(text: str) -> bool:
    return any('一' <= c <= '鿿' for c in text)


def has_english(text: str) -> bool:
    return bool(re.search(r'[a-zA-Z]', text))


def split_bilingual(zh_val: str):
    """处理译文的 '中文\\n英文' 双语格式：只取中文行。

    返回干净的中文字符串；无法得到（首行无中文）则返回 None。
    """
    if '\n' not in zh_val:
        return zh_val.strip()
    first = zh_val.split('\n')[0].strip()
    if has_chinese(first):
        return first
    return None


def admit_term(en_val: str, zh_val: str):
    """准入判定。返回 (是否收录, 拒收原因)，原因用于报告统计。"""
    en = en_val.strip()
    zh = zh_val.strip()
    if not en or not zh:
        return False, 'empty'
    if '\n' in en:
        return False, 'en_newline'
    if not has_english(en):
        return False, 'no_english'
    if not has_chinese(zh):
        return False, 'no_chinese'
    if '??' in en or '??' in zh:
        return False, 'placeholder'
    if len(en) > MAX_EN_TERM_LEN or len(zh) > MAX_ZH_TERM_LEN:
        return False, 'too_long'
    if _KOREAN_RE.search(en) or _KOREAN_RE.search(zh):
        return False, 'korean'
    if '<' in en or '>' in en:
        return False, 'html'
    # 全大写的代码式字符串（VERY_HIGH、TRUE 等）
    if re.match(r'^[A-Z0-9_,().\s]+$', en):
        return False, 'code_like'
    # R9：截断碎片 / 省略号
    if '...' in en or '…' in en:
        return False, 'ellipsis'
    words = en.split()
    if len(words) >= 7:
        return False, 'too_many_words'
    # R1：全大写章节标题句
    letters = [c for c in en if c.isalpha()]
    if len(words) >= 4 and letters and sum(c.isupper() for c in letters) / len(letters) > 0.85:
        return False, 'all_caps_title'
    # R2：叙述性标题句
    if len(words) >= 5 and _NARRATIVE_RE.match(en):
        return False, 'narrative_title'
    # R7：含人称代词的句子
    if _PRONOUN_RE.search(en):
        return False, 'sentence_pronoun'
    # R7：句末标点（保留 Corp. 等缩写）
    if en.endswith(('.', '!', '?')) and len(words) >= 3 and not en.endswith(_ABBREV_ENDINGS):
        return False, 'sentence_punct'
    return True, 'ok'
