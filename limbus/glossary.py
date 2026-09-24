#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""术语表查找。

旧实现对每条文本跑 2600 项 × SequenceMatcher，CPU 开销比网络请求还大。
这里改成一次编译成单个「长词优先 + 词边界」正则，查一句是一次扫描。
"""

import re

import config
from limbus.jsonio import load_json


class Glossary:
    """键以 ``!`` 开头表示大小写敏感（如 ``!Ticket`` 只命中大写 Ticket，不命中 ticket）。
    hits() 返回的键不带 ``!``。"""

    def __init__(self, path=None):
        self.terms = load_json(path or config.GLOSSARY) or {}
        if not isinstance(self.terms, dict):
            self.terms = {}
        # 长词优先，避免 "Aspect Pool" 被 "Aspect" 先吃掉
        keys = sorted((t for t in self.terms if len(t.lstrip("!")) >= 3), key=len, reverse=True)
        ci = [k for k in keys if not k.startswith("!")]
        cs = [k[1:] for k in keys if k.startswith("!")]
        self._lookup_ci = {k.lower(): k for k in ci}
        self._lookup_cs = {k: "!" + k for k in cs}
        self._re_ci = self._compile(ci, re.IGNORECASE)
        self._re_cs = self._compile(cs, 0)

    @staticmethod
    def _compile(keys, flags):
        if not keys:
            return None
        return re.compile(
            # 允许复数后缀：Fixers / Mannequins / Strangers 也命中单数条目
            r"(?<![A-Za-z])(?:" + "|".join(re.escape(k) for k in keys) + r")(?:e?s)?(?![A-Za-z])",
            flags,
        )

    def __len__(self):
        return len(self.terms)

    @staticmethod
    def _find(lookup, word):
        for w in (word, word[:-1], word[:-2]):
            if w in lookup:
                return lookup[w]
        return None

    def hits(self, text, max_hits=12):
        """返回 {原词: 译名}，按在文中出现的顺序，最多 max_hits 条。"""
        if not text:
            return {}
        found = []  # (pos, 显示词, 译名)
        if self._re_ci:
            for m in self._re_ci.finditer(text):
                orig = self._find(self._lookup_ci, m.group(0).lower())
                if orig:
                    found.append((m.start(), orig, self.terms[orig]))
        if self._re_cs:
            for m in self._re_cs.finditer(text):
                k = self._find(self._lookup_cs, m.group(0))
                if k:
                    found.append((m.start(), k[1:], self.terms[k]))
        out = {}
        for _, word, zh in sorted(found, key=lambda x: x[0]):
            if word not in out:
                out[word] = zh
                if len(out) >= max_hits:
                    break
        return out
