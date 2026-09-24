#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻译记忆库：把官方 LLC_zh-CN 里已有的译文按原文索引起来。

机制文本（技能/被动/Buff）大量重复 —— "[OnSucceedAttack] Inflict 3 [Combustion]"
这种句子官方已经译过几十次。同一句直接复用官方译法，比重译更一致也更快。

缓存在 out/tm.json，游戏更新后删掉重建即可（或 build(force=True)）。
"""

import json
import os
from collections import Counter, defaultdict

import config
from limbus import walk
from limbus.fmtcode import has_cjk
from limbus.jsonio import load_json, save_json

CACHE = os.path.join(config.OUT_DIR, "tm.json")


def build(force: bool = False) -> dict:
    """扫描 EN/ZH 全部同名文件对，产出 {英文原文: 官方中文}。

    同一原文有多种官方译法时取出现次数最多的那个。
    """
    if not force:
        cached = load_json(CACHE)
        if cached:
            return cached

    votes = defaultdict(Counter)
    for fn in sorted(os.listdir(config.EN_ROOT)):
        if not (fn.startswith("EN_") and fn.endswith(".json")):
            continue
        zh_path = os.path.join(config.ZH_ROOT, fn[3:])
        if not os.path.exists(zh_path):
            continue
        en = load_json(os.path.join(config.EN_ROOT, fn))
        zh = load_json(zh_path)
        if not (isinstance(en, dict) and isinstance(zh, dict)):
            continue
        zh_index = walk.index_by_id(zh)
        for item, item_id in zip(walk.data_list(en), walk.item_ids(en)):
            if item_id is None:
                continue
            zh_item = zh_index.get(item_id)
            if not isinstance(zh_item, dict):
                continue
            for path, v in walk.iter_string_paths(item):
                w = walk.get_by_path(zh_item, path)
                if isinstance(w, str) and w and w != v and has_cjk(w):
                    votes[v][w] += 1

    tm = {k: c.most_common(1)[0][0] for k, c in votes.items()}
    ambiguous = {k for k, c in votes.items() if len(c) > 1}
    save_json(CACHE, tm, indent=0)
    save_json(os.path.join(config.OUT_DIR, "tm_ambiguous.json"),
              sorted(ambiguous), indent=0)
    return tm


def load() -> dict:
    return build()


def ambiguous_set() -> set:
    return set(load_json(os.path.join(config.OUT_DIR, "tm_ambiguous.json")) or [])
