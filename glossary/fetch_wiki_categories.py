#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_wiki_categories.py - 从英文 wiki（limbuscompany.wiki.gg）拉术语的页面分类。

  python glossary/fetch_wiki_categories.py            只拉缓存里还没有的词
  python glossary/fetch_wiki_categories.py --refresh  全部重拉

结果缓存到 glossary/wiki_categories_cache.json：
  {"Faust": {"page": "Faust", "cats": ["Characters"]},
   "Nest":  {"page": null, "cats": []}}          ← wiki 没这个页面
缓存只是原始资料；归类规则在 categorize.py。
灰机 wiki（中文）有 Cloudflare 人机验证，脚本进不去，所以只用英文 wiki。
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from limbus.jsonio import load_json, save_json, setup_stdout

API = "https://limbuscompany.wiki.gg/api.php"
UA = "LimbusZhGlossary/0.1 (personal fan translation; glossary categorisation)"
CACHE = os.path.join(config.BASE_DIR, "glossary", "wiki_categories_cache.json")
BATCH = 50      # MediaWiki 一次最多 50 个标题
PAUSE = 1.0     # 每次请求间隔，别给人家 wiki 添负担


def query(titles):
    params = {
        "action": "query", "format": "json", "redirects": 1,
        "prop": "categories", "cllimit": "max", "clshow": "!hidden",
        "titles": "|".join(titles),
    }
    pages, redirects, normalized = {}, [], []
    cont = {}
    while True:
        url = API + "?" + urllib.parse.urlencode({**params, **cont})
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        q = data.get("query", {})
        normalized += q.get("normalized", [])
        redirects += q.get("redirects", [])
        for p in q.get("pages", {}).values():
            slot = pages.setdefault(p["title"], {"missing": "missing" in p or "invalid" in p, "cats": []})
            slot["cats"] += [c["title"].split(":", 1)[1] for c in p.get("categories", [])]
        if "continue" not in data:
            break
        cont = data["continue"]
        time.sleep(PAUSE)
    return pages, {n["from"]: n["to"] for n in normalized}, {r["from"]: r["to"] for r in redirects}


def main():
    setup_stdout()
    glossary = load_json(config.GLOSSARY) or {}
    cache = {} if "--refresh" in sys.argv else (load_json(CACHE) or {})
    todo = [k for k in glossary if k.lstrip("!") not in cache]
    # wiki 标题不能含这些字符，直接记为无页面
    bad = set("#<>[]|{}")
    for k in [k for k in todo if bad & set(k)]:
        cache[k.lstrip("!")] = {"page": None, "cats": []}
    todo = [k.lstrip("!") for k in todo if not bad & set(k)]
    todo = list(dict.fromkeys(todo))
    print(f"术语 {len(glossary)} 条，待查 {len(todo)} 条")

    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        try:
            pages, norm, redir = query(chunk)
        except Exception as e:
            print(f"  [警告] 第 {i // BATCH + 1} 批失败，已缓存的先保存：{e}")
            break
        for term in chunk:
            title = norm.get(term, term)
            title = redir.get(title, title)
            p = pages.get(title)
            if p is None or p["missing"]:
                cache[term] = {"page": None, "cats": []}
            else:
                cache[term] = {"page": title, "cats": sorted(set(p["cats"]))}
        save_json(CACHE, cache)
        print(f"  {min(i + BATCH, len(todo))}/{len(todo)}")
        time.sleep(PAUSE)

    found = sum(1 for v in cache.values() if v["page"])
    print(f"缓存 {len(cache)} 条，wiki 有页面 {found} 条 → {os.path.relpath(CACHE, config.BASE_DIR)}")


if __name__ == "__main__":
    main()
