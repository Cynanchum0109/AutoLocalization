# Limbus Company 术语表清洗参考文档

> 本文档记录术语表（glossary.json）的清洗原则与方法，供后续提取/清洗复用。

---

## 术语表结构

- **文件**：`glossary.json`，UTF-8，`indent=2`，`ensure_ascii=False`
- **格式**：`{"EN键": "ZH值", ...}`，有序 dict
- **受保护区**：第 1 条（`"Gnome"`）至 `"Udjat"` 共 262 条——人工校对完毕，**任何脚本均不得修改**
- **自动区**：`"Udjat"` 之后的所有条目——自动提取，可被过滤脚本处理

---

## 哪些不应进入术语表

### R1. ALL-CAPS 章节标题句
- **特征**：≥4 词，>85% 字母为大写
- **示例**：`"IN WHICH IS EXPLORED LIMBUS COMPANY'S NOT-EXACTLY-FIRST ALLIANCE WITH A WING"`
- **处理**：直接删除

### R2. 叙述性标题句
- **特征**：以 `The Tale of / A Tale of / In Which / Of the / Wherein / Of how` 等开头，≥5 词
- **示例**：`"The Tale of a Great Fixer Who Once Reached for The Dream"`
- **处理**：直接删除

### R3. 编号变体地名
- **特征**：`[基础地名] 2F / 3F / 4F` 等，ZH值末尾带数字/楼层标志
- **示例**：`"Yong-jin Building 2F"`, `"Yong-jin Building 4F"`
- **处理**：
  - 若基础地名已在词典：删除所有编号变体
  - 若基础地名不在词典：用 ZH 最长公共前缀添加基础地名，再删除编号变体

### R4. 描述性 NPC 名（同类 ≥2 个变体）
- **特征**：2-3 词，末词为通用角色名词（Audience/Candidate/Attendant/Villager 等），且该末词有 ≥2 个变体
- **示例**：`"Stunned Audience"`, `"Suspicious Audience"`, `"Gossiping Audience"`
- **处理**：删除所有变体（基础角色名词如 `"Audience"` 本身若无独立含义也可删）
- **通用角色名词列表**：Audience, Candidate, Attendant, Spectator, Crowd, Onlooker, Bystander, Passerby, Villager, Civilian, Resident, Patient, Inmate, Thug, Goon, Mob, Rioter, Peasant, Commoner, Prisoner, Refugee

### R5. 地名子集合（已有基础名 + 常见场所后缀）
- **特征**：`[已在词典的基础地名], [Hallway/Corridor/Lab/Office/Ward/...]`
- **示例**：`"LCE Research Team Broadcast Sector"`, `"LCE Research Team Hallway"`, `"LCE Research Team Laboratory"`
- **处理**：若去掉后缀后的基础名已在词典，则删除复合地名
- **常见场所后缀**：Hallway, Corridor, Lobby, Lounge, Waiting Room, Meeting Room, Control Room, Entrance, Exit, Laboratory, Lab Unit, Security Unit, Broadcast Sector, Research Sector, Storage, Quarantine Zone, Ward, Bay, Cafeteria, Office

### R6. 现有术语的组合（ZH值可递归分解）
- **特征**：某条目的 ZH值可在空格（` `）或游戏专用分隔符（` - `）处拆分，
  拆分出的每一段均已是词典中某条目的 ZH值（或可进一步递归拆分），
  且每段长度 ≥ 2（` - ` 右侧名称允许 ≥ 1 字符，因角色名可能极短如"莲"）
- **示例（空格型）**：
  - `"W. Faust"` → `"W公司 浮士德"` = `ZH("W Corp.")` + `ZH("Faust")`
  - `"Kurokumo Hong Lu"` → `"黑云会 鸿璐"` = `ZH("Kurokumo Clan")` + `ZH("Hong Lu")`
  - `"The Thumb Apprentice"` → `"拇指 子辈"` = `ZH("The Thumb")` + `ZH("Apprentice")`
- **示例（" - " 分隔符型，递归）**：
  - `"The Thumb Apprentice - Lucio"` → `"拇指 子辈 - 卢西奥"`：左侧"拇指 子辈"可再分解，右侧"卢西奥"是独立条目
  - `"The Ring Nursefather - Callisto"` → `"环指 父辈 - 卡利斯托"`：同上
  - `"Lobotomy E.G.O::Red Sheet - Marile"` → `"脑叶公司E.G.O::朱符 - 马里勒"`
- **处理**：删除复合条目（翻译时可由组件分别查询后拼接得到）
- **脚本执行顺序**：
  1. `phase3_compound_filter.py` — ZH值空格分解（有分隔符型）
  2. `phase3b_compound_filter.py` — ZH值递归分解（含 " - " 分隔符、左侧递归型）
  3. `phase4_combined_filter.py` — **EN侧拆分 + ZH值精确验证**（无分隔符型，最后兜底）
     - 对 EN键 在词边界尝试 2段/3段拆分，所有段均须是词典中已有的 EN键
     - 用空格/无分隔/"` - `" 拼接各段的 ZH值，与当前 ZH值精确比对
     - 捕获如 `"Slash Protection"→"斩击守护"` 这类 ZH 无空格拼接型
     - **需迭代运行至收敛（输出"发现 0 条"为止）**
- **特别注意**：
  - Sinner ID 皮肤名（`[势力缩写] [罪人名]`）也属于此类。若势力 ZH 不在词典中，用罪人 ZH 后缀匹配检测
  - 若 ZH 右侧的人名不在词典中（如"盐见夜" / Shiomi Yoru），则保留该复合条目，因为无法拆分推导
  - **运行 phase4 后须再运行一次确认归零**，因为移除复合条目后其 EN键 消失，可能使原先依赖它的更高层复合变得可检测

### R7. 对话/剧情句子（非术语）
- **特征**：完整句子，含第一/二人称、标点、省略号等
- **示例**：`"You know your stuff"`, `"We're the 'samples'."`, `"I used too much power"`
- **处理**：删除

### R8. 系统占位符与格式残留
- **特征**：`#N Deployment Effect`、含换行符但无对应 ZH 换行、含 HTML 标签的键、含韩文字符的键
- **处理**：删除

### R11. 换行符拼接的多词组条目（EN键或ZH值含 `\n`）
- **特征**：EN键（或ZH值）含换行符 `\n`，表示两个及以上词组被拼接为单条术语
- **示例（EN含换行）**：
  - `"Seven Assoc.\nSouth Section 6"` → `"Seven协会\n南部6科"`：两个独立术语拼接
  - `"Blade Lineage\nMentor"` → `"剑契组\n头领"`：势力 + 角色职衔
  - `"E.G.O [HE]\nUpgrade Pack"` → `"E.G.O[HE]\n成长组合包"`
- **示例（ZH含换行，EN干净）**：
  - `"Rosespanner Workshop Fixer"` → `"玫瑰扳手工坊\n收尾人"`：ZH格式残留换行
  - `"Lobotomy E.G.O::Lamp"` → `"脑叶公司E.G.O::\n目灯"`：`::` 后换行
- **处理**：
  1. **EN含换行**：按 `\n` 拆分 EN 和 ZH，将每对 `(EN_part, ZH_part)` 作为独立术语加入词典（若该 EN_part 已存在则跳过），然后删除复合条目
     - 部件数相等：直接逐对对齐
     - EN 段数 > ZH 段数（如 Full Moon 202X Commemorative：EN=3, ZH=2）：
       若 EN 以 `Full Moon` 开头，合并前 N 段 EN；其他情况合并后 N 段 EN
     - ZH 段数 > EN 段数（如 R Corp. 4th Pack 系列：EN=2, ZH=3）：
       合并前 N 段 ZH
  2. **ZH含换行（EN干净）**：将 ZH 中的换行符替换为正确分隔符（`::` 后用空字符，其余用空格），再通过 phase3b/phase4 检测是否为复合条目
- **脚本**：`phase5_newline_split.py`（处理 EN 含换行），随后运行 ZH 换行归一化 + phase3b + phase4
- **执行后**：须再跑 phase3b → phase4（至收敛），因拆出的新术语可能暴露更多复合条目

### R9. 截断文本碎片
- **特征**：`"ies..."`, `"Yo..."`, `"ool..."`——明显是被截断的文字，无实际含义
- **处理**：删除

### R10. 编号续集变体
- **特征**：`"[已有术语] 2"`, `"[已有术语] 3"` 等（章节标题编号变体，非楼层）
- **示例**：`"Pirates 2"`, `"The Diary 2"`, `"Abikyōkan 2"`
- **处理**：删除（保留无编号的基础版本）

### R12. 核心词包含条目
- **特征**：自动区条目的 EN键（以词/词组为单位）含有前264条核心区某 EN键（长度≥3字符），或 ZH值以子串形式含有前264条核心区某 ZH值（长度≥2字符）
- **示例**：`"Lobotomy Corporation Central Command"` EN含 `"Lobotomy Corporation"`；`"Quiet Corridor of the Middle"` ZH含 `"中指"`
- **处理**：直接删除（翻译时可由核心词查询推导）
- **脚本**：`clean_compounds.py` 步骤6，常数 `N_CORE = 264`

### R13. ZH首字前缀重复
- **特征**：多条自动区条目的 ZH值 以相同的 **≥3个连续汉字** 开头（即 ZH开头的连续CJK字符串的前3字相同）
- **示例**：
  - `"Evaluation Arena 1F"→"评审场内部 1层"` / `"Evaluation Arena 1F - Lab Ruins"→"评审场1层 实验室废墟"` / `"Evaluation Arena Interior B1"→"评审场内部 地下1层"` — 同组，共享前缀 `"评审场"`
  - `"Refracted Sin"→"折射的罪孽"` / `"Refracted Mind"→"折射的理智"` 等80条 — 同组，共享前缀 `"折射的"`
- **处理**：同一前缀组内只保留 **EN键最短** 的条目（同长取先出现者），删除其余
- **脚本**：`clean_compounds.py` 步骤7，函数 `remove_zh_prefix_duplicates`

---

---

## 清洗流程总结（本次执行顺序）

| 步骤 | 脚本 | 说明 | 结果 |
|------|------|------|------|
| 0 | `clean_glossary.py` | 去除换行/HTML/韩文键、明确错误条目 | 初步清理 |
| 1 | `filter_glossary_by_wiki.py` | 与 wiki 对照，移除低置信度条目，去重 | 保留有 wiki 依据的条目 |
| 2 | `rededup_glossary.py` | 修复去重优先级（no_brackets + is_ascii + -length），恢复被错误移除的条目 | 77 条换回正确形式 |
| 3 | `phase1_filter.py` | 规则过滤 R1-R5 | -175 +8 → 6188 条 |
| 4 | LLM 审查（6 chunks） | Claude 子代理逐条审查，识别非术语 | 472 候选 |
| 5 | `apply_llm_removals.py` | 应用 LLM 结果，保护核心词 | -465 → 5723 条 |
| 6 | `phase3_compound_filter.py` | ZH值分解法检测复合条目 | -55 → 5647 条 |
| 7 | 手动补充（Sinner ID 皮肤） | 基础名不在词典的 ID 皮肤专项移除 | -5 → **5642 条** |
| 8 | `phase3b_compound_filter.py` | 递归 ZH 分解（含 " - " 分隔符型） | -13 → 5629 条 |
| 9 | `phase4_combined_filter.py` × 2 | EN侧拆分 + ZH验证，迭代至收敛 | -34 → **5403 条** (含多轮) |
| 10 | `phase5_newline_split.py` | 拆分所有 EN含\n 的复合条目，提取独立术语 | -113 +93 → 5383 条 |
| 11 | ZH换行归一化（内联脚本） | 修复 ZH 值中的格式残留换行符 | 修复 10 条 |
| 12 | `phase3b_compound_filter.py` | 补扫新暴露的复合条目 | -25 → 5351 条 |
| 13 | `phase4_combined_filter.py` × 2 | 再次迭代至收敛 | -0 → **5351 条** |
| 14 | `clean_compounds.py`（统一脚本） | 合并 phase3/3b/4/5，新增 R3b/R4b/R5b + 地支支持 | **5072 条** |
| 15 | `clean_compounds.py` 步骤3-5 | 等级变体(+/++)、序数词变体、Heishou地支修复 | -228 → **4843 条** |
| 16 | `clean_compounds.py` 步骤6（R12） | 核心词包含检测（前264条 EN+ZH子串） | -651 → **4115 条** |
| 17 | `clean_compounds.py` 步骤7（R13） | ZH首字前缀去重（≥3汉字前缀，保留最短EN） | -590 → **3519 条** |

---

## 去重优先级（决定同 ZH 多个 EN 键保留哪个）

优先级从高到低：
1. `in_wiki`：EN键规范化后在英文 wiki 存在
2. `no_newline`：EN键不含换行符
3. `no_brackets`：EN键不含 ASCII 方括号注释 `[xxx]`（wiki 标题注释形式）
4. `is_ascii`：EN键为纯 ASCII（无 ō ū ā 等特殊调号字符）
5. `-length`：EN键越短越优先

---

## LLM 审查 Prompt 设计要点


---

## 注意事项

1. **保护区不可动**：受保护区（Udjat 及之前）只读。任何脚本在写入前必须检查 pivot。
2. **去重先于过滤**：去重逻辑应在规则过滤之前执行，避免过滤后的词典不完整影响去重判断。
3. **ZH分解法的局限**：若复合条目的某一组件本身不在词典中（如"Liu Association"未单独收录），ZH分解法无法检测，需要通过 Sinner ZH 名后缀匹配补充。
5. **Wiki 对照缓存**：wiki 标题缓存在 `wiki_titles_cache.json`，用于 `filter_glossary_by_wiki.py` 和 `rededup_glossary.py`。
