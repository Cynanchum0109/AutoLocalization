# 边狱公司文本翻译工作区 | Limbus Company Translation Workspace

翻译由 **Claude Code 在会话里完成**，脚本只负责：扫描游戏目录变更 → 出批次 → 校验合批 → 生成成品文件。
不再调用任何翻译 API。

## 玩家安装

补丁包发布在 [Releases](../../releases/latest)，下载最新的 zip。

1. 双击 `install.bat`（或右键 `install.ps1` → 用 PowerShell 运行）。
2. 脚本自动查找 Steam 里的 Limbus Company 安装目录并安装；
   若自动查找失败，会提示手动输入游戏安装路径（形如 `D:\Steam\steamapps\common\Limbus Company`）。
3. 两种方式都失败时，把压缩包里的 `LLC_zh-CN` 文件夹手动复制到
   `Limbus Company\LimbusCompany_Data\Lang`（Steam 右键边狱巴士 → 浏览本地文件可找到这一层），
   选择替换所有文件。
4. 安装完成后重启游戏。

**需先装过零协会汉化版本再装本补丁；零协更新后会自动覆盖本补丁。**

## 译者 / agent 工作流程

**完整说明见 [`TRANSLATION_GUIDE.md`](TRANSLATION_GUIDE.md)**（唯一真本，规则只改那一份），
本轮翻哪些文件、做到哪了见 [`PROGRESS.md`](PROGRESS.md)。一句话流程：

```bash
python scan.py                                  # 看游戏更新了什么
python batch_next.py --size 60                  # 取一批 todo
#   → 填 out/slots/<slot>/batch_answers.json
python batch_merge.py                           # 校验 + 入库，格式错整批拒绝
python apply.py                                 # 每翻完一个文件出一次成品 → Workplace/translated/
python pack.py <附件名>.zip                     # 发布时打玩家安装包 → out/
```

## 状态含义

**只翻中文没有、英文有的部分。** `StoryData/`、`PersonalityVoiceDlg/` 按文件判断（中文侧缺整个文件才翻），
其余按 JSON 条目判断（中文侧缺这个条目才翻）。只有 `todo` 进队列，其余状态仅作统计。

| 状态 | 含义 | 是否进队列 |
|---|---|---|
| `todo` | ZH 缺这个文件（按文件的目录）/ 缺这个条目（其余目录） | 是 |
| `ours` | 我们译过（英文原文之后改了也不重翻） | 否 |
| `official` | ZH 已有中文 | 否 |
| `has_zh` | ZH 已有该文件/条目，只是缺这个字段 | 否 |
| `same_as_en` | ZH 已有，但与 EN 一模一样 | 否 |
| `zh_placeholder` | ZH 已有，但没有汉字（韩文占位等） | 否 |
| `ignored` | 记在 `out/ignore.json` 的 todo，永久跳过 | 否 |

## 文件说明

| 路径 | 作用 |
|---|---|
| `config.py` | 路径、翻译范围、字段规则 —— 唯一配置入口 |
| `limbus/walk.py` | 遍历文件、生成 key、判断哪些字段要翻 |
| `limbus/glossary.py` | 术语表索引（长词优先 + 词边界正则） |
| `limbus/tm.py` | 翻译记忆库：官方已译过的同一句原文直接复用（3 万条，缓存 out/tm.json） |
| `limbus/fmtcode.py` | 格式标签识别与校验（标签名硬编码，清单见 `FORMAT_TAGS.md`） |
| `limbus/jsonio.py` | JSON 读写（剥 BOM，写出对齐官方：utf-8 无 BOM / LF / indent=2） |
| `scan.py` | 扫描 + 快照 diff + 待办清单 |
| `batch_next.py` | 出批次 |
| `batch_merge.py` | 校验 + 合批 |
| `apply.py` | progress → 成品文件 |
| `pack.py` | 打玩家安装包（校验结构） |
| `Installer/` | 安装包外壳：install.bat / install.ps1 / README.txt，`LLC_zh-CN/` 由 pack.py 生成 |
| `check.py` | 全库体检 |
| `out/progress.json` | **我们自己的译文库，唯一真相** |
| `out/snapshot.json` | 上次 accept 的 EN 原文指纹（变更检测基线） |
| `out/ignore.json` | 永久跳过的条目 |
| `glossary/glossary.json` | 术语表（不入 git） |
| `glossary/categories.json` | 术语分组：所属章 `chap` + 类型 `cat`（`by`/`chap_by: 人工` 为手改，重跑不覆盖） |
| `glossary/categorize.py` | 生成分组 + 出处索引 `term_where.json`；文件名→章节的对照写在 `source_label` |
| `glossary/fetch_wiki_categories.py` | 从英文 wiki 拉页面分类，缓存供 categorize.py 判类型用 |
| `term.py` | 术语查找：中英互查、`--chap` 按章、`--cat` 按类型、`--where` 按出处、`--set`/`--set-chap` 手改、`--check` |

## 格式标签

见 `FORMAT_TAGS.md`。一句话版本：`<color>` `<style>` `<mark>` `<noparse>` 和 `{占位符}`
必须一一对应；`<i> <b> <size> <ruby>` 等排版标签**原样照抄，不丢也不加**（只有良秀注音 `<ruby=Yoshihide>` 例外）；
`<Uh...>` `[INITIATING SITE BURIAL.]` 这类尖/方括号是**引号不是标签**，内容要翻、括号保留。

## 机制文本（`_mech` scope）

技能文件是嵌套结构，key 的第三段用路径表示：

```
_mech/Skills_Abnormality-BossRaid.json#501905#levelList[0].coinlist[2].coindescs[4].desc
```

机制文本的 `[Sinking]` `[WhenUse]` 是**关键词 ID，保留英文不译**（`desc`/`summary`/`flavor` 字段），
但 `name` 字段里的方括号是名字的一部分，要翻：`Shade of Reflection [Rouge]` → `映射[红色]`。
关键词只查「有没有」不查出现几次 —— 官方常把重复提及合并成一句更顺的中文。

## key 格式

```
<scope>/<文件名>#<id>#<字段>
StoryData/1D101A.json#0#content
_root/BattleSpeechBubbleDlg.json#battle_speechbubble_cromer_1#dlg
```

同一文件里 id 重复时（音效条目常年用 `id=-1`），第 2 个起加 `~n`：`...#-1~2#content`。

## 不翻的字段

`id` / `model`（StoryData 里的角色标识，官方 ZH 保持韩文）/ `d`。
韩文内容（气泡文件的 `desc`）与纯符号（`teller` 里的 `@!($&$2w!`）自动跳过。

---

欢迎 bilibili 私聊 白前Cynanchum，不作技术方面回答。
