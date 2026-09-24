#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自家译文记忆：从 progress.json 找「同一个大写名词短语，我们之前怎么译的」。

术语表只覆盖已定名的词；RPG 新名词（Golden Skein / Prestige Tier / Le Kaki …）
每批各译各的就会分裂。这里把候选专名短语抽出来，回查我们自己的译文库，
在 batch 里附上前译例句，让同一个词前后一致。

另外读 glossary/pending_terms.json 里的待定词，命中时也提示「待定，暂沿用 X」。
"""

import glob
import json
import os
import re
from collections import defaultdict

import config
from limbus.jsonio import load_json

PENDING_TERMS = os.path.join(config.BASE_DIR, "glossary", "pending_terms.json")
# 跨 agent 共享的「这个词我们说定了译成 X」台账。两个 agent（甚至不同家的 AI）
# 都读它、都往里写，新造的专名才不会一人一个译法。
SESSION_TERMS = os.path.join(config.BASE_DIR, "glossary", "session_terms.json")

# 大写开头的词串：Golden Skein / Le Rouge Store Manager / King of Needleworks / Kromer's Sister
_CAP = r"[A-Z][a-zA-Z'\-]+"
_PHRASE_RE = re.compile(
    rf"\b{_CAP}(?:(?: (?:of|the|de|du|la|le|des))? {_CAP})*"
)
# 句首常见词、称谓、感叹词——单独出现时不算专名
_STOP = {
    "I", "The", "A", "An", "And", "But", "Or", "So", "If", "In", "On", "At", "To", "Of",
    "It", "Is", "We", "You", "He", "She", "They", "That", "This", "There", "Then", "What",
    "Why", "How", "When", "Where", "Who", "Yes", "No", "Oh", "Ah", "Hm", "Hmm", "Well",
    "Let", "Don't", "Can't", "Won't", "Isn't", "Wasn't", "Didn't", "Doesn't", "Ugh", "Huh",
    "Just", "Now", "Not", "For", "With", "As", "Be", "Do", "Go", "My", "Your", "Our", "Their",
    "His", "Her", "Its", "Are", "Was", "Were", "Have", "Has", "Had", "Will", "Would", "Should",
    "Could", "May", "Might", "Must", "Please", "Thank", "Thanks", "Okay", "Alright", "Right",
    "Wait", "Look", "Hey", "Uh", "Um", "Er", "Eh", "Very", "Still", "Even", "Only", "Also",
    "Though", "Because", "While", "After", "Before", "Once", "Since", "Until", "Every", "All",
    "Some", "Any", "Each", "Both", "Either", "Neither", "None", "Nothing", "Everything",
    "Something", "Anything", "Perhaps", "Maybe", "Indeed", "Of", "By", "From", "Into", "Onto",
    "Sure", "Fine", "Good", "Bad", "Great", "Ha", "Hah", "Haha", "Tch", "Hmph", "Whoa", "Wow",
    "Here", "Those", "These", "Which", "Whose", "Than", "Too", "Such", "Much", "Many", "More",
    "Most", "Less", "Least", "Other", "Another", "Same", "Own", "Ready", "Come", "Get", "Got",
    "Stop", "Keep", "Take", "Make", "Give", "Tell", "Say", "See", "Know", "Think", "Want",
    "Need", "Like", "Love", "Hate", "Sorry", "Excuse", "Listen", "Watch", "Hold", "Move",
    "Run", "Kill", "Die", "Dead", "Damn", "Shut", "Never", "Always", "Sometimes", "Again",
    "Anyway", "However", "Besides", "Actually", "Really", "Truly", "Certainly", "Exactly",
    "Absolutely", "Obviously", "Apparently", "Honestly", "Seriously", "Finally", "First",
    "Second", "Third", "Last", "Next", "Today", "Tomorrow", "Yesterday", "Tonight",
}


def phrases(text):
    """抽候选专名短语（去重，保持出现顺序）。"""
    out = []
    seen = set()
    for m in _PHRASE_RE.finditer(text or ""):
        p = m.group(0)
        words = p.split()
        # 剥掉开头的句首词（"The Golden Nail" -> "Golden Nail"；"Why Golden" -> "Golden"）
        while words and words[0] in _STOP:
            words = words[1:]
        while words and words[-1] in _STOP:
            words = words[:-1]
        if not words:
            continue
        p = " ".join(words)
        if len(words) == 1 and (len(p) < 4 or p in _STOP):
            continue
        # 单个大写词若紧跟在句首/引号后，很可能只是句首大写；要求它在文中别处也出现或是多词
        if len(words) == 1 and m.start() > 0 and text[m.start() - 1] in ".!?\"'<[\n" :
            pass  # 句首单词照样收，靠 progress 里的出现频次过滤
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


class OurTerms:
    def __init__(self, progress=None, min_count=2, include_inflight=True):
        self.progress = progress if progress is not None else (load_json(config.PROGRESS) or {})
        self.min_count = min_count
        self.index = defaultdict(list)  # phrase -> [(key, en, zh, inflight)]
        for key, v in self.progress.items():
            if not isinstance(v, dict):
                continue
            en, zh = v.get("en") or "", v.get("zh") or ""
            self._add(key, en, zh, False)
        # 另一个 agent 手上翻好、还没合批的批次也算数：否则 A 刚定的译名
        # 要等 A 合批 + B 重新取批才看得到，中间这段时间两人必然分叉。
        self.inflight = 0
        if include_inflight:
            for key, en, zh in _iter_inflight():
                self._add(key, en, zh, True)
                self.inflight += 1
        self.pending = self._load_pending()
        self.session = load_json(SESSION_TERMS) or {}

    def _add(self, key, en, zh, inflight):
        if not en or not zh:
            return
        for p in phrases(en):
            self.index[p].append((key, en, zh, inflight))

    @staticmethod
    def _load_pending():
        d = load_json(PENDING_TERMS) or {}
        flat = {}
        for section, terms in d.items():
            if section.startswith("_") or not isinstance(terms, dict):
                continue
            for k, v in terms.items():
                if k.startswith("_"):
                    continue
                for part in k.split("/"):
                    flat[part.strip()] = v
        return flat

    def lookup(self, text, exclude_key=None, max_terms=6, max_examples=2):
        """返回 {短语: [前译 zh, ...]}，只列我们译过 ≥min_count 次的短语。"""
        out = {}
        for p in phrases(text):
            rows = [r for r in self.index.get(p, []) if r[0] != exclude_key]
            # 别的 agent 手上刚翻好的，一条就够——那正是最容易分叉的时刻
            if len(rows) < self.min_count and not any(r[3] for r in rows):
                continue
            # 例句去重、优先短句（更容易看出该词怎么译）；未合批的排前面
            uniq = []
            seen = set()
            for _, en, zh, inflight in sorted(rows, key=lambda r: (not r[3], len(r[2]))):
                if zh and zh not in seen:
                    seen.add(zh)
                    uniq.append(("[另一 agent 刚定] " if inflight else "") + zh)
                if len(uniq) >= max_examples:
                    break
            if uniq:
                out[p] = uniq
            if len(out) >= max_terms:
                break
        return out

    def session_hits(self, text):
        """命中共享台账里说定的译名（跨 agent 一致性的硬约定）。"""
        out = {}
        for k, v in self.session.items():
            if k.startswith("_"):
                continue
            if re.search(r"(?<![A-Za-z])" + re.escape(k) + r"(?![A-Za-z])", text or "",
                         re.IGNORECASE):
                out[k] = v
        return out

    def pending_hits(self, text):
        low = text or ""
        out = {}
        for k, v in self.pending.items():
            if re.search(r"(?<![A-Za-z])" + re.escape(k) + r"(?![A-Za-z])", low, re.IGNORECASE):
                out[k] = v
        return out


def _iter_inflight():
    """扫所有 slot 的 batch_answers.json，配上同 slot 的 pending 拿英文原文。

    产出 (key, en, zh)，只要那条已经填了译文。
    """
    root = os.path.join(config.OUT_DIR, "slots")
    for ans_path in glob.glob(os.path.join(root, "*", "batch_answers.json")):
        if os.path.basename(os.path.dirname(ans_path)) == config.SLOT:
            continue          # 自己手上那批不算「别人刚定的」
        pend_path = os.path.join(os.path.dirname(ans_path), "batch_pending.json")
        answers = load_json(ans_path) or []
        pending = load_json(pend_path) or []
        en_by_key = {p.get("key"): p.get("original", "") for p in pending if isinstance(p, dict)}
        for a in answers:
            if not isinstance(a, dict):
                continue
            key, zh = a.get("key"), (a.get("translation") or "").strip()
            if key and zh:
                yield key, en_by_key.get(key, ""), zh


def record(term, zh, note="", who=None, force=False):
    """把「这个词定成这么译」写进共享台账（两个 agent 都该调）。

    同词同译 → 静默通过。同词异译 → 报冲突并**保留旧译名**（要改用 force=True），
    否则后写的人会无声盖掉先定的译名，两边译文当场分叉。
    """
    from limbus import lock
    who = who or config.SLOT
    with lock.lock("session_terms"):
        data = load_json(SESSION_TERMS) or {}
        old = data.get(term)
        if isinstance(old, dict) and old.get("zh") and old["zh"] != zh and not force:
            print(f"[冲突] 术语 {term!r} 已由 {old.get('by', '?')} 定为 {old['zh']!r}，"
                  f"本次想改成 {zh!r} —— 保留旧译名。")
            print("       确认要改：record(..., force=True)，并同步改掉已合批的译文。")
            return old
        data.setdefault("_note", "跨 agent 共享的新造专名台账：glossary.json 里没有、"
                                 "但本轮已经定下来的译名。两个 agent 都要读、都要写。")
        entry = {"zh": zh, "by": who}
        if note:
            entry["note"] = note
        data[term] = entry
        from limbus.jsonio import save_json
        save_json(SESSION_TERMS, data, indent=1)
    return data[term]
