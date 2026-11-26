# 当前进度

> 这是**当前状态**，每翻完一个文件就改写对应小节，不追加流水账（规矩见 `TRANSLATION_GUIDE.md`「进度记录」）。
> 2026-09-24 以前的完整记录在 `docs/archive/PROGRESS_archive.md`，只作历史参考。

更新：2026-11-25

## 本轮范围

新人格：黑派楼层经理 李箱（10117，B3F）、红派楼层经理 格里高尔（11217，B2F 线团之巢）。
本轮开工时 `tools/scan.py` 共 2020 条 todo（基线未 `--accept`）：

- StoryData：`P10117.json`（192）、`P11217.json`（162）
- PersonalityVoiceDlg：`Voice_Yisang_Contem_10117.json`、`Voice_Gregor_Contem_11217.json`（各 48）
- `_root`：`BattleSpeechBubbleDlg.json`（18）
- `_tailmech`：Skills_personality-01/12、Skills_Enemy-schema、Passives(_Enemy-schema)、Bufs/BattleKeywords（含 schema、Synergy）等
- `_tail`：`LimtochessUI.json`（941）、`TutorialMainUIText.json`（119）、`SchemaCraftChoice.json`（59）、`Announcer_Overseer_60.json`（32）及杂项

## 已完成

- `StoryData/P10117.json`（slot a，192 条，已 apply）。李箱=B3F 黑派楼层经理，对杜布瓦称「你」，书面腔不文言。
  缩写梗（EN 首字母 `<size=150%>` 放大、KR 无空格连写）：译成无空格连写短语，**每个词首字放大**，`<size>` 个数与原文一致。
  自拟：Leather Glove 皮革手套、hidescraper 剥皮匠（已记台账）；eyeballs 眼球（官方）、B2F/B3F 照官方留英文。
- `StoryData/P11217.json`（slot a，162 条，已 apply）。格里高尔=B2F 红派楼层经理，随和口吻。
  赤红之神的 He/Him 一律译「那位」；漆黑之神用「他」。yearning=渴望、shroud=寿衣、Golden Shroud 黄金寿衣、
  Things of eld 古老之物（官方）；自拟 two-ply 双股、fitting 配件（已记台账）。
- **StoryData 全部完成。**
- `PersonalityVoiceDlg/Voice_Yisang_Contem_10117.json`、`Voice_Gregor_Contem_11217.json`（各 48，slot a，已 apply）。
  desc 照官方语音文件惯例（Deployment=人格出战，Extra Conditions Fulfilled=EX CLEAR战斗胜利）。
  李箱缩写梗同剧情做法；square（KR 사각）=四方。格里高尔：Crimson Voice 赤红之声（自拟，已记台账），He=那位；Dyehouse 染色室。
- `_root/BattleSpeechBubbleDlg.json`（18，slot a，已 apply）。
- `_tailmech` 全部（slot a，已 apply）。官方机制句式照 `linetm` 逐行对齐；Bufs/Bufs-schema/Bufs_Synergy 复用 BattleKeywords 同 key 译文。
  人格名格式照官方 `高级定制::黑派 B3F 干燥室 李箱`（中间有空格）。黑云会敌人：峰=第三组组长（KR 제3조장）。
  已记台账：Battō Shisei 拔刀架势、Ready to Draw 拔刀准备、Kumogiri 云切、Schemacraft 图式构筑、Thread Tether 相连之线 等。
- `_tail` 全部（slot a，已 apply）。
  - 杂项小文件：GachaTitle/IAPProduct 照官方「新人格定向提取 - …」「发布纪念礼包」格式；Yisang Exchange=[理想]兑换（官方）；
    Personalities title 照官方两行格式 `高级定制::
黑派 B3F 干燥室`（原文 3 个换行，有警告，按官方格式处理）。
    MirrorDungeonRentalName 用官方 蜘蛛巢、SynergyKeyword 用官方 第四根火柴之焰（与术语表旧译 蜘蛛屋/终末火柴之光 不同，以官方现行为准）。
  - `Announcer_Overseer_60`：管制员，敬语口吻。句末全大写标签照官方 `BattleSpeechBubbleDlg-a1c10p2` 与 RPG `RPGSystem/rpg-loc-dialogue-floor-b3-b`（管制员 41 句）的格式：无任何标签或标点标记，句号后接无标记短语，多为动宾式（部署罪犯、补充人员、转移所有权、确认违反规定、再收监；与 RPG 重合的标签照官方：刺激挑战欲望、感叹与称赞、疑问产生、观察中）；prisoner 在此语境用官方的「罪犯」。
    통제/control 统一译「管制」（含 P10117、李箱语音），不用「管控」。
  - `SchemaCraftChoice` / `TutorialMainUIText` / `LimtochessUI`（图式构筑玩法 UI）：新词已记台账——
    Schema 图式、Representation 表象、Schema Deformation 图式扭曲、Craftpower 构筑力、Obstacle 苦难（官方 OZ「碍事的家伙」不合语境未用）、
    Sliver 碎片/通用碎片、Starting/Manual/Randomized Team 初始/手动/随机编队、Defense Strat. 防御策略、Backup Identity 候补人格、
    Reshuffle 刷新次数、Pack 卡包、Temptation 诱惑、Cost 费用。沿用官方：Respite 喘息、Boss 头目、Regular/Elite Encounter 常规/精锐遭遇战、
    Canard 传闻、Urban Myth/Legend 都市怪谈/传说、Night 深宵。LimtochessUI 人格专属守备条件里的关键词名全部按官方 Bufs/Skills 名称。
  - `LimtochessUI` 两条 EN 占位符与 KR 不一致（`final_damage_row` 出战次数 EN 写成 `{0}`、`event_hardship_stacked` EN 写死 `1`），合批硬规则要求同 EN，已照 EN。

## 进行中

无。`tools/scan.py` 2026-11-25：**todo 0**，ours 2020。产物在 `Workplace/translated/`，未 install，未 commit，基线未 `--accept`。

## 待用户确认

- Ruminating：官方李箱台词 반추 一律译「反刍」，本轮照用；如要改「沉思」需用户拍板。
- （`glossary/glossary.json` 按用户决定继续不入 git，靠 `glossary/glossary.json.bak-*` 备份。）
