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

## 当前范围（tier 0）

| scope | 内容 |
|---|---|
| `StoryData/` | 剧情对话与旁白（922 个文件） |
| `PersonalityVoiceDlg/` | 人格语音台词（186 个文件） |
| `_root/BattleSpeechBubbleDlg*.json` | 战斗气泡台词 |
| `_root/ScenarioModelCodes-AutoCreated.json` | 角色名 / 别名表 |
| `_mech/*-BossRaid.json` | BossRaid 的技能 / 被动 / Buff / 关键词 / UI |

其余根目录文件（技能、被动、Buff、事件、UI 等约 890 个）暂不处理，等剧情和语音之后再排优先级。
范围在 `config.py` 的 `TIER0_*` 里改。

## 基线约定

**当前 `LLC_zh-CN` 版本视为完备基线。** 基线里没翻的条目（ZH 缺条目、ZH 与 EN 一模一样的 390 条，
如 `LCCB`、`Mon3tr`、`Gesellschaft`）已记入 `out/ignore.json`，**以后不再翻**。
只有官方改写了这些条目的英文原文，它们才会重新进入队列。

因此日常待办 = **游戏更新带来的增量**：新文件、新条目、被官方改写的原文。

## 日常流程

```bash
# 1. 游戏更新后，看官方改了什么
python scan.py
#    → out/changes/<时间>.md   新增 / 改写 / 删除 的清单
#    → out/state.json          待办条目

# 2. 取一批待译文本
python batch_next.py --size 60
#    → out/batch_pending.json

# 3. Claude Code 读 batch_pending.json，逐条填 translation，
#    存成 out/batch_answers.json

# 4. 校验并入库
python batch_merge.py
#    格式码丢失 / 空译文 → 整批拒绝，progress.json 不会被污染

# 重复 2-4 直到 state.json 清空

# 5. 生成成品
python apply.py            # → Workplace/translated/**
python apply.py --install  # 产出并直接拷进游戏 LLC_zh-CN（覆盖前自动备份）
python check.py            # 全库体检：格式码、漏译、术语不一致

# 6. 确认看过本次变更后，推进基线
python scan.py --accept
```

## 状态含义

| 状态 | 含义 | 是否进队列 |
|---|---|---|
| `todo` | ZH 侧没有（缺文件 / 缺条目 / 缺字段） | 是 |
| `stale` | 我们译过，之后官方改了英文原文 | 是 |
| `outdated_official` | 官方有中文，但英文原文在上次基线后被改过 | 手动 `--status outdated_official` |
| `same_as_en` | ZH 与 EN 一模一样 | 手动 |
| `ignored` | 基线里就没翻，按约定永久跳过 | 否 |
| `ours` / `official` | 已译且原文未变 | 否 |

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
| `check.py` | 全库体检 |
| `out/progress.json` | **我们自己的译文库，唯一真相** |
| `out/snapshot.json` | 上次 accept 的 EN 原文指纹（变更检测基线） |
| `out/ignore.json` | 永久跳过的条目 |
| `glossary/glossary.json` | 术语表（2612 条，不入库） |

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
