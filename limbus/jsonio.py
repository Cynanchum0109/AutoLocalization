#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JSON 读写：统一剥 BOM、统一无 BOM / LF / ensure_ascii=False 写出。"""

import json
import os
import sys
from typing import Any, Optional


def load_json(path: str, *, on_error: str = "none") -> Optional[Any]:
    """读 JSON，自动剥 UTF-8 BOM。

    on_error: "none" 静默返回 None / "warn" 打警告 / "raise" 抛出
    """
    try:
        with open(path, "rb") as f:
            raw = f.read()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        if on_error == "raise":
            raise
        if on_error == "warn":
            print(f"  [警告] 读取失败 {path}: {e}", file=sys.stderr)
        return None


def save_json(path: str, data: Any, *, indent: int = 2, makedirs: bool = True) -> None:
    """写 JSON：utf-8 无 BOM、LF 换行、ensure_ascii=False。

    indent 默认 2，与游戏 LLC_zh-CN 现有文件一致，避免 diff 全变。

    先写同目录下的临时文件再 os.replace 换上去：写到一半被打断（或另一个 agent
    同时在读）都不会读到半截 JSON。
    """
    if makedirs:
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def setup_stdout() -> None:
    """Windows 控制台输出中文不炸。"""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
