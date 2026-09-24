#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨进程文件锁 + 认领表（claims），给多个 agent 同时干活用。

两个 agent 各跑一份 batch_next / batch_merge 时有两处会打架：
  1. progress.json 是 read-modify-write，两边同时合批会丢译文；
  2. batch_next 可能把同一批条目同时发给两个 agent，白翻一遍还互相覆盖。

解决：
  - `with lock("progress"):` 包住任何读-改-写，锁文件在 out/locks/ 下，
    O_CREAT|O_EXCL 抢占，Windows 也能用；超过 STALE_SECONDS 的残锁自动清掉
    （进程被 Ctrl-C 掉不会把整条流水线卡死）。
  - claims.json 记 **文件** -> {slot, ts}：一个文件整份包给一个 agent，
    别的 slot 不碰。按文件分工才有上下文可言——同一段对话被两个 agent 各翻一半，
    称谓、语气、代词指代必然对不上。租约 LEASE_SECONDS 到期自动失效。
"""

import os
import time
from contextlib import contextmanager

import config
from limbus.jsonio import load_json, save_json

LOCK_DIR = os.path.join(config.OUT_DIR, "locks")
CLAIMS = os.path.join(config.OUT_DIR, "claims.json")

STALE_SECONDS = 300      # 锁文件超过这么久没人动 → 认定是残锁
LEASE_SECONDS = 4 * 3600  # 认领的条目多久没合批 → 自动放出来给别人


@contextmanager
def lock(name, timeout=60):
    """抢一把命名锁，抢不到就等，超时抛 TimeoutError。"""
    os.makedirs(LOCK_DIR, exist_ok=True)
    path = os.path.join(LOCK_DIR, name + ".lock")
    deadline = time.time() + timeout
    fd = None
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()} {config.SLOT} {time.time():.0f}".encode())
            break
        except FileExistsError:
            try:
                age = time.time() - os.path.getmtime(path)
            except OSError:
                continue          # 刚好被别人释放了，重试
            if age > STALE_SECONDS:
                print(f"  [锁] 清掉 {name} 的残锁（{age:.0f}s 无人动）")
                try:
                    os.unlink(path)
                except OSError:
                    pass
                continue
            if time.time() > deadline:
                raise TimeoutError(f"等 {name} 锁超时（{timeout}s）：另一个 agent 正在写")
            time.sleep(0.2)
    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        try:
            os.unlink(path)
        except OSError:
            pass


def _prune(claims, now=None):
    now = now or time.time()
    return {k: v for k, v in claims.items()
            if now - v.get("ts", 0) < LEASE_SECONDS}


def load_claims():
    """读认领表，顺手滤掉过期租约。"""
    return _prune(load_json(CLAIMS) or {})


def claimed_by_others(slot=None):
    """别的 slot 正包着的文件集合（形如 "RPGSystem/xxx.json"）。"""
    slot = slot or config.SLOT
    return {k for k, v in load_claims().items() if v.get("slot") != slot}


def mine(slot=None):
    """自己正包着的文件集合。"""
    slot = slot or config.SLOT
    return {k for k, v in load_claims().items() if v.get("slot") == slot}


def claim(files, slot=None):
    """把整个文件包到自己名下。返回真正拿到的文件集合。

    别人已经占着的不会抢；锁内做，避免两边同时写丢一半。
    """
    slot = slot or config.SLOT
    now = time.time()
    got = set()
    with lock("claims"):
        claims = load_claims()
        for f in files:
            holder = claims.get(f, {}).get("slot")
            if holder and holder != slot:
                continue
            claims[f] = {"slot": slot, "ts": now}
            got.add(f)
        save_json(CLAIMS, claims, indent=1)
    return got


def touch(files, slot=None):
    """续租：批次还在手上就刷新时间戳，别让 4 小时租约到期被别人抢走。"""
    slot = slot or config.SLOT
    now = time.time()
    with lock("claims"):
        claims = load_claims()
        for f in files:
            if claims.get(f, {}).get("slot") == slot:
                claims[f]["ts"] = now
        save_json(CLAIMS, claims, indent=1)


def release(files, slot=None):
    """文件翻完了，交还给池子。"""
    slot = slot or config.SLOT
    with lock("claims"):
        claims = load_claims()
        for f in set(files):
            if claims.get(f, {}).get("slot") == slot:
                claims.pop(f, None)
        save_json(CLAIMS, claims, indent=1)


def release_all(slot=None):
    """释放某个 slot 包着的全部文件（agent 退出或想重来时用）。"""
    slot = slot or config.SLOT
    with lock("claims"):
        claims = load_claims()
        claims = {k: v for k, v in claims.items() if v.get("slot") != slot}
        save_json(CLAIMS, claims, indent=1)
