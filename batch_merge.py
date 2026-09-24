#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""batch_merge.py - 校验 batch_answers.json 并并入 out/progress.json。

任何硬错误都会整批拒绝，progress 不会被悄悄污染。

硬错误（拒绝合批）：
  - answers 与 pending 的 key 对不上
  - 译文为空
  - 强标记数量与原文不一致：<color=..> <style=..> {0} 乱码序列
  - 机制关键词 [Sinking] 整个消失或凭空多出（只在机制文本的 desc/summary/flavor 里查；
    重复提及合并成一次是允许的，官方也这么写）
  - 排版标签丢失或擅自新增：<i> <b> <u> <s> <size> <ruby> 等
    （唯一放行的新增是良秀注音 <ruby=Yoshihide>…</ruby>）
  - 译文里残留 ⟦n⟧ 之类的哨兵

软警告（照常合批，只打印）：
  - 换行数与原文不同（官方译文也常合并两行）
  - 译文不含中文
  - 译文与原文完全相同
  - 术语表命中词在译文里找不到对应译名（Fixer→收尾人 之类；普通词义可忽略）

用法：
  python batch_merge.py
  python batch_merge.py --force   忽略硬错误强行合批（不建议）
"""

import argparse
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from limbus import walk
from limbus.glossary import Glossary
from limbus import lock
from limbus.fmtcode import has_cjk, keyword_diff, layout_diff, soft_count, strict_tokens
from limbus.jsonio import load_json, save_json, setup_stdout


def main():
    setup_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    pending = load_json(config.PENDING)
    answers = load_json(config.ANSWERS)
    if pending is None:
        print(f"[错误] 缺少 {config.PENDING}，先跑 batch_next.py")
        sys.exit(1)
    if answers is None:
        print(f"[错误] 缺少 {config.ANSWERS}")
        sys.exit(1)

    batch_files = {p["key"].rsplit("#", 2)[0] for p in pending if "key" in p}
    poached = batch_files & lock.claimed_by_others()
    if poached and not args.force:
        print("[拒绝合批] 这些文件现在归别的 agent 包着（本 slot 的租约多半已过期，"
              "期间对方可能已重译）：")
        for f in sorted(poached):
            print(f"  - {f}")
        print()
        print("答案文件保留原处，不会被覆盖。要么让对方合批，要么确认无冲突后 --force。")
        sys.exit(1)

    pend_map = {p["key"]: p for p in pending}
    ans_map  = {a["key"]: a.get("translation", "") for a in answers if "key" in a}

    hard, soft = [], []
    gloss = Glossary()

    missing = [k for k in pend_map if k not in ans_map]
    extra   = [k for k in ans_map if k not in pend_map]
    for k in missing:
        hard.append((k, "answers 里没有这条"))
    for k in extra:
        soft.append((k, "answers 里多出来的 key，忽略"))

    for key, p in pend_map.items():
        zh = ans_map.get(key)
        if zh is None:
            continue
        if not zh.strip():
            hard.append((key, "译文为空"))
            continue
        en = p["original"]
        scope = key.split("/", 1)[0]
        field = key.rsplit("#", 1)[-1]
        st_en, st_zh = strict_tokens(en), strict_tokens(zh)
        if config.keyword_brackets(scope, field):
            lost_kw, added_kw = keyword_diff(en, zh)
            if lost_kw:
                hard.append((key, "机制关键词丢失（必须保留英文 ID）：" + " ".join(sorted(lost_kw))))
            if added_kw:
                hard.append((key, "凭空多出的机制关键词：" + " ".join(sorted(added_kw))))
        if st_en != st_zh:
            lost  = st_en - st_zh
            added = st_zh - st_en
            detail = []
            if lost:
                detail.append("丢失 " + " ".join(f"{t}×{n}" for t, n in lost.items()))
            if added:
                detail.append("多出 " + " ".join(f"{t}×{n}" for t, n in added.items()))
            hard.append((key, "格式码不一致：" + "；".join(detail)))
        if "⟦" in zh or "⟧" in zh:
            hard.append((key, "译文残留哨兵 ⟦n⟧"))
        lost, bad_added, ok_added = layout_diff(en, zh)
        if lost:
            hard.append((key, "排版标签丢失（必须原样保留）："
                              + " ".join(f"{t}×{n}" for t, n in lost.items())))
        if bad_added:
            hard.append((key, "擅自新增排版标签（只有良秀注音 <ruby=Yoshihide> 例外）："
                              + " ".join(f"{t}×{n}" for t, n in bad_added.items())))
        if ok_added:
            soft.append((key, "新增良秀注音："
                              + " ".join(f"{t}×{n}" for t, n in ok_added.items())))
        if soft_count(en) != soft_count(zh):
            soft.append((key, f"换行数 {soft_count(en)} → {soft_count(zh)}"))
        # 术语表命中词，译文里找不到对应译名 → 提醒（可能是普通词义，不拦）
        miss = []
        for word, val in gloss.hits(en).items():
            expect = re.split(r"[（(/]", val)[0].strip()
            if expect and expect not in zh:
                miss.append(f"{word}→{expect}")
        if miss:
            soft.append((key, "术语未按表使用（若是普通词义可忽略）：" + "；".join(miss)))
        if not has_cjk(zh):
            soft.append((key, f"译文不含中文：{zh[:40]!r}"))
        elif zh == en:
            soft.append((key, "译文与原文完全相同"))

    for key, msg in soft:
        print(f"  [警告] {key}\n         {msg}")

    if hard and not args.force:
        print(f"\n[拒绝合批] {len(hard)} 个硬错误：")
        for key, msg in hard[:30]:
            print(f"  - {key}\n    {msg}")
        if len(hard) > 30:
            print(f"  …… 另有 {len(hard) - 30} 条")
        print("\n改好 batch_answers.json 后重跑。")
        sys.exit(1)
    if hard and args.force:
        print(f"\n[--force] 忽略 {len(hard)} 个硬错误，继续合批。")

    # progress.json 是读-改-写：不加锁的话两个 agent 同时合批会丢掉一整批译文
    now = datetime.now().isoformat(timespec="seconds")
    with lock.lock("progress"):
        progress = load_json(config.PROGRESS) or {}
        before = len(progress)
        for key, p in pend_map.items():
            zh = ans_map.get(key)
            if zh is None or not zh.strip():
                continue
            progress[key] = {
                "zh":       zh,
                "src_hash": walk.src_hash(p["original"]),
                "en":       p["original"],
                "ts":       now,
            }
        save_json(config.PROGRESS, progress, indent=1)
    # 本批涉及的文件：还有没翻完的就续租，翻完的交还池子（scan 之后才知道，
    # 所以这里按 state.json 的剩余量粗判；拿不到 state 就保守续租）
    files = {k.rsplit("#", 2)[0] for k in pend_map}
    state = load_json(config.STATE) or {}
    merged = set(pend_map)
    left = {f"{x['scope']}/{x['file']}" for x in state.get("actionable", [])
            if x["status"] in ("todo", "stale", "outdated_official")
            and x["key"] not in merged}
    drained = files - left
    if drained:
        lock.release(drained)
        print(f"[并行] 已翻完并交还：{', '.join(sorted(drained))}")
    if files - drained:
        lock.touch(files - drained)

    print(f"\n合批完成：{before} → {len(progress)} 条译文（{config.PROGRESS}）")
    print("下一步：python scan.py 刷新状态，或 python apply.py 出文件。")

    # 合批成功后归档，避免下一批误用旧答案
    for path in (config.PENDING, config.ANSWERS):
        if os.path.exists(path):
            os.replace(path, path + ".done")


if __name__ == "__main__":
    main()
