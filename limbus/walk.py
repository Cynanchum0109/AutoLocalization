#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""遍历游戏文件、生成翻译单元（unit）与稳定 key。

key 格式：  <scope>/<file.json>#<id>#<field>
例：        StoryData/1D101A.json#0#content
            _root/BattleSpeechBubbleDlg.json#battle_speechbubble_cromer_1#dlg

key 只依赖 id 与字段名，官方增删条目不会打乱已有译文的归属。

注意：游戏文件里存在重复 id（音效条目常年用 id=-1，个别文件真的有重复 id）。
同一文件内 id 重复时，第 2 个起加 "~n" 后缀区分：`...#-1~2#content`。
"""

import hashlib
import os
import re

import config
from limbus.fmtcode import STRICT_KW_RE, STRICT_RE, has_latin_word
from limbus.jsonio import load_json


class Target:
    """一个待处理文件：EN 源 + ZH 对照 + 输出路径。"""

    __slots__ = ("scope", "filename", "en_path", "zh_path", "out_path")

    def __init__(self, scope, filename, en_path, zh_path, out_path):
        self.scope    = scope
        self.filename = filename
        self.en_path  = en_path
        self.zh_path  = zh_path
        self.out_path = out_path

    @property
    def label(self):
        return f"{self.scope}/{self.filename}"


def iter_targets():
    """按 config 里的 tier0 范围列出所有待处理文件。"""
    for scope, subdir in config.TIER0_DIRS:
        en_dir = os.path.join(config.EN_ROOT, subdir)
        zh_dir = os.path.join(config.ZH_ROOT, subdir)
        if not os.path.isdir(en_dir):
            continue
        for fn in sorted(os.listdir(en_dir)):
            if not (fn.startswith("EN_") and fn.endswith(".json")):
                continue
            zh_fn = fn[3:]
            yield Target(
                scope, zh_fn,
                os.path.join(en_dir, fn),
                os.path.join(zh_dir, zh_fn),
                os.path.join(config.WORK_ROOT, subdir, zh_fn),
            )

    # 机制文本（根目录，单独 scope：方括号关键词不翻）
    for zh_fn in config.TIER0_MECH_FILES:
        en_path = os.path.join(config.EN_ROOT, "EN_" + zh_fn)
        if not os.path.exists(en_path):
            continue
        yield Target(
            config.MECH_SCOPE, zh_fn,
            en_path,
            os.path.join(config.ZH_ROOT, zh_fn),
            os.path.join(config.WORK_ROOT, zh_fn),
        )

    # 根目录点名文件
    wanted = set(config.TIER0_ROOT_FILES)
    if os.path.isdir(config.EN_ROOT):
        for fn in sorted(os.listdir(config.EN_ROOT)):
            if not (fn.startswith("EN_") and fn.endswith(".json")):
                continue
            zh_fn = fn[3:]
            hit = zh_fn in wanted or any(
                zh_fn.startswith(p) for p in config.TIER0_ROOT_PREFIXES
            )
            if not hit:
                continue
            yield Target(
                config.ROOT_SCOPE, zh_fn,
                os.path.join(config.EN_ROOT, fn),
                os.path.join(config.ZH_ROOT, zh_fn),
                os.path.join(config.WORK_ROOT, zh_fn),
            )


def make_key(scope, filename, item_id, field):
    return f"{scope}/{filename}#{item_id}#{field}"


def src_hash(text):
    return hashlib.sha1((text or "").encode("utf-8")).hexdigest()[:16]


def data_list(data):
    if isinstance(data, dict) and isinstance(data.get("dataList"), list):
        return data["dataList"]
    return []


def item_ids(data):
    """给 dataList 每个条目算出唯一 id 串，与 data_list(data) 一一对应。

    非 dict 或没有 id 的条目返回 None。同一 id 第 2 次出现起加 "~n"。
    """
    seen = {}
    out = []
    for it in data_list(data):
        if not isinstance(it, dict):
            out.append(None)
            continue
        # RPGSystem 用 "key" 当条目标识，没有 "id" 字段
        raw_id = it["id"] if "id" in it else it.get("key")
        if raw_id is None:
            out.append(None)
            continue
        raw = str(raw_id)
        n = seen.get(raw, 0) + 1
        seen[raw] = n
        out.append(raw if n == 1 else f"{raw}~{n}")
    return out


def index_by_id(data):
    """{唯一 id 串: 条目}"""
    items = data_list(data)
    return {iid: it for iid, it in zip(item_ids(data), items) if iid is not None}


def needs_translation(value, keyword_brackets: bool = False):
    """该字段值是否需要翻译。

    只认拉丁字母串。韩文（气泡文件的 desc、StoryData 的 model）与纯符号
    （teller 的 '@!($&$2w!'）都不进队列——官方 ZH 也保持原样。

    机制文本里还有一类整条就是关键词 ID 的（desc 就是 "[SuperCoin]"），
    去掉强标记后什么都不剩，也不该进队列。
    """
    if not isinstance(value, str) or not has_latin_word(value):
        return False
    rx = STRICT_KW_RE if keyword_brackets else STRICT_RE
    return has_latin_word(rx.sub("", value))


def iter_units(target, en_data=None):
    """产出该文件的全部待翻译单元。

    每个 unit: dict(key, scope, filename, id, field, original, order, item)
    order 用于还原上下文顺序。
    """
    if en_data is None:
        en_data = load_json(target.en_path, on_error="warn")
    items = data_list(en_data)
    ids = item_ids(en_data)
    for order, (item, item_id) in enumerate(zip(items, ids)):
        if item_id is None:
            continue
        for path, value in iter_string_paths(item):
            if not needs_translation(value, config.keyword_brackets(target.scope, path)):
                continue
            yield {
                "key":      make_key(target.scope, target.filename, item_id, path),
                "scope":    target.scope,
                "filename": target.filename,
                "id":       item_id,
                "field":    path,
                "original": value,
                "order":    order,
                "item":     item,
            }


# ==================== 嵌套字段（机制文本用） ====================
# 技能文件不是扁平的：
#   {"id": 501905, "levelList": [{"name": ..., "desc": ...,
#     "coinlist": [{"coindescs": [{"desc": ...}]}]}]}
# 于是 key 的第三段用路径表示：levelList[0].coinlist[2].coindescs[4].desc

_PATH_RE = re.compile(r"[^.\[\]]+|\[\d+\]")


def iter_string_paths(item):
    """产出 (路径, 字符串值)，只认 TRANSLATE_FIELDS 里的叶子字段名。"""
    out = []

    def rec(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in config.NEVER_TRANSLATE:
                    continue
                rec(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                rec(v, f"{path}[{i}]")
        elif isinstance(node, str):
            leaf = path.split(".")[-1].split("[")[0]
            if leaf in config.TRANSLATE_FIELDS:
                out.append((path, node))

    rec(item, "")
    return out


def get_by_path(item, path):
    node = item
    for part in _PATH_RE.findall(path):
        try:
            node = node[int(part[1:-1])] if part.startswith("[") else node[part]
        except (KeyError, IndexError, TypeError):
            return None
    return node


def set_by_path(item, path, value):
    parts = _PATH_RE.findall(path)
    node = item
    for part in parts[:-1]:
        node = node[int(part[1:-1])] if part.startswith("[") else node[part]
    last = parts[-1]
    if last.startswith("["):
        node[int(last[1:-1])] = value
    else:
        node[last] = value
