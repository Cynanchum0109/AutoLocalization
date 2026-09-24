# 翻译进度记录

每完成一个文件/批次后更新本文件，方便随时接手。

> **2026-09-23：译文库重置。** `out/progress.json` 已不存在，本文件下方
> 「已完成」的全部记录**只作历史参考，不代表当前工作区状态**——那些译文已经没了。
> 新一轮从空库重新开始：`scan.py` 判定的 todo/stale 就是实际要做的量，
> 不要因为下面写着「已完成」就跳过某个文件。
> 完成记录从本行以下的新小节重新计起。

## 阶段顺序（按用户指定）

1. Story（`StoryData/`，排除 `EN_P*` 开头，按文件名顺序；起点已改为 S1000B，见下方说明）
2. Model（`EN_ScenarioModelCodes-AutoCreated.json`）—— **已完成**
3. Bubble（`EN_BattleSpeechBubbleDlg*.json` 系列）
4. RPG新玩法（游戏未更新，文件未知，待更新后重新 `scan.py` 确认范围）
5. 事件相关（`EN_*Events*` / `EN_Event*Text` / `EN_AbEvents*` / `EN_ActionEvents*` 等，范围待枚举）
6. 其它全部（根目录剩余文件 + PersonalityVoiceDlg 等）

## 重要规则变更（2026-09-16，最新在最上面）

- **Story 范围再收窄**：只做文件名以 **S10** 开头的文件——S1000B~S1016B、S101B、S109B、S1060B~S1062B 这些。
  其余 S2xx/S3xx/S7xx/S8xx/S9xx 系列，以及 3D/7D/E 系列、S001A，全部不用管（不管有没有翻过，都跳过）。
  这条规则**只适用于 Story 阶段**，不影响 Model/Bubble/事件/其它阶段的范围。
  待办清单里凡是非 S10 开头的文件，直接忽略，不用 batch_next 拉取。

- **起点改了**：3D101A、3D102A（第3章开头两个文件）用户决定不翻，已撤销：
  从 `out/progress.json` 删除对应条目、游戏目录用 `Workplace/backup_*` 还原原文件、
  `Workplace/translated/` 里的产物也删了。`scan.py --accept` 确认过 `ours` 归零。
  Story 改从 **S1000B.json** 开始往后翻。
- **不再自动装游戏**：以后 `apply.py` **不带 `--install`**，只出到 `Workplace/translated/`，
  游戏目录由用户自己拷贝。
  例外：S1000B.json 是在改规矩*之前*用 `--install` 装进游戏的，已生效，没有回退。
  Model 文件（ScenarioModelCodes）开始就是纯 `apply.py`（无 install），之后同理。
- **待确认**：3D301B / 3D309A / 7D112A / E001X 等 E 系列 / S001A 这些排在 S1000B 之前的文件
  要不要也跳过、只做 S10xx 及以后——还没问清楚，下次开工前先问用户。

## 当前状态

- 当前阶段：**Bubble 阶段已完成，转入 RPG 阶段**（Story S10范围✅、Model✅、Bubble✅）
- **RPG 阶段发现**：`Skills_Abnormality-BossRaid.json`/`Passives-BossRaid.json`/`Bufs-BossRaid.json`/
  `BattleKeywords-BossRaid.json`/`BossRaidUI-4.json` 这5个 `_mech` 机制文件已经在源数据里出现（tier0 scope
  自带），文件名带 BossRaid，判断就是用户说的"还没更新的RPG玩法"对应的文本——数据已经在，可以直接开始翻，
  不用等游戏正式更新。**机制文本规则**：desc/summary/flavor 里的 `[Xxx]` 是关键词ID，必须保留英文，
  与剧情文本的方括号规则相反（那边是要翻译的）。
  - 2026-09-17 00:10 `_mech/Skills_Abnormality-BossRaid.json`（162条译文，全部命中 `official_zh` 翻译记忆库
    直接照抄，分6批翻完，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏。RPG 剩余4个 `_mech` 文件：Passives/Bufs/BattleKeywords/BossRaidUI-4，继续做）
  - **RPG 阶段到此全部完成**：Passives-BossRaid.json / Bufs-BossRaid.json / BattleKeywords-BossRaid.json /
    BossRaidUI-4.json 这4个文件检查后发现没有待译条目（已经是 same_as_en 之外的状态，或者内容本来就没有
    需要翻的），不用管。
  - **当前剩余范围盘点（2026-09-17 00:11 scan 快照）**：841条待译，分布在67个文件：
    - PersonalityVoiceDlg（P10xxx/PC0xx/Voice_*，约517条）——tier0已扫描，可直接开工，**下一步就做这个**
    - 非S10开头的Story文件（S9991B/S951B/S203B等，约300+条）——按既定规则**永久跳过**，不用管
    - E系列StoryData遗留文件（E519A/E513A/E001X等）——用户已确认这批"3D301B~S001A"先不管，**跳过**
    - 根目录真正的 Event 文件（`EN_AbEvents-*`/`EN_AbEventsResultLog-*` 等）——**还没进 tier0 扫描范围**，
      需要先在 config.py 的 TIER0_DIRS/TIER0_ROOT_FILES 里加进去才能 scan 到，PersonalityVoiceDlg 做完后再处理
  - 2026-09-17 00:15 StoryData/P10816.json（143条译文，以实玛利个人剧情：红色精品店/杜博阿/黑色精品店戏份，
    分5批翻完，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；新增术语：Boutique du Rouge→红色精品店，Maison du Noir→黑色精品店，Dubois→杜博阿，Kaki→卡基）
  - 2026-09-17 00:19 StoryData/P10416.json（142条译文，良秀个人剧情：漆黑者鞋履厅/杜博阿买鞋+大战赤红者鞋履厅戏份，
    分5批翻完，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；新增术语：Le Noir Footwear Hall→漆黑者鞋履厅，Rouge Footwear Hall→赤红者鞋履厅，
    Four-legs/Two-legs/One-leg→四腿/两腿/一腿）
  - 2026-09-17 00:21 StoryData/P10705.json（72条译文，希斯克利夫独白：技术解放联盟往事回忆，全部是
    teller/title字段、命中official_zh译文记忆库直接照抄，分3批翻完，apply（无install）+ check 通过（无硬伤）
    + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-17 00:24 PersonalityVoiceDlg/Voice_Ishmael_Contem_10816.json（48条译文，以实玛利化身为红色精品店设计师
    的战斗语音，分2批翻完，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏；与P10816保持术语一致：挚爱之人/Le Rouge赤红者/Le Noir漆黑者/"声音"）
  - 2026-09-17 00:26 PersonalityVoiceDlg/Voice_Ryoshu_Contem_10416.json（48条译文，良秀化身为漆黑者鞋履厅店主
    的战斗语音，分2批翻完，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏；S.M.L./U.S./E.W./S.A.P./T.A.P./B.E.等缩写谐音梗原样保留未翻译）
  - 2026-09-17 00:27 StoryData/P10116.json（11条译文，全部是"LCE"部门代号的title字段，与LCD/LCB/LCCB
    同类规则保留英文不翻，1批翻完，apply（无install）+ check 通过（无硬伤，仅软警告"不含中文"符合预期）
    + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
- **Story 范围已收窄为只做 S10 开头文件**（见上方规则变更），下面清单里 ~~删除线~~ 的都是不用管的（撤销/不在S10范围内）：
  ~~3D101A~~ ~~3D102A~~ ~~3D301B~~ ~~3D309A~~ ~~7D112A~~ ~~E001X~~ ~~E003I3~~ ~~E405A~~ ~~E406B~~
  ~~E501B~~ ~~E509B~~ ~~E512A~~ ~~E513A~~ ~~E519A~~ ~~E616B~~ ~~E702B~~ ~~E703B~~ ~~E914B~~ ~~E923B~~ ~~S001A~~ →
  **S1000B✅** → **S1001B✅** → **S1002B✅** → **S1003B✅** → **S1004B✅** → **S1005B✅** → **S1008B✅** → **S1009B✅** →
  **S1010B✅** → **S1011B✅** → **S1012B✅** → **S1013B✅** → **S1014B✅** → **S1015B✅** → **S1016B✅** → **S101B✅** → **S1060B✅** → **S1061B✅** → **S1062B✅** → **S109B✅**
  **Story阶段（S10范围）全部完成，进入 Bubble 阶段。**
  ~~S203B~~ ~~S204B~~ ~~S205A~~ ~~S205B~~ ~~S206B~~ ~~S207A~~ ~~S208B~~ ~~S209A~~ ~~S212A~~ ~~S212B~~ ~~S215A~~
  ~~S215B~~ ~~S216B~~ ~~S217B~~ ~~S219B~~ ~~S303B~~ ~~S308B~~ ~~S310B~~ ~~S311B~~ ~~S317B~~ ~~S713B~~ ~~S813B~~
  ~~S821B~~ ~~S901B~~ ~~S931B~~ ~~S949A~~ ~~S951B~~ ~~S9991B~~（这些非S10开头的，全部跳过不做）
  （注：这份清单是首次 scan 时"有待译内容"的文件，不是全部729个非P story文件——已经和官方中文一致、无需改动的文件不会出现在这里，属于正常跳过；
  S10开头且在此清单里的做完后，Story 阶段即算完成，可以进 Bubble）
- 已完成文件列表（真正完成的，撤销的不算）：
  - 2026-09-16 22:11 StoryData/S1000B.json（21条译文，apply --install + check 通过 + scan --accept 已推进基线；已装进游戏目录）
  - 2026-09-16 22:13 _root/ScenarioModelCodes-AutoCreated.json（Model阶段，47条译文，apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 22:17 StoryData/S1001B.json（63条译文，apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 22:22 StoryData/S1002B.json（118条译文，分4批翻完，apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 22:29 StoryData/S1003B.json（136条译文，分5批翻完，apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 22:43 StoryData/S1004B.json（370条译文，N公司法庭审判默尔索的完整戏份，分13批翻完，
    apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:22 StoryData/S1005B.json（233条译文，希斯克利夫/耐莉/亚细亚/贾环/仇甫的九人会密谈+进自杀贩卖机戏份，
    分8批翻完，apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:25 StoryData/S1008B.json（53条译文，让娜（雅克）作为"声音/巨人"戏弄默尔索的戏份，分2批翻完，
    apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:27 StoryData/S1009B.json（35条译文，改衣师安妮特的商店戏份，分2批翻完，
    apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:29 StoryData/S1010B.json（24条译文，让娜与默尔索继续对话，弑母案+"声音"的真相，1批翻完，
    apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:31 StoryData/S1011B.json（26条译文，让娜的回忆+扶梯谜题戏份，1批翻完，
    apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:32 StoryData/S1012B.json（9条译文，肉苏打/经验罐头对话+副主厨登场，1批翻完，
    apply（无install）+ check 通过 + scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:38 StoryData/S1013B.json（31条译文，B2层楼层经理制作金丝绞戏份，分2批翻完，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:40 StoryData/S1014B.json（65条译文，染坊帕莱特排队买金染料+良秀"普蒂"梗+找"裸者"（漆黑者成员）交涉戏份，
    分3批翻完，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    新增术语：Palette→帕莱特，Dyehouse→染坊，Le Noir→漆黑者，Naked→裸者）
  - 2026-09-16 23:42 StoryData/S1015B.json（44条译文，改衣师安妮特用金丝绞织布+前任主人回忆戏份，分2批翻完，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Alterationist→改衣师，Alteration Shop→改衣店，与S1009B的安妮特设定保持一致）
  - 2026-09-16 23:44 StoryData/S1016B.json（39条译文，红色精品店，不动者（Le Rouge人偶）扭曲发狂+默尔索前女友回忆戏份，
    分2批翻完，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    L'Inamovible→不动者，Le Rouge→赤红者，与既有 Le Noir→漆黑者 命名规律保持一致；<color=#a5ab8e>…</color>心声原样保留）
  - 2026-09-16 23:45 StoryData/S101B.json（1条译文，仅一个 zh_placeholder 的话数标题"Episode S0_1"，1批翻完，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:45 StoryData/S1060B.json（8条译文，默尔索弑母案审判开场（法官/被告问答），1批翻完，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    语气与S1004B法庭戏份保持一致的正式庭审措辞）
  - 2026-09-16 23:47 StoryData/S1061B.json（22条译文，默尔索母亲扭曲成怪物哀求默尔索杀了她+摇篮曲戏份，1批翻完，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:48 StoryData/S1062B.json（10条译文，西西弗塔巨人之室，让娜看着堕落的人变成家具的戏份，1批翻完，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - 2026-09-16 23:48 StoryData/S109B.json（1条译文，仅一个 zh_placeholder 的话数标题"Episode S0_8"，1批翻完，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - **Story阶段（只做S10开头文件的范围）到此全部完成。** 累计 1356 条译文，21 个输出文件。
  - 2026-09-16 23:50 _root/BattleSpeechBubbleDlg.json（Bubble阶段第1个文件，16条译文，10416/10816两个技能ID的战斗喊话短句，
    1批翻完，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Bubble 阶段还有 BattleSpeechBubbleDlg-a1c10p1.json 等分章节文件，共约52条待译，继续做）
- **用户已确认（2026-09-16）**：3D301B~S001A 那批先不管，按清单顺序从 S10 系列继续往后翻完，不用先问了。
- **大文件处理经验**：像 S1002B~S1004B 这种上百条甚至300+条的文件，`batch_next.py --size` 用 30 左右分批拉取，
  不要一次拉全部（100+条一次读取会超出上下文分页，还容易漏看）。每批读 pending → 填 answers → merge，
  重复到该文件耗尽为止，再统一 apply+check+scan --accept。大文件建议每10批左右做一次 checkpoint（apply+check+scan --accept），
  不要攒到文件翻完才第一次跑 apply，防止中途断线丢失"已装好但没留痕"的状态。
- **引号规则（2026-09-16 用户纠正）**：英文双引号 `"..."` 照翻成中文双引号，不要换成书名号『』或日式引号「」。
  已把 S1000B~S1003B 里错误使用的『』「」批量替换回双引号（详见 [[feedback_quote_style.md]] 记忆）。
  以后新批次直接用双引号，不要再犯。
- 下一步：`python batch_next.py --size 30 --file BattleSpeechBubbleDlg-a1c10p1.json --status todo,stale,outdated_official,same_as_en,zh_placeholder`
  Story 剩余文件按清单顺序一个个做完，再进 Bubble。

## RPGSystem 阶段（2026-09-17 新开的大阶段）

- **发现经过**：用户问起"floor-1~4/floor-b1/b2/route-a"和"自杀贩卖机"相关内容，搜索后发现
  `EN_ROOT/RPGSystem/` 整个子目录（44个文件，约6400条待译，之前完全没扫描到）+ 根目录 `EN_RPGSuicideBoxUI.json`
  （自杀贩卖机UI）。这才是用户最初说的"还没更新的RPG玩法"，之前做的 `_mech/*-BossRaid.json`
  是完全不同的另一个战斗系统（Boss Raid），不是这个。
- **技术改动**：RPGSystem 用的是不同的 JSON schema——条目标识字段是 `"key"`（不是 `"id"`），
  文本字段是扁平的 `"text"`/`"displayName"`/`"description"`/`"statText"`/`"goalDescription1~6"`，
  以及嵌套的 `"texts": [{"index":0,"text":...,"speaker":...}]` 对话数组。为此改了：
  - `config.py`：`TIER0_DIRS` 加入 `("RPGSystem", "RPGSystem")`；`TIER0_ROOT_FILES` 加入
    `RPGSuicideBoxUI.json`；`TRANSLATE_FIELDS` 加入 `text`/`displayName`/`description`/`speaker`/
    `statText`/`goalDescription1~6`。
  - `limbus/walk.py` 的 `item_ids()`：条目没有 `"id"` 时改用 `"key"` 当标识（RPGSystem 全部靠这个）。
  - 双语拼接（`config.BILINGUAL_JOIN`）对所有 scope 通用，RPGSystem 自动也有中英对照，不用额外处理。
- **翻译顺序（用户 2026-09-17 明确要求）**：
  1. **common 系列先做**（`*-common-a1c10p1.json`：dialogue-common、dialogue-choice-common、
     item-common、ui-common —— 这些是跨楼层共享的通用文本/UI/物品）
  2. **floor-1 全部做完**（dialogue-floor-1、dialogue-choice-floor-1、npc-floor-1、
     npc-floor-1-a-enemy、quest-floor-1、location-floor-1，等等所有 floor-1 相关文件）
  3. **floor-2 全部做完**，然后 floor-3（含 narration-floor-3）、floor-4、floor-b1、floor-b2、
     route-a（含 npc-route-a-warden）、theater，按这个顺序一路往后
  4. 严禁跳着做——同一个 floor 的文件要在切换到下一个 floor 之前全部清空待译
- **人名/陌生人称呼沿用既有术语表**（Kromer→克罗默、Meursault→默尔索、Yi Sang→李箱、Faust→浮士德、
  Sinclair→辛克莱、Gregor→格里高尔、Ryōshū→良秀、Heathcliff→希斯克利夫、Outis→奥提斯、Hong Lu→鸿璐、
  Don Quixote→堂吉诃德、Dubois→杜博阿，来自 P10816/P10416 阶段）；新出现的 Quillian 暂译"奎利安"。
- **纯韩文/内部开发标注不翻**：像 `단테 SD`、`발소리 Fixed 예시(참고용 — 스폰 미배치)` 这种明显是
  内部占位/开发备注（含少量拉丁字母如"SD"导致被扫描进待译队列），原样抄回去即可，
  batch_merge 只会报"译文不含中文"软警告，不是硬伤。
- **当前进度**（2026-09-17 02:31）：
  - `rpg-loc-npc-floor-1.json` ✅ 已完成（25条）
  - `rpg-loc-dialogue-common-a1c10p1.json` ✅ **已完成**（238条译文全部翻完，最后一批28条是尸体检视/D91xxx系列
    哲学独白，含大量 ■■■■■ 审查黑块，逐字保留原有黑块数量与分组，未新增未删除；apply（无install）+
    check 通过（无硬伤，仅软警告：韩文nickName不含中文属正常、'<It's just a corpse.>'与旧译法不一致——
    历史遗留多译法，不影响）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - `rpg-loc-dialogue-choice-common-a1c10p1.json` ✅ **已完成**（4条译文，DC11~DC14问答选项，1批翻完，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - `rpg-loc-item-common-a1c10p1.json` 进行中（2026-09-17 02:35）：约150条已翻完，分5批（服装/道具/家具/
    快乐衣橱器官/美食广场系列），apply（无install）+ check 通过（无硬伤，检查报告里的多译法/长度比警告
    都是历史遗留旧问题，与本次无关）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Shank→深剜（official_zh命中照抄）、Soda Pop→美味苏打（术语表命中）
  - `rpg-loc-item-common-a1c10p1.json` ✅ **已完成**（2026-09-17 02:38，共257条译文，分7批翻完：服装/道具/
    家具/快乐衣橱器官/美食广场系列/Sephirah符号道具（Yi Sang/Faust/Don Quixote/Ryōshū/Hong Lu/Heathcliff/
    Ishmael/Rodion/Sinclair/Outis/Gregor 全部 official_zh 命中照抄）/品牌总监遗物/自动攻击道具等，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；Thread→纺锤、Shank→深剜 均 official_zh 命中照抄）
  - `rpg-loc-ui-common-a1c10p1.json` ✅ **已完成**（127条，check 发现该文件此前某次会话已翻完但未记入本文件；
    确认无待译、check 通过无硬伤）
  - **common 系列全部完成，进入 floor-1 阶段。**
  - **踩坑记录（2026-09-17 02:40）**：Bash 工具在这台机器上终端codepage是GBK，直接用python打印UTF-8
    中/韩文到终端会显示成乱码（如"ȷ��"），**这不代表progress.json数据损坏**——用 Read 工具读文件或写到
    文件里再读，内容都是正常UTF-8。以后怀疑乱码先这样排除，不要慌着当硬伤处理。
  - `rpg-loc-dialogue-floor-1.json` 进行中（2026-09-17 02:42 checkpoint）：90条已翻完（D1911~D1991系列，
    但丁/以实玛利/默尔索/罗佳四人小队探索一楼漆黑者/赤红者卖场、遭遇尖钉Boss战前对话），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 02:43 checkpoint）：又翻完90条（D10011洗手间四人限制对话、D1099金针人体模特分析、
    D1100~D1109找默尔索/但丁远程侦察、D1963过时衣服堆、D1980扶梯选错楼层折返），累计约270条，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - `rpg-loc-dialogue-floor-1.json` ✅ **已完成**（2026-09-17 02:45，共1205条译文，分若干批翻完；
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    新增NPC名：Mimosa→米摩莎、Dubois→杜博阿（沿用）、Gustave→古斯塔夫、Quillian→奎利安（沿用既有暂译）；
    "Manager Bud"→经理老兄（术语表命中）；check里出现的多译法都是同一原文在不同文件/上下文分别命中过两种
    合理译法，非硬伤，不用管）
  - **floor-1 剩余4个文件核实后发现全部已完成**（choice/npc-a-enemy/quest/location 都是"没有符合条件的待译条目"，
    应是更早某次会话做的、没写进本文件）。**floor-1 阶段全部完成，进入 floor-2。**
  - **文件名注意**：floor-2 及以后的 RPGSystem 文件名**不带 `-a1c10p1` 后缀**（如 `rpg-loc-dialogue-floor-2.json`
    而非 `...-a1c10p1.json`），跟 common/floor-1 系列不一样，batch_next.py --file 要用不带后缀的名字。
  - floor-2 规模：`rpg-loc-dialogue-floor-2.json`(401) `rpg-loc-npc-floor-2.json`(33)
    `rpg-loc-quest-floor-2.json`(15) `rpg-loc-npc-floor-2-a-enemy.json`(9) 等，dialogue是大头先做
  - `rpg-loc-dialogue-floor-2.json` 进行中（2026-09-17 02:48 checkpoint）：120条已翻完（D2002奢华厅装修/
    品牌总监刁难/D2004~D2006希斯克利夫舔肘子梗+但丁楼层切换机制解说/D2007~D2009血肉墙+漆黑者狂信徒乌玛尔
    (Umar)出现，古风措辞/D20091乌玛尔要求用金钉毁灭赤红者伪神的交易对话），apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    新增术语：Umar→乌玛尔（说话古风文言腔，thee/thou式，翻成文言/半文言）
  - 继续（2026-09-17 02:58 checkpoint）：又翻完60条（D20091但丁与浮士德/默尔索的选择对话+让娜梗+乌玛尔催促/
    D2010金钉刺入漆黑者/D2011品牌总监"沉睡者"摇篮描述+希斯克利夫认出她+进战斗前警告），累计180条，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:00 checkpoint）：又翻完60条（D2011品牌总监拉黑发言/D20111圣幕/垂死漆黑者古风临终
    独白/D2012~D20122牧师"声音"神谕古风文言+品牌经理骑士出场，两人都是圣经体thee/thou，按规则3译成
    文言/半文言；君主→Lord的既有译法），累计240条，apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:01 checkpoint）：又翻完60条（D2020品牌经理古风独白结束+但丁/浮士德/默尔索发现自己是
    "来自喷泉的怪人"能穿过赤红者/漆黑者的规则屏障+D2021进入下一战），累计300条，apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    新增：Le Noir Hammer→漆黑者铁锤（品牌总监的护卫机制怪）
  - 继续（2026-09-17 03:02 checkpoint）：又翻完30条（D2014灰字"声音"文言体独白/D2016金钉刺向摇篮/D2019
    施工结束回楼上/D2030赤红之神苏醒前奏/D2601~D2905漆黑者守卫+赤红者各类尸体描述），累计330条，
    apply（无install）+ check 通过（无硬伤，'The Crimson God'出现赤红之神/赤红神两种历史译法属正常）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:03 checkpoint）：又翻完30条（D2030~D2031赤红之神苏醒/哭泣/摇篮曲+金色婴孩死亡+
    行政官浮士德意识到什么不对劲+希斯克利夫收尾吐槽），累计360条，apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:04 checkpoint）：又翻完30条（D2022品牌总监警告/D2031浮士德意识到Gesellschaft相关+
    默尔索永恒化影响/D2906战斗失败后重开对话回顾决策链/D2907默尔索死后复活头部恢复梗），累计390条，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Gesellschaft 保留原文不译（组织专名，类似LCD/LCB处理）
  - `rpg-loc-dialogue-floor-2.json` ✅ **已完成**（2026-09-17 03:05，共401条译文，D2032~D2908收尾：离开限制/
    赤红者守卫被击败/战斗前观察建议），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏
  - floor-2 剩余文件：`rpg-loc-npc-floor-2.json`(33) → `rpg-loc-quest-floor-2.json`(15) →
    `rpg-loc-npc-floor-2-a-enemy.json`(9) → 其余小文件（dialogue-choice-floor-2等，如有）
  - `rpg-loc-npc-floor-2.json` ✅ **已完成**（33条，赤红者店长/店员/漆黑者冲锋兵/抵抗的赤红者/品牌总监/
    品牌经理/漆黑者高阶护卫/赤红之神[初生之躯] 等NPC名称，apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；Kromer's Sister→克罗默的姐姐）
  - `rpg-loc-quest-floor-2.json` ✅ **已完成**（15条，Q2001~Q2011任务描述/目标，apply（无install）+ check
    通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    "Flannel and Felt"→法兰绒和毛毡，暂译，未确认具体指代哪两个角色）
  - `rpg-loc-npc-floor-2-a-enemy.json` ✅ **已完成**（9条，apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏）
  - **floor-2 阶段全部完成。核实 state.json 确认 floor-2 相关文件已无剩余，进入 floor-3。**
  - floor-3 规模：`rpg-loc-dialogue-floor-3.json`(1087，大头) `rpg-loc-quest-floor-3.json`(56)
    `rpg-loc-narration-floor-3.json`(约7) `rpg-loc-npc-floor-3.json`(约11) `rpg-loc-npc-floor-3-a-enemy.json`(约7)
    `rpg-loc-dialogue-choice-floor-3.json`(约11) 等，dialogue先做
  - `rpg-loc-dialogue-floor-3.json` 进行中（2026-09-17 03:06 checkpoint）：30条已翻完（D3001辛克莱/奥提斯
    三楼分组开场+D3110~D3115奥提斯审问默尔索为何对这地方了如指掌），apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 下一步：`python batch_next.py --size 30 --file rpg-loc-dialogue-floor-3.json --status todo,stale,outdated_official,same_as_en,zh_placeholder`
    继续翻（大文件，1087条，预计还要三十几轮，每完成~90-150条做一次apply+check+scan--accept checkpoint）
  - 继续（2026-09-17 03:07 checkpoint）：又翻完60条（D3002让娜/默尔索前恋人关系吐槽收尾/D3003~D3019找声音
    来源路线提示/D3301"两件套"人偶用支离破碎的话谈论"会议"味道咸如眼泪），累计90条，apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Two-piece→两件套（破碎话语的诡异人偶NPC）
  - 继续（2026-09-17 03:08 checkpoint）：又翻完30条（D3005新"声音"发现+奥提斯分析阵营操纵手段/D3006不动者
    (L'Inamovible)商贩出场+纠缠顾客+被钉在地上/D3301两件套议题一二会议纪要梗收尾），累计120条，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:09 checkpoint）：又翻完30条（D3006不动者与赤红之神"声音"祈愿独白+默尔索揭示自己
    知道声音是谁+奥提斯"又一个知道的人"伏笔），累计150条，apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:10 checkpoint）：又翻完30条（D3006默尔索揭晓"母亲的声音"真相/D3007不动者绝望独白+
    恳求玩家去广播室查真相+被尖钉束缚在地/但丁意识到瞒不住默尔索母亲已死的事实），累计180条，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:11 checkpoint）：又翻完30条（D3007奥提斯建议顺从不动者请求去广播室/D3008安妮特
    改衣店登场/D3009改衣店太贵吐槽+默尔索解释"两件套"是名字/D3011三楼楼层经理拉长音诡异低语），累计210条，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:11 checkpoint）：又翻完30条（D3011三楼楼层经理"无尽的旁白者"巨型面板怪+手持鸟笼
    录音带模仿"声音"梗/D3012继续拉长音独白），累计240条，apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:17 checkpoint）：又翻完30条（D3013~D3018楼层经理拉长音独白收尾+获得广播录音带道具/
    D3100~D3102赤红者尤内斯库(Ionesco)出场，讲述教义"声音存在是为了区分不信者和疑虑者"），累计270条，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    拉长音单词统一处理为汉字重复（如"披披披披上""西西西西弗弗弗弗"），保持风味
  - 继续（2026-09-17 03:17 checkpoint）：又翻完30条（D3081~D3082不动者得知"声音"只是循环播放的录音真相后
    崩溃+奥提斯冷眼吐槽/D3100尤内斯库预言"声音"将以全新形态回归收尾），累计300条，apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:18 checkpoint）：又翻完30条（D3082不动者被手掌茧包裹吞噬+奥提斯"神会抛弃最依附它的
    人"感悟/D3083变形描写/D3094让娜揭示Giant真相的完整独白：录音带年代不重要，高层赤红者早有察觉但不敢说），
    累计330条，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 03:19 checkpoint）：又翻完30条（D3084两件套会议梗/D3094让娜解释Giant是"支柱"+害怕
    西西弗一切+匆匆离开/辛克莱与奥提斯讨论下一步探索方向），累计360条，apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:20 checkpoint）：又翻完30条（D3084两件套密语继续+奥提斯提议拷问破译+辛克莱阻止），
    累计390条，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 03:21 checkpoint）：又翻完30条（D3084密语对话收尾去改衣店/D3085安妮特改衣店买巨剪
    讨价还价开场），累计420条，apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:21 checkpoint）：又翻完30条（D3085安妮特提议剖开默尔索脑袋换更好价钱+奥提斯解释
    西西弗象征意义规则+默尔索同意/D3086安妮特翻看默尔索脑内景象，看到抽屉但守规矩不翻），累计450条，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:22 checkpoint）：又翻完30条（D3086安妮特看完默尔索脑内景象+免单剪刀/D3087~D3088
    法兰绒(Flannel)与毛毡(Felt)两位NPC正式登场，担心西西弗要垮+质问队伍如何绕过两件套），累计480条，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    确认 Flannel→法兰绒、Felt→毛毡 是正式NPC名（此前quest文本"Flannel and Felt"暂译已验证正确）
  - 继续（2026-09-17 03:23 checkpoint）：又翻完30条（D3088法兰绒/毛毡质问一行人如何从一楼快速抵达三楼+
    "喷泉"与"洗手间"混淆梗+情报换折扣交易开启），累计510条，apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:23 checkpoint）：又翻完30条（D3088法兰绒/毛毡讨价还价听完整个不动者商贩故事+录音带
    真相揭晓+法兰绒嘲讽赤红者"活该"），累计540条（floor-3约50%），apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:24 checkpoint）：又翻完30条（D3089着迷的漆黑者沐浴诡异光芒/D3090法兰绒毛毡"召回
    产品"梗——想清除穿自家品牌却配不上的顾客，揭示奢华厅准入需要"稀缺性"），累计570条，apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:25 checkpoint）：又翻完30条（D3090法兰绒毛毡召回品牌交易达成+D3091让娜揭示"死亡在
    这模拟中变成终局"+队伍是例外的伏笔/D3092任务奖励+法兰绒确认队伍要继续往上爬），累计600条（约55%），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:26 checkpoint）：又翻完30条（D3092任务收尾：法兰绒毛毡赠送品鉴证书作为报酬+请求
    转告楼上漆黑者赤红者秘密），累计630条（约58%），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:27 checkpoint）：又翻完30条（D3104~D3108不动者继续求助/D3151默尔索遇到"阳光"声音+
    烦躁反应，暗示与之前Le Rouge Sales Associate[Sunshone]相关梗+奥提斯识趣不追问/D3152~D3154蚕茧中未知
    女性状态描述/D3603~D3607法兰绒毛毡VIP折扣收尾），累计660条（约61%），apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:28 checkpoint）：又翻完30条（D3016三楼楼层经理颤音低语/D3904~D3905楼层经理死亡描述/
    D3962~D3963两件套"投票表决"梗，辛克莱用类比帮它们打破僵局），累计690条（约63%），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:28 checkpoint）：又翻完30条（D3906~D3909坠落主题装置艺术描述+奥提斯/但丁/辛克莱
    讨论良秀会怎么吐槽"D.R.A.B."（土气）梗/D3963两件套确认自己"一直是两个"收尾），累计720条（约66%），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:29 checkpoint）：又翻完30条（D3910~D3916商店物件描写+收银机拿眼球/D39161~D39163
    让娜"呼呼"调侃辛克莱偷窃道德焦虑，默尔索认真回答"没有法律框架"梗），累计750条（约69%），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:29 checkpoint）：又翻完30条（D3917~D3982一堆物件描写：脂肪釉面装置艺术/68年系列/
    第1辑辛西娅坠落装置艺术+辛克莱吐槽艺术品/门帘/剪刀/巨型手臂等场景细节），累计780条（约72%），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    新增：Ring Nursefather→环指父辈
  - 继续（2026-09-17 03:30 checkpoint）：又翻完30条（D3801~D3817广播室场景细节：插孔/通风扇/骰子+人工通讯
    总机机制解说，奥提斯军事背景知识展现），累计810条（约75%），apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:31 checkpoint）：又翻完30条（D3818管风琴状装置+"视线不受视觉限制"梗/D3819死鸟广播+
    捡到老式录音机/D3821辛克莱外套变小=四楼流行"功能袜"梗，奥提斯借机跟法兰绒讨价还价换情报），累计840条
    （约77%），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 03:32 checkpoint）：又翻完30条（D3821袜子交易收尾/D3831~D3833折纸收藏系列限量版号梗，
    辛克莱科普版画编号价值差异知识/D3834~D3836 Prêt-à-porter法语时装术语，Prêt-à-porter保留原文不译，
    类似Gesellschaft处理），累计870条（约80%），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:33 checkpoint）：又翻完30条（D3837~D3852恐怖商店陈列描写+人体模特服装细节+让娜嘲讽
    "勤劳小蜜蜂"翻收银机+金丝含量诈骗广告梗），累计900条（约83%），apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏。
    **踩坑**：batch_answers.json 里译文正文含英文直引号 `"` 会破坏JSON语法（batch_merge报"缺少文件"的
    误导性错误，实际是JSON解析失败）。以后译文中的引号一律用中文弯引号“”，不要用直引号。
  - 继续（2026-09-17 03:34 checkpoint）：又翻完30条（D3854~D3859眼镜展柜+"凳屉"双关梗/D41410法兰绒毛毡
    与队伍任务链接续：赤红者密谋孕育新"声音"，需要尖钉+金色布料阻止，请求队伍再次帮忙），累计930条
    （约86%），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；strawer→凳屉（双关译法）
  - 继续（2026-09-17 03:35 checkpoint）：又翻完30条（D41410法兰绒毛毡完整任务链说明：金色线束需要地下一层
    蚕茧+地下二层楼层经理，尖钉需要利用地下三层那位"恶心的赤红者"脊柱，奥提斯吐槽任务"曲折"），累计960条
    （约88%），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 03:35 checkpoint）：又翻完30条（D41410任务链收尾，法兰绒毛毡承诺美言+品鉴证书/D41420
    金色布料完成+确认脊柱当尖钉/D41510让娜灰字点评不动者的"扭曲恶化"是因为终于适应了不合身的躯壳），
    累计990条（约91%），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:36 checkpoint）：又翻完30条（D3155~D3156法兰绒毛毡拿到金钉后感激涕零+VIP承诺+
    揭示奢华厅准入需要"不受楼层规则束缚的顾客"（即队伍本身）+让娜嘲讽赤红者妄图自造声音/D41610从死去
    赤红者身上撕下脊柱当"尖钉"+缠上金布，三件套凑齐），累计1020条（约94%），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:37 checkpoint）：又翻完30条（D-PB-FLOOR3MASTER三楼楼层经理BOSS战开场拉长音台词/
    D3156法兰绒毛毡下达"粉碎奢华厅抵抗"指令+让娜灰字"金色树脂凝聚永恒"预言/D3983~D3984BOSS战躲避机制
    对话），累计1050条（约97%，只剩约37条），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - `rpg-loc-dialogue-floor-3.json` ✅ **已完成**（2026-09-17 03:38，共1087条译文，最后7条D3987~D3990
    收尾不动者(L'Inamovible)当场死亡场景），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - `rpg-loc-quest-floor-3.json` ✅ **已完成**（2026-09-17 03:40，共56条译文，Q3001~Q3013/Q4014~Q4017
    任务描述/目标，3F探索+两件套剪开+黑色精品店清理漆黑者+金色布料/钉子任务链，分2批翻完），
    apply（无install）+ check 通过（无硬伤，误报"疑似漏译"均为Maison du Noir/Boutique du Rouge等
    保留原文的法语店名）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    确认沿用 Arc Floor Lamp→弧光落地目灯（既有译法）
  - `rpg-loc-npc-floor-3.json` ✅ **已完成**（11条，不动者/两件套/改衣师安妮特/法兰绒/毡呢/尤内斯库等NPC名，
    含3条韩文SD占位原样保留）
  - `rpg-loc-npc-floor-3-a-enemy.json` ✅ **已完成**（7条，漆黑者/赤红者店员[阳光]/自走旋转器/皮革父辈/
    三楼楼层经理等敌人显示名）
  - `rpg-loc-dialogue-choice-floor-3.json` ✅ **已完成**（11条，DC3111~DC39162选项文本，安妮特脑内景象/
    商店主题的谜语式选项）
  - `rpg-loc-narration-floor-3.json` ✅ **已完成**（7条，NAR_3F_HighDomestic/NAR_3F_Le_Noir系列，
    赤红者/漆黑者"诫命"体旁白，用文言腔翻译，与D2012~D2020品牌经理/牧师古风注册保持一致）
  - **floor-3 阶段全部完成**（2026-09-17 03:42，dialogue1087+quest56+npc11+npc-a-enemy7+
    dialogue-choice11+narration7，共1179条），apply（无install）+ check 通过（无硬伤，剩余均为历史
    遗留多译法软警告，如'Felt'本次npc条目用了"毡呢"与floor-2 quest既有译法"毛毡"不一致，非硬伤不影响）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏。**进入 floor-4。**
  - floor-4 规模：`rpg-loc-dialogue-floor-4.json`(1047，大头) 等，按floor-3的模式
    （dialogue先做，再quest/npc/npc-a-enemy/dialogue-choice/narration等收尾文件）
  - `rpg-loc-dialogue-floor-4.json` 进行中（2026-09-17 03:45 checkpoint）：120条已翻完（D40001开场蓝字旁白/
    D40110堂吉诃德洗手间梗+鸿璐草叶少女放松法/D40210堂吉诃德驽骍难得同伴梗+盘查鞋子被抓包/D40212~D40213
    鞋履厅"一腿"训斥"四腿"+四腿向队伍诉说渴望"一腿"地位+复活机制已失效的绝望+四腿突然袭击队伍），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；Don Quixote thee/thou古风腔延续；Four-legs/One-leg沿用四腿/一腿既有译法
  - 继续（2026-09-17 03:47 checkpoint）：又翻完210条累计（D40211四腿求死被击败后解脱独白/D40220~D40222
    金色巨人"声音"（让娜相关）金枝/金色树脂真相独白+默尔索弑母责任对话/D40230~D40231A一腿鞋履厅经理登场，
    训斥四腿死亡+盘问队伍出示漆黑者验真证书+三楼赤红者失声传闻印证），apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Golden Bough→金枝，ma puce（法语昵称）保留原文不译（沿用floor-3既有处理）
  - 继续（2026-09-17 03:48 checkpoint）：又翻完30条累计270条（D40231一腿给出卡基偷神器线索/D40310~D40311
    队伍进入家具厅+弧光落地目灯登场"是灯是人"梗），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏；Kaki→卡基（沿用P10816既有译法）
  - 继续（2026-09-17 03:49 checkpoint）：又翻完30条累计330条（D40311弧光落地目灯自卖梗收尾：4000眼球报价被
    拒+要求买新衣服打折促销失败+队伍借口去找家具厅经理，堂吉诃德古风腔与目灯商贩腔对话交织），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 03:51 checkpoint）：又翻完60条累计390条（D40410~D40411家具厅"店主"登场——不会说话、
    用展开躯干露出杂物的方式交流，队伍拿走一件给目灯当衣服/D40510目灯不满衣服选择+撤销折扣但答应回答问题，
    揭示店主是"快乐衣橱"、家具们因永远上不去楼层/进不了奢华厅而"选择留下"），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Happy Closet→快乐衣橱（沿用既有译法）
  - 继续（2026-09-17 03:51 checkpoint）：又翻完30条累计420条（D40510目灯家具们苏醒渴望被购买的"痛苦"独白+
    折扣重新出价+其余家具围观"想要装饰"起哄变得"森然"诡异，队伍察觉不对劲，店主始终无法开口解释），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 03:52 checkpoint）：又翻完60条累计480条（D40610~D40611快乐衣橱再次开合分发物品+
    但丁吐槽速度慢/D40710骨骸衣架要"脚趾甲"结果堂吉诃德拿错成舌头当帽饰/D40711松软皮床全程赖床不肯起来
    只让队伍直接把毛茸茸外套披上去），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏；Bonehanger→骨骸衣架，Mellow Leather Bed→松软皮床（新译名）
  - 继续（2026-09-17 03:53 checkpoint）：又翻完30条累计510条（D40712剥制皮帘"酷~"口癖式营销梗+但丁吐槽/
    D40713红垫凳登场吐槽货源不足），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏；Taxidermied Leather Curtain→剥制皮帘，
    Red-cushioned Stool→红垫凳（新译名）；kewl~口癖统一译"酷~"
  - 继续（2026-09-17 03:54 checkpoint）：又翻完30条累计540条（D40713红垫凳吐槽收尾/D40714生皮沙发礼貌感激+
    连挑三件衣服），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏；Skinhide Couch→生皮沙发（新译名）
  - 继续（2026-09-17 03:55 checkpoint）：又翻完30条累计570条（D40714生皮沙发礼貌假象破裂爆粗口+赶人+
    发现其实只能拿一件后又恢复礼貌收尾/D40715双子灯登场，双胞胎式重复台词），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Lamp Twin→双子灯（新译名）
  - 继续（2026-09-17 03:56 checkpoint）：又翻完30条累计600条（D40715双子灯9900眼球报价+队伍付不起被嘲穷/
    D40810堂吉诃德感谢快乐衣橱慷慨/D40813快乐衣橱再次无言敞开，队伍疑惑其慷慨动机，鸿璐用"徽章收藏"类比
    引出堂吉诃德表态愿为助人舍弃colección），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:57 checkpoint）：又翻完30条累计630条（D40811所有家具集体暴露真面目会动+一拥而上
    抢快乐衣橱物资/D40813堂吉诃德恳求留下"红雾"限量徽章被吐槽大惊小怪/D40814队伍被挤开，家具们如食腐鸟般
    扑向不动的快乐衣橱抢衣服，松软皮床羡慕摇椅"永远沉睡"），apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:58 checkpoint）：又翻完30条累计660条（D40812目灯赶来指责队伍"抢客户"+默尔索灰字
    对错相对论吐槽/D40814家具们互相抢夺器官部位争吵收尾），apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 03:59 checkpoint）：又翻完30条累计690条（D40812目灯发现快乐衣橱"心脏"是无价之宝+
    请求献出心脏+家具们哄抢分割场面收尾），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:00 checkpoint）：又翻完30条累计720条（D40812家具混战收尾/D40818场景突变，看到疑似
    "让娜"过去的记忆片段（非默尔索）/D40819堂吉诃德推理巨人职责=从外部观察西西弗百货+家具们曾经是"城市里的
    普通人"+默尔索揭示巨人=心怀恐惧之人，非享受他人苦难），apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:01 checkpoint）：又翻完30条累计750条（D40815记忆片段核心场景：默尔索与让娜在罐头
    电影院共享《孤独的收尾人走向夕阳》，让娜大段独白坦白对存在本身的恐惧+"为何生为人类"的诘问，
    默尔索始终沉默），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:02 checkpoint）：又翻完30条累计780条（D40816但丁询问默尔索是否也害怕+默尔索透露
    恐惧始于母亲快满一周年时第一次痛哭/D41320~D41323场景切回现实，家具洗劫后快乐衣橱彻底静止不动，
    鸿璐捡到一张纸条，目灯当垃圾不要），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:03 checkpoint）：又翻完30条累计810条（D41321~D41324纸条揭晓"金色布料与钉子"预言
    文本，队伍联想到一腿提到的传说武器/D41325堂吉诃德感慨快乐衣橱的下场+摘下藏着的收尾人徽章放在残骸旁
    致意后离开/D41330目灯继续揽客推销），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:04 checkpoint）：又翻完30条累计840条（D41330目灯不打折推销收尾/D41331把配方交给
    一腿+一腿轻蔑评价队伍"卑微低贱"但认可结盟价值+队伍打听五楼入口，一腿透露需要符合尊贵着装规范），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 04:05 checkpoint）：又翻完30条累计870条（D41331一腿解释五楼门槛+透支质问后恼羞成怒
    收尾/D41901~D41912一批场景/机制描写小段：路被堵死/家具们"安宁"下来/两盏目灯低语摆动/单只目灯眨眼互动
    （含32次重复"眨眼"拟声梗）/碰黑沙发触发家具苏醒逼近的战斗前提示），apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:06 checkpoint）：又翻完30条累计900条（D40740~D40754家具们分散的招揽台词补充/
    D41914~D41946黑色沙发触发家具苏醒+鞋履厅天花板悬挂鞋履展示场景描写系列，暗示金色毛皮/血肉目灯登场），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；Vanitas（拉丁语"虚空"）保留原文不译，沿用ma puce/colección处理方式
  - 继续（2026-09-17 04:07 checkpoint）：又翻完30条累计930条（D40754~D407551生皮沙发爆粗后杀死默尔索的
    战斗后对话（重复两次，D407551为副本），队伍推测阳光/阴影可能是家具攻击性的触发条件，计划下次在阳光下
    交谈），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 04:08 checkpoint）：又翻完30条累计960条（D40910一腿疑惑队伍为何折返+发现但丁走错路
    回地下一层重试扶梯/D41949鞋架场景描写/D41950花盆藏物梗：鸿璐忆惜春&怡红院旧事+堂吉诃德讲述尼可莉娜
    藏钥匙于城堡花盆的往事），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏；沿用惜春/怡红院既有译名，新增尼可莉娜（Nicolina，堂吉诃德背景人物）
  - 继续（2026-09-17 04:09 checkpoint）：又翻完30条累计990条（D41950花盆藏物梗收尾/D41952~D41966一批场景
    机制描写：阳光下发现快乐衣橱遗物"灯下黑"梗/扫帚声/健壮盆栽/长椅/赤红者尸体+鞋子描写等环境细节），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 04:10 checkpoint）：又翻完30条累计1020条（D40756战斗后吐槽被家具偷袭/D41801~D41804
    目灯继续揽客+新NPC多萝西娅（Dorothea）登场/D41967~D41971家具"死亡"后的残骸环境描写系列（血渍/床架
    散架等）/D4960~D4964一腿因被"错误攻击"恼怒+多萝西娅委屈求饶想回家，一腿最终原谅），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；新增NPC：Dorothea→多萝西娅
  - `rpg-loc-dialogue-floor-4.json` ✅ **已完成**（2026-09-17 04:11，共1047条译文，最后27条D4964~D4977
    家具们挨打惨叫收尾），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏
  - floor-4 剩余文件（按floor-3模式，dialogue先做完，下面依次做）：`rpg-loc-quest-floor-4.json` →
    `rpg-loc-npc-floor-4.json` → `rpg-loc-npc-floor-4-a-enemy.json` → `rpg-loc-dialogue-choice-floor-4.json` →
    `rpg-loc-narration-floor-4.json`（若存在），先跑 batch_next 确认每个文件规模
  - `rpg-loc-quest-floor-4.json` ✅ **已完成**（2026-09-17 04:13，共39条译文，Q4001~Q4013任务链：四楼探索/
    一腿传说武器线索/家具厅目灯换装任务链/快乐衣橱被摘心+去地下层拿金色蚕茧任务过渡），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - `rpg-loc-npc-floor-4.json` ✅ **已完成**（21条NPC名，家具们全套译名：骨骸衣架/弧光落地目灯/剥制皮帘/
    生皮沙发/快乐衣橱/多萝西娅/一腿/四腿/珂赛特/双子灯/红垫凳/松软皮床/皮床/长腿灯等）
  - `rpg-loc-npc-floor-4-a-enemy.json` ✅ **已完成**（4条，咔嗒作响的抽屉/吱呀作响的抽屉）
  - `rpg-loc-dialogue-choice-floor-4.json`、`rpg-loc-narration-floor-4.json` 核实后确认不存在待译条目
    （文件本身不在待办范围，或已完成）
  - **floor-4 阶段全部完成**（2026-09-17 04:14，dialogue1047+quest39+npc21+npc-a-enemy4，共1111条），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏。**进入 floor-b1。**
  - floor-b1 规模（2026-09-17 04:14 待确认，先跑 scan/batch_next 看清单）：约763条待译，
    按floor-4模式（dialogue先做，再quest/npc/npc-a-enemy/dialogue-choice/narration等收尾文件）
  - `rpg-loc-dialogue-floor-b1.json` 进行中（2026-09-17 04:15 checkpoint）：30条已翻完（D-10001开场蓝字
    旁白/D-1001格里高尔（Gregor）地下一层登场，粗犷口语化美式俚语风格+"鲜肉科"招牌梗+复盘二楼/家具偷袭/
    默尔索脑壳被剪刀剪开等既往战报），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏；Gregor 用随性口语化现代汉语（非古风）
  - 继续（2026-09-17 04:16 checkpoint）：又翻完30条累计60条（D-1001鲜肉科场景描写+格里高尔"大海捞针"抱怨+
    虫子自嘲梗+浮士德认真吐槽/D-1102干渴的卡基与饥饿的卡基两个新NPC窃窃私语，误判队伍阵营+盘算蹭钱），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；新增NPC：Thirsty Kaki→干渴的卡基，Hungry Kaki→饥饿的卡基
  - 继续（2026-09-17 04:17 checkpoint）：又翻完30条累计90条（D-1102格里高尔搭话两位卡基/D-1103默尔索出示
    蚕茧图片问路，两卡基讨价还价收买情报未遂+误以为蚕茧是"美食广场新菜式"+格里高尔"看着不像能吃的"吐槽，
    队伍决定改去美食广场打听），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:18 checkpoint）：又翻完30条累计120条（D-1002默尔索解释罪人受象征界域束缚不能分头
    找扶梯/D-1103两卡基收钱后指路"跟着螺旋贝壳走"=蜗牛壳梗+浮士德确认情报收集完毕，卡基们卷钱溜走，
    队伍前往美食广场），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:19 checkpoint）：又翻完30条累计150条（D-1002~D-1005扶梯场景描写系列/D-1006~D-1008
    两卡基喷泉抢位+"五小时定律"捡食梗/D-1009副主厨（Sous Chef）人偶登场，坚决否认自己是人体模特，
    提及上级"布彻"（Boucher）），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏；Sous Chef→副主厨（沿用S1012B既有译法），新增NPC Boucher→布彻
  - 继续（2026-09-17 04:20 checkpoint）：又翻完30条累计180条（D-1009副主厨"听清楚了吗？"口癖持续+队伍
    连蛹/蚕茧概念都要解释+确认金色蚕茧在布彻储藏室但不卖，副主厨提议拿"合适的替代品"以物易物，暗示队伍
    自身可能就是替代品），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:21 checkpoint）：又翻完30条累计210条（D-1009副主厨逐一"品鉴"队伍成员当食材+闻到
    格里高尔身上"虫气十足"的味道疯狂索求他的手臂当替代品交换蚕茧+格里高尔震惊反应，队伍讨论砍手臂这种
    离谱选项是否可行），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:22 checkpoint）：又翻完30条累计240条（D-1009但丁拒绝拿格里高尔手臂交易+担心象征界域
    未知风险，副主厨恼羞成怒决定强抢/D-1010战斗中副主厨喊"暂停"求饶但仍执念于虫子手臂风味，格里高尔怒斥），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 04:23 checkpoint）：又翻完30条累计270条（D-1010副主厨逃跑求饶+浮士德建议追击/
    D-1026~D-1027美食广场场景切换/D-1028追上副主厨谈判，用布彻情报交换她带路见布彻+副主厨提出"舔三下
    虫子手臂"的怪异条件收尾），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:24 checkpoint）：又翻完30条累计300条（D-1028格里高尔抗拒被舔手臂+但丁拿金笠往事
    类比劝说+格里高尔妥协同意，副主厨指路肉铺+透露布彻是楼层经理），apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:25 checkpoint）：又翻完30条累计330条（D-1011布彻正式登场，纠正副主厨"主厨/副主厨"
    职称混淆梗+默尔索交涉金色蚕茧+布彻婉拒眼球，让副主厨去查库存"搁浅幼虫"/D-1028格里高尔手臂被舔三下不止
    的爆笑收尾，副主厨确认自己是苏打调味负责人），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏；新增NPC：Boucher→布彻（正式登场确认）
  - 继续（2026-09-17 04:26 checkpoint）：又翻完30条累计360条（D-1011布彻揭示金色蚕茧其实是幼虫身上的
    "风味"部位+幼虫已濒临绝种（前一个时代的遗迹）+格里高尔再次拒绝手臂交易，布彻改用"猎物反刍肉"作为
    替代食材，指路天花板悬挂的"猎物反刍肉"），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏；新增术语：Camemblack Scabbardfish→卡门布莱克刀鱼，
    Ruminations of the Prey→猎物反刍肉
  - 继续（2026-09-17 04:27 checkpoint）：又翻完30条累计390条（D-1011布彻指路鲜肉科锈蚀吊钩/D-1012反复追问
    反刍肉外形，副主厨"我不知道"绕圈+格里高尔玩梗叫她"汤主厨"+副主厨最终给出关键线索"挂在最左边+肋骨间
    闪光"，队伍推断出即带金色毛皮的肉块），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:28 checkpoint）：又翻完30条累计420条（D-1012格里高尔坦白讨厌自己的虫子手臂但仍不愿
    献出+副主厨最终放弃索取+浮士德/默尔索点评格里高尔"劝说与恐吓"话术+队伍继续前进/D-1013~D-1017搜索猎物
    反刍肉过程环境描写系列，成功获得食材/D-1033~D-1034副主厨重复线索提示+告别），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:29 checkpoint）：又翻完30条累计450条（D-1017~D-1018格里高尔吐槽讨厌鬼太多+返回
    布彻确认食材+布彻调侃格里高尔差点少几条手臂"火焰头"梗+索要活体幼虫/D-1104布彻确认队伍只要金色蚕茧
    不要幼虫本体，成功交货完成任务），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:30 checkpoint）：又翻完30条累计480条（D-1104布彻招待免费苏打（没气版本梗）+布彻
    哲学化解释幼虫哭声"降生即被恐惧吞没"+提醒队伍前往下一层入口，格里高尔讨水喝收尾），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:31 checkpoint）：又翻完30条累计510条（D-1104默尔索拒绝喝苏打+解释味道会逼近但绝非
    等同记忆中真实食物的哲学理由，格里高尔反驳"价值取决于当下感受"，默尔索表示理解但仍坚持己见），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 04:32 checkpoint）：又翻完30条累计540条（D-1019~D-1022诡异楼梯场景三段重复描写+让娜
    灰字祝贺"又拿下一个"+梯子/山/鞋子的模糊意象/D-1104苏打话题收尾，默尔索意外没有强烈反驳格里高尔+"怀念"
    哲学独白：怀念是围绕愉快记忆重构的产物），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:33 checkpoint）：又翻完30条累计570条（D-1022让娜灰字讽刺默尔索"让他们做最终裁决"是
    懦弱+默尔索沉默等待队伍答案，转场地下二层/D-1059~D-1069一批民宅探索场景描写（诡异身影/肉皮革堆积/
    眼球成山+肚子肿胀死者等）/D-1201默尔索母亲记忆闪回：黑咖啡场景，母亲引导默尔索用自己的经验重新定义
    "熟悉感"，默尔索首次描述咖啡带来的苦、烫、湿润眼眶的真实感受），apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:34 checkpoint）：又翻完30条累计600条（D-1052~D-1055漆黑者搬运工登场，指路地下二层+
    默尔索出示三楼验真证书后获得礼遇祝福"愿你们的下行之路一路顺遂"/D-1058~D-1064环境物件描写系列），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；新增NPC：Le Noir Porter→漆黑者搬运工
  - 继续（2026-09-17 04:35 checkpoint）：又翻完30条累计630条（D-1049黑暗之门场景，格里高尔怕进去+改走
    走廊/D-1050~D-1051环境描写/D-1056赤红者搬运工登场，抱怨补给中断+突然又听见"声音"陶醉贴墙），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；新增NPC：Le Rouge Porter→赤红者搬运工
  - 继续（2026-09-17 04:36 checkpoint）：又翻完30条累计660条（D-1036美食广场螺旋标记提示/D-1040堵死的门+
    让娜灰字"如同巨人的想象般浩瀚"金句/D-1042~D-1048喷泉溺水式狂饮苏打的顾客+眼球菜肴等美食广场环境描写
    系列/D-1071~D-1072被回避的诡异存在感场景），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:37 checkpoint）：又翻完30条累计690条（D-1072~D-1076默尔索被神秘力量撞飞+门纹丝
    不动的诡异哑剧梗，格里高尔自己也遇到同样怪事+调侃默尔索"脑袋没关严"/D-1077~D-1078遮光帘后诡异挤压声
    +喷溅声环境描写系列），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在
    Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:38 checkpoint）：又翻完30条累计720条（D-1079~D-1082诡异垃圾滑道场景+格里高尔独栋
    住宅吐槽+浮士德"象征界域不能套用城市常识"解释/D-1083~D-1090一批物件描写：贩卖机导览图+地图残片/
    肉铺陈列/眼球拾取/扶梯/副主厨语音片段等），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 04:39 checkpoint）：又翻完30条累计750条（D-1091~D-1101美食广场收尾环境描写系列（死者/
    尸体等）/D-1105~D-1107战斗过渡吐槽：格里高尔差点被剁+默尔索真的被剁手臂+副主厨"屠宰功夫名副其实"梗，
    「阴影」概念首次出现/D-1901副主厨语音片段），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - `rpg-loc-dialogue-floor-b1.json` ✅ **已完成**（2026-09-17 04:40，共763条译文，最后13条D-1107浮士德解释
    默尔索作为象征界域主体是与罪人互动的唯一媒介+队伍决定不砍格里高尔手臂+返回美食广场），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - floor-b1 剩余文件（按floor-4模式，先跑 batch_next 确认各文件规模）：quest-floor-b1 →
    npc-floor-b1 → npc-floor-b1-a-enemy → dialogue-choice-floor-b1 → narration-floor-b1（若存在）
  - `rpg-loc-quest-floor-b1.json` ✅ **已完成**（2026-09-17 04:41，共27条译文，Q-1000~Q-1011任务链：地下一层
    美食厅探索/扶梯迷宫寻路/追踪副主厨→拜访布彻→带回猎物反刍肉→定义扶梯"梯子/小山/鞋子"选择支线），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - `rpg-loc-npc-floor-b1.json` ✅ **已完成**（2026-09-17 04:42，共24条NPC名，卡基系列全套译名：干渴的卡基/
    饥饿的卡基/饕餮的卡基/饿到极致的卡基/谨慎的卡基/可疑的卡基+楼层经理/试味员/难以辨认的尸骸/通往黑暗的门
    等），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - `rpg-loc-npc-floor-b1-a-enemy.json` ✅ **已完成**（10条，眼睛/鼻子/嘴巴试味员+皮革钱包/丹宁钱包等敌人名）
  - `rpg-loc-dialogue-choice-floor-b1.json` ✅ **已完成**（13条，鞋子/小山/梯子选择支线+若干"进去/不进去/
    离开"通用选项）
  - **floor-b1 阶段全部完成**（2026-09-17 04:43，dialogue763+quest27+npc24+npc-a-enemy10+
    dialogue-choice13，共837条；narration-floor-b1.json不存在待译条目），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏。
    **进入 floor-b2（最后一个RPGSystem楼层阶段）。**
  - floor-b2 规模（2026-09-17 04:43 待确认，先跑 batch_next 看清单）：约710条待译，
    按floor-b1模式（dialogue先做，再quest/npc/npc-a-enemy/dialogue-choice/narration等收尾文件）
  - `rpg-loc-dialogue-floor-b2.json` 进行中（2026-09-17 04:44 checkpoint）：30条已翻完（D-20001开场蓝字
    旁白/D20200xxx地下二层楼层经理"号码券券"梗+排队顾客系列/新NPC"被压榨的染料"（Exploited Dye）+
    帕莱特/腻子（Putty）登场+染料储藏室通道场景），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏；Palette→帕莱特（沿用既有译法），
    新增NPC：Exploited Dye→被压榨的染料，Putty→腻子
  - 继续（2026-09-17 04:45 checkpoint）：又翻完30条累计60条（D-2000-1~D-2000-3奥提斯/良秀新组队登场，
    奥提斯吐槽分组标准+"I.O.T."缩写猜谜梗（含默尔索"经理？"打岔笑点）/阿赖耶识颤动伏笔），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏；Executive Manager→总经理（区别于常规"经理"）
  - 继续（2026-09-17 09:14 checkpoint，补录）：又翻完30条累计90条（D-2000-3剩余段+D-2000-4开头：
    阿赖耶剑鞘震动/默尔索用"M.B."(mediocre bunch)"W.W.A."(where we're at)缩写调侃"时钟"/
    奥提斯问良秀是否懂克罗默姐姐的缩写黑话/但丁心声吐槽/克罗默姐姐登场"你们就在自己想来的地方"），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏（此次 scan 发现新增/改写均为0，merge实际发生在上一轮会话未及时记录，此处补记）
  - 继续（2026-09-17 09:16 checkpoint）：又翻完30条累计120条（D-2000-4后段：但丁被克罗默姐姐嫌弃"滴答声"
    没有血肉/奥提斯质问她打什么算盘+她威胁"哼哧哼哧声在逼近"/她嘲笑队伍"没头绪"+D-2000-5开场但丁吐槽
    她一头撞墙；"D.D."=dilly-dally缩写梗，默尔索照常直译解密；"the Fount"沿用"源泉"，Chaplain沿用"牧师"），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 09:17 checkpoint）：又翻完30条累计150条（D-2000-6撞见"D.E."死路/前往丝绞巢+
    D-2001-1返回地面遇格里高尔，讲述被暴怒的东西追杀，良秀"感受到"其情绪+发现是金色蚕茧在作祟，
    队伍商议对策拦路）；"Skein Nest"沿用"丝绞巢"、"Golden Cocoon"沿用"金色蚕茧"，D.E./C.H.缩写梗未解密先保留原文，
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 09:18 checkpoint）：又翻完30条累计180条（D-2001-1收尾：辛克莱问起克罗默女人+
    奥提斯/但丁回忆她凭空出现嘲讽后撞墙/良秀"不能放松警惕"+撤退找别路；D-2002-1/D-2002-2：死后复活，
    克罗默姐姐得意"警告过你们了"+怪物已绕远路暂无威胁+调侃队伍"随心所欲磨蹭"+提到"下一次搁浅"），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 09:19 checkpoint）：又翻完30条累计210条（D-2002-2收尾"S.H.N.C."缩写梗+克罗默姐姐
    调侃队伍死得"滑稽可笑"退场；D-2002-3良秀通报"她又穿墙过去了"→默尔索接通讯耳机与克罗默本体("ma puce"
    法语称呼保留)调情式对话，奥提斯讽刺她"玩神明"+她佯装信号断了躲问题），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Jeanne沿用"让娜"
  - 继续（2026-09-17 09:21 checkpoint）：又翻完30条累计240条（D-2003-1到达"S.N."丝绞巢正门，讨论荣誉等级
    是否够格求金丝线；D-2004-1染料纺丝旁白；D-2005系列新NPC"帕莱特"（沿用既有译法）忙着卖"券券"/
    金色染料被抢购拒客；D-2006-1新增敌人"劳作的针族"1/2；D-2017-0通用离场旁白），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Prestige Tier沿用"荣誉等级"、Golden Skein沿用"金丝线"
  - 继续（2026-09-17 09:22 checkpoint）：又翻完30条累计270条（D-2006系列"劳作的针族"敌人补全+D-2008-1
    "排队的漆黑者"x4+D-2009-1帕莱特认可队伍已从"裸者"处拿到金色染料，商谈用"L'Incolore"（法语，保留原文）
    深海染料交换，帕莱特称无人排队直接可得），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏；Naked沿用"裸者"、Queueing Noir→排队的漆黑者
  - 继续（2026-09-17 09:23 checkpoint）：又翻完30条累计300条（D-2009-1收尾：帕莱特让队伍去戳破"哭泡泡"
    换取眼泪当染料原料；D-2010-1队伍返回交差，帕莱特却拿出"透明液体"糊弄，声称这就是"L'Incolore"，
    奥提斯察觉不对，帕莱特讽刺"记忆沾污/心已起球"暗示队伍认知有问题），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Putty沿用"腻子"、"blubber-bubbles"意译为"哭泡泡"（无既有术语，此处新造）
  - 继续（2026-09-17 09:24 checkpoint）：又翻完30条累计330条（D-2010-1核心哲学对话收尾：帕莱特坦白
    "纯粹之心可见的颜色"只是玩笑，讽刺纯真降生人世便幻灭+染料本质是无色透明的"什么东西"却耗费巨大心血
    制成；良秀吐槽染料是"破烂货"（S.L.O.P.=Seems Like Oil Pigment谐音梗）引发帕莱特恼怒，
    分析出油性无污渍特性），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 09:25 checkpoint）：又翻完30条累计360条（D-2010-1收尾：良秀拎着染料要走+"W.T.T.A."
    缩写梗+良秀更喜欢这桶"比G.D.雅致"；D-2011-1队伍把"L'Incolore"忽悠给裸者，奥提斯疯狂话术吹嘘
    "涟漪粘稠/晶莹剔透"忽悠他"心尚未起球"，最终成功换到金色染料），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 09:26 checkpoint）：又翻完30条累计390条（D-2011-1收尾：裸者彻底被忽悠折服，
    交出下一批金色染料+D-2012-1帕莱特收场旁白x3；D-2013-1蚕茧被绞丝惨叫，地下二层楼层经理登场预警
    "古老之物降临"+"受阻纺出的丝线永远织不出美丽的颜色"），apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；B2F Floor Manager沿用文件内既有译法
    "地下二层楼层经理"
  - 继续（2026-09-17 09:27 checkpoint）：又翻完30条累计420条（D-2013-1收尾：加固走廊防守蚕茧纺丝+
    黑色存在疑似折返；D-2015-1/D-2015-2蚕茧丝线抽尽，楼层经理让队伍绕成纱线带走，成功获得金丝线，
    但丁下令返回三楼；D-2016-1/D-2034-1但丁场景过渡；D-SH109001新增商店NPC"红色针族"卖针+
    D-SH109002裸者也开始摆摊卖东西），apply（无install）+ check 通过（无硬伤）+ scan --accept
    已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 09:28 checkpoint）：又翻完30条累计450条（D-SH109003帕莱特摆摊+D202210x系列纺纱机
    场景旁白（白线卷/纺纱机吐丝/丝线来源成谜）；D20221301克罗默撞墙处捡到"B.S."留言物+D20221401-402
    队伍操作纺纱机三大功能（抽取/纺丝/染色）+D20221411机器吸附默尔索皮肤，"O. of a K."缩写梗），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 09:29 checkpoint）：又翻完30条累计480条（D202214xx纺纱机连环梗收尾：机器反复吸附
    默尔索皮肤，良秀问"S.I.T."(split into threads)+"S.E.N.I.T."(split every nerve into threads)缩写梗，
    但丁记不清语境；最终吐出默尔索皮肤丝线+按钮再按触发针族劳工抗议产量失控+顾客怒目+染料耗尽警告，
    奥提斯质问总经理意图），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏；"Needlekin Laborer"沿用"劳作的针族"（与"Laboring Needlekin"
    同一敌人统一译名）
  - 继续（2026-09-17 09:30 checkpoint）：又翻完30条累计510条（D202214xx纺纱机彩蛋收尾：阿赖耶拍手肘
    暗示"别耍小孩子脾气"+但丁自我反省住手；D202215xx染色布料仓库场景过渡；D20221521核心桥段：门缝透出
    火车轰鸣与刺眼强光，但丁受惊尖叫，奥提斯发现缝隙里卡着一颗眼球并让默尔索取出，暗示门后是另一个
    "世界"/地铁站的诡异呼应），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 09:31 checkpoint）：又翻完30条累计540条（D-209001/002/005-007客户尸块/染料爆炸场景
    描写；D20221601天蓝色测试染料取样+良秀点评"有审美价值"；D20221701黑暗中默尔索摸到木屑；D20221801-804
    绿/黄/蓝/红各色染料场景描写，蓝色染料让良秀想起"小指父辈之廊"、阿赖耶却很喜欢；D20221901斑斓沙发
    +良秀与陌生人对瞪+剑鞘劝架；D20222001-002自动售货机上损毁的楼层指南），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    Pinky Nursefather沿用既有"Ring Nursefather→环指父辈"命名模式译为"小指父辈"
  - 继续（2026-09-17 09:32 checkpoint）：又翻完30条累计570条（D-2041/D-2041-2裸者身世独白：为登上五楼
    甘愿在地下楼层耗费数季青春，拒绝更多眼球贿赂；D-209008~011尸体旁白x4统一为"不过是具尸体罢了"；
    D20221805-816染料仓库大量桶装染料描写（纯度标签/待丢弃/不是这个/废弃处理/封死的桶等环境叙事）），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 09:33 checkpoint）：又翻完30条累计600条（D-2041-2主线收尾：裸者道出"L'Incolore"秘闻
    传说+良秀吐槽是隐形染料"谁会穿这种衣服"+裸者揭晓自己就是那个人+讨价还价后同意用金色染料交换+
    最终轮到他被叫去领奖被打断），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 09:34 checkpoint）：又翻完30条累计630条（D-2041-2/D-2041-3收尾：裸者答应交易条件+
    队伍决定回帕莱特处打探"L'Incolore"；D-2042新Boss"针线之王"登场呓语"黑色的……盛宴再临"，
    奥提斯坚持死守生产线，良秀提醒"C.H."准备战斗；D-2043战后余波+D-2044敌人"黑线"惨叫+D-2045
    地下二层楼层经理验收金色染料"配得上这缕丝线的美"），apply（无install）+ check 通过（无硬伤）+
    scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；新增专有名词：
    King of Needleworks→针线之王，Blackthread→黑线
  - 继续（2026-09-17 09:35 checkpoint）：又翻完30条累计660条（D-2045收尾：楼层经理三张脸紧盯默尔索口袋
    默默收下蚕茧；D-2801小怪群袭战后吐槽"M.U.G."(Mortally Urgent Gift)缩写梗+辛克莱挨剑鞘揍+小怪太小
    难以追踪；D-2802回顾染料哭泡泡经历，良秀觉得"挺有意思"提议干脆每种颜色都死一次试试），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 09:36 checkpoint）：又翻完30条累计690条（D-2802收尾：染料水坑成唯一威胁，再战一次；
    D-2803奇特桥段：但丁死后复活发现金色蚕茧竟"恢复原状"，默尔索证实"它确实被吞掉了但依然还在"，
    暗示时间被操纵——良秀"T.M."(Timepiece Move/Time Manipulated)双关缩写梗把但丁绕晕），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，
    未装进游戏
  - 继续（2026-09-17 09:38 checkpoint）：又翻完20条累计710条（D-209060/061裸者发现染料被换怒斥"胭红者"
    间谍（Rouge新势力，与Le Noir漆黑者对应译"胭红者"）；D-2803尾声出去查看+D-2804针族真相大白/
    商议是否赶回楼层经理房间保护蚕茧，默尔索安抚"那房间没那么好进"，队伍决定折返走廊），
    apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    **踩坑记录**：本轮merge时遇到Read工具与python直接读取的batch_pending.json内容不一致（Read显示floor-b2条目，
    但batch_merge却报错说文件是route-a的69条）——推测是文件系统缓存延迟，之后重新执行`python -c "import json..."`
    直接校验pending文件内容再merge，问题消失。以后每次batch_next后应直接用python校验pending文件真实内容，
    不要只信Read工具或命令行的echo输出
  - **`rpg-loc-dialogue-floor-b2.json` ✅ 已完成**（2026-09-17 09:38，累计710条，B2层主线终章：楼层经理验收
    金色染料→针线之王Boss战→黑线杂兵→蚕茧诡异复原伏笔→裸者染料东窗事发怒斥"胭红者"间谍）
  - `rpg-loc-quest-floor-b2.json` ✅ **已完成**（2026-09-17 09:40，30条：Q-2000~Q-2010任务链，
    探索地下二层→丝绞巢死路→绕路→楼层经理→染坊帕莱特→裸者排队交涉→染料仓库戳眼泪收集材料）
  - **用户指示（2026-09-17 09:40）**：优先插队翻译 `EN_rpg-loc-dialogue-route-a.json`
    （源文件路径：`D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en\RPGSystem\`，
    工程内对应 `rpg-loc-dialogue-route-a.json`），floor-b2剩余伴生文件
    （npc-floor-b2/npc-floor-b2-a-enemy/dialogue-choice-floor-b2，narration-floor-b2无待译）
    暂缓，先做完route-a对话文件再回头补
  - `rpg-loc-dialogue-route-a.json` 进行中（2026-09-17 09:41 checkpoint）：30条已翻完（D999999洗手间
    重置事件核心桥段：默尔索死亡触发全队"送回"洗手间但只有他和但丁记得发生过什么，众人围绕"背上钉满
    尖钉的怪物"猜测是扭曲还是异想体但都不像，格里高尔追问被打断），apply（无install）+ check 通过
    （无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 09:42 checkpoint）：又翻完30条累计60条（D999998桥段收尾：默尔索解释自己是"象征绑定
    主体"死亡即触发全队送回+罗佳吐槽"我们成鬼魂了"+奥提斯点出这机制"具有战术价值"；D999999尾声：
    默尔索揭示大百货商场被"重置"到某选择之前，暗示"选择未被锁链束缚"故触发重置，以实玛利/格里高尔
    等罪人对此毫无记忆），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏
  - 继续（2026-09-17 09:43 checkpoint）：又翻完9条累计69条，D999998+D999999两条开场剧情**全部完成**
    （李箱古雅措辞"茅厕"+辛克莱反对把洗手间死亡重置当逃生通道当哏），apply（无install）+
    check 通过（无硬伤）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏；
    李箱台词延续既有"诸位/阁下/可否/尚待商榷"式古雅现代汉语register
  - **`rpg-loc-dialogue-route-a.json` ✅ 已完成**（2026-09-17 09:43，69字段，D999998+D999999开场剧情，
    应用户指示插队优先完成）
  - **`rpg-loc-quest-floor-b2.json` ✅ 已完成**（2026-09-17 09:45，54字段，Q-2010~Q-2017收尾：
    收集三色染料→L'Incolore换金色染料→交给楼层经理→守卫纺丝→领取金丝线→离开地下二层前往三楼）
  - floor-b2剩余伴生文件：npc-floor-b2(19)、npc-floor-b2-a-enemy(7)、location-floor-b2(8，新发现文件)、
    dialogue-choice-floor-b2(4)；route-a剩余：npc-route-a-warden(1)
  - **`rpg-loc-npc-floor-b2.json` ✅ 已完成**（2026-09-17 09:46，19条NPC名：楼层经理/克罗默姐姐/裸者/帕莱特/
    针线之王/腻子/红色针族/劳作的针族x3/排队的针族x3/排队的漆黑者x2/蒙尘的金色蚕茧+SD小人立绘变体x3）
  - floor-b2剩余：npc-floor-b2-a-enemy(7)、location-floor-b2(8)、dialogue-choice-floor-b2(4)；
    route-a剩余：npc-route-a-warden(1)
  - **`rpg-loc-npc-floor-b2-a-enemy.json` ✅ 已完成**（2026-09-17 09:46，7条：浸软的黄色眼泪/溃烂的红色
    眼泪/溢流的蓝色眼泪+红色针族x2/绿色针族/黑线）
  - floor-b2剩余：location-floor-b2(8)、dialogue-choice-floor-b2(4)；route-a剩余：npc-route-a-warden(1)
  - **`rpg-loc-location-floor-b2.json` ✅ 已完成**（2026-09-17 09:47，8条地点名：纺纱厂/丝绞巢/走廊/染坊/
    染泪仓库/隐秘扶梯厅/丝绞巢走廊/染泪仓库走廊）；scan发现2条因源文件更新变为stale，后续批次会自动补上
  - floor-b2剩余：dialogue-choice-floor-b2(4)；route-a剩余：npc-route-a-warden(1)
  - **`rpg-loc-dialogue-choice-floor-b2.json` ✅ 已完成**（2026-09-17 09:48，4条：提取/纺丝/染色/乱按按钮）
  - **floor-b2 阶段（乃至整个 RPGSystem 楼层1~b2）全部完成！** 累计floor-b2共
    dialogue710+quest54+npc19+npc-a-enemy7+location8+dialogue-choice4 = 802条；narration-floor-b2
    无待译。**RPGSystem楼层部分（floor-1~floor-4、floor-b1、floor-b2）已全部完成，正式进入route-a阶段。**
  - route-a剩余：`rpg-loc-npc-route-a-warden.json`（1条）；dialogue-route-a.json已完成（69条，此前应
    用户指示插队完成）。scan发现2条floor-b2旧条目因源文件更新变stale，会在后续批次自动追上
  - **`rpg-loc-npc-route-a-warden.json` ✅ 已完成**（2026-09-17 09:48，1条：The Warden→典狱长，
    沿用既有"典狱长的大钉"译名前缀）
  - **route-a 阶段全部完成！RPGSystem 全部楼层+route-a 均已完成翻译。** 剩余53条待译分散在
    theater等其他RPGSystem文件及大批StoryData文件（S9991B/S951B/E519A等，疑似游戏更新带来的
    新增/改写内容，与楼层剧情无关）。下次开工先跑 `python scan.py` 看清单，按文件规模从大到小清理，
    theater若存在待译优先于零散StoryData杂项
  - **用户指示（2026-09-17 10:20）**：翻译前先检查StoryData官方中文目录（`LLC_zh-CN`）是否已有对应文件/
    条目，官方已译（哪怕是保留原文如"Gesellschaft"这类专有名词）就不要碰。核查后确认：scan 报的53条
    "todo"里只有6个文件是**真正**官方没有的（S9991B/E003I3/S308B/E406B/S1004B/rpg-loc-ui-common-a1c10p1，
    合计55条）；其余276条same_as_en+48条zh_placeholder基本是官方本就保留原文的专名（如`S951B.json`
    的title=Gesellschaft德语社交场名）或韩文占位，**不翻**。以后每次遇到same_as_en/zh_placeholder批量
    条目，先用python核对`LLC_zh-CN`对应文件是否真的缺失，不要无脑batch_next全部拉出来翻
  - `StoryData/S9991B.json` 进行中（2026-09-17 10:26 checkpoint）：翻完30条（id0~29，大百货商场"求永恒"
    哲学独白诗篇：从"必须永续"的圣歌体开场，到胭红者/漆黑者化为立柱的神话叙事，再到"渐近与收敛"的
    死亡哲学思辨），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
    只在 Workplace/translated/，未装进游戏；此文件官方无中文版（真todo，非same_as_en误报）
  - 剩余真todo：S9991B(15)、E003I3(4)、S308B(3)、E406B(1)、S1004B(1)、rpg-loc-ui-common-a1c10p1(1)
  - **`StoryData/S9991B.json` ✅ 已完成**（2026-09-17 10:27，累计45条id0~44，"大百货商场求永恒"完整
    哲学独白诗篇：尖钉/锤子二choice隐喻+"世界之树"意象+"心之种与永恒之种本是同一颗"收尾，
    结尾但丁心声"渐近与收敛确实有区别"呼应开篇思辨）
  - 剩余真todo：E003I3(4)、S308B(3)、E406B(1)、S1004B(1)、rpg-loc-ui-common-a1c10p1(1)
  - **`E003I3.json`（4条）/`S308B.json`（3条）/`E406B.json`（1条）/`S1004B.json`（1条stale）/
    `rpg-loc-ui-common-a1c10p1.json`（1条stale，返回主菜单确认框文案）全部完成**（2026-09-17 10:28）
  - **`python scan.py` 确认 todo/stale/outdated_official 全部清零（0/0/0）！**
    剩余276条same_as_en+48条zh_placeholder均已核实为官方本就保留原文的专有名词（德语/其他语言梗）
    或韩文占位符，**按约定不翻**。**至此 tier0（StoryData + PersonalityVoiceDlg + RPGSystem 全部楼层
    + route-a + 根目录点名文件）已翻译完毕，无待办。**
  - 下一步：等游戏后续更新产生新的英文原文变更时，`python scan.py` 会自动检出新增/stale条目，
    届时先查官方 `LLC_zh-CN` 是否已跟进翻译（尤其是same_as_en/zh_placeholder类，可能是官方特意
    保留原文），确认真的没翻再动手，参照本次踩坑经验不要无脑全量翻译same_as_en
  - **术语备忘（Ishy）**：用户确认 "Ishy" 是以实玛利（Ishmael）的昵称，简称"以实"，遇到按此翻
  - common 全部做完后，回头补 floor-1 剩余文件：`rpg-loc-dialogue-floor-1.json`（1205条，大头）→
    `rpg-loc-dialogue-choice-floor-1.json`（2条）→ `rpg-loc-npc-floor-1-a-enemy.json`（7条）→
    `rpg-loc-quest-floor-1.json`（44条）→ `rpg-loc-location-floor-1.json`（14条），
    floor-1 全部清零后才进 floor-2
  - **规模提醒**：RPGSystem 阶段总计约 6400+ 条待译（远超此前 Story/Bubble/RPG-BossRaid 阶段总和），
    这是一个跨多个会话的长期任务，每次开工先读这份 PROGRESS.md 的"当前进度"接着做，不要重新规划顺序。

## 新任务线：a1c10p1（第10章）机制文本补译（2026-09-17起）

RPGSystem楼层 + StoryData tier0 已于2026-09-17上午全部翻完（见上方"当前进度"，todo/stale/outdated_official
清零）。下午应用户要求，扫描了游戏根目录全部906个EN文件（超出原tier0范围），找到1437条官方真缺失
（排除same_as_en误报——已核实同类same_as_en多为官方本就保留原文的专名，不是真缺失）。缺口几乎全在
**a1c10p1（第10章，最新章节，官方中文尚未跟进）**的技能/被动/Buff机制文件。用户指示先做"技能"（Skills）。

已把以下4个文件永久加进 `config.py` 的 `TIER0_MECH_FILES`：
- `Skills_Abnormality-a1c10p1.json`（425条，待译）
- `Skills_Enemy-a1c10p1.json`（122条，**✅ 已完成**，2026-09-17 10:51）
- `Skills_personality-04.json`（709条，待译）
- `Skills_personality-08.json`（577条，待译）

合计1833条（比初步估算多，因为levelList/coinlist/coindescs嵌套字段比预估更深）。目前只完成122条
（Skills_Enemy-a1c10p1.json全部），剩余1711条规模巨大，**是一个需要多个会话才能做完的新任务线**，
与RPGSystem/StoryData那条并列，不要互相混淆进度。

**机制文本翻译方法论**（详见memory `mech-translation-templates.md`）：
- 这类文本不是叙事对话，是固定句式的游戏数值机制描述（Final Power/Coin Power/Potency/Count等），
  不能靠"自然口语化改写"那套，要去挖官方已译的同类文件（通常是上一赛季，如Skills_Enemy-a1c9p1.json）
  找精确原文匹配，照抄官方句式。batch_next.py吐出的`official_zh`字段是最高优先级参考，直接抄。
- `[Sinking]`这类方括号技能关键词ID必须保留英文（`_mech`作用域自动处理keyword_brackets规则），
  只翻方括号外的说明文字。
- 术语：Potency（强度型状态）→"X级[Keyword]强度"；Count（层数型状态）→"X层[Keyword]"；
  同一原文"Inflict N [X]"依据原文是否带"Count"字样二选一模板，不要混用。
- 遇到没见过的新keyword（如本次的ChargeNoir/NiddlePin/PenetrateResistDown等），没有术语库命中就
  按普通描述文字直译，保留方括号；但如果该keyword在同一文件的其他条目里已经出现过明确的官方/自译
  句式，要保持内部一致，不要每次都重新措辞。
- apply.py出的这些mech文件**尚未 --install 进游戏**，等Skills系列全部做完再统一问用户要不要装。

- `Skills_Abnormality-a1c10p1.json` 进行中（2026-09-17 11:21 checkpoint）：已翻完60/425条
  （Le Noir百货售货员异想体"衬衫区这边请/西裤陈列区就在这里/尊贵的顾客"系列话术+ChargeNoir/
  NoirNoComply机制；Le Rouge缝纫主题异想体"缝合/盖章/三重缝合/强势营销"+ChargeRouge/[SuperCoin]
  转化机制），apply（无install）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏

- `Skills_Abnormality-a1c10p1.json` 继续（2026-09-17 11:23 checkpoint）：120/425条（新增副主厨Sous Chef
  美食广场系列异想体："我在收集食材呢/开炒！让我炒起来/我不想被做成菜"等"...you hear?"口癖统一译作
  "……听见没？"；机制SapsareeSpices/SapsareeYammi/SapsareeCooking/SapsareeHungry/SapsareeShield等
  一系列新keyword、"啊呜啊呜/啊姆啊姆(官方)/咯嗝~"拟声词技能名），apply（无install）+ scan --accept
  已推进基线；只在 Workplace/translated/，未装进游戏

- `Skills_Abnormality-a1c10p1.json` 继续（2026-09-17 11:26 checkpoint）：180/425条（"信徒/教团"主题异想体
  "我听见了/换装机会/信仰没有白费/刮剥削/世界并非毫无意义/那声音与我同在"系列狂信徒台词+ChargeRouge/
  Wariness/ReliefSense/Sinking/UnresolvedFeelings机制，"WHUMP! THUMP! KRA-KOOM!"系拟声技能名），
  apply（无install）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏

- **术语修正（2026-09-17 11:29）**：用户指出"City"（专指Limbus世界观里的"都市"这个专有名词）
  被多次误译成"城市/城中/城里/本市"。全局搜索progress.json找到9处误译并修正为"都市"：
  S1003B.json#35、rpg-loc-dialogue-common-a1c10p1.json（D91001_A/D91020_A共3处）、
  rpg-loc-dialogue-floor-3.json（D3006共2处）、rpg-loc-dialogue-floor-4.json（D40819/D40815共2处）、
  rpg-loc-dialogue-floor-b1.json（D-1081）。已apply重新出文件。**以后遇到大写"City"（尤其"the City"）
  一律译"都市"，不要看语境翻成"城市/本市/城里"等**——这是设定的固定专有名词，不是普通名词city

- `Skills_Abnormality-a1c10p1.json` 继续（2026-09-17 11:33 checkpoint）：210/425条（RougeThreeCocoon
  邪教徒"做我自己……彻彻底底地做我自己……！"+马蹄声主题异想体"嗒嗒/嗒嗒尥蹶子/求你了把它们剪掉/
  嗒嗒嗒多刺耳"系列，机制ChargeNoir/NoirSuit/Realisation/NoirBindArmor/RougeThreeCocoonHit），
  apply（无install）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏

- `Skills_Abnormality-a1c10p1.json` 继续（2026-09-17 11:34 checkpoint）：240/425条（"多余的腿"马腿异想体
  续作："你不为那条多余的腿感到羞耻吗/我会把那东西砍掉就当是种慈悲/单腿踢击/单腿踢击-高定连环"，
  NoirSuit/Realisation/DefenseUp/ChargeNoir多重机制叠加），apply（无install）+ scan --accept
  已推进基线；只在 Workplace/translated/，未装进游戏

- `Skills_Abnormality-a1c10p1.json` 继续（2026-09-17 11:37 checkpoint）：300/425条（缝纫检验员系列
  "双针车打回去/十字扣眼打回去/手缝到底/给我吃下去"+NiddlePin/NiddlePinned机制；咳嗽黏液异想体
  "唔嗯/呃嗯/噗咳"+BloodyMucus/Nutrition机制），apply（无install）+ check 通过（无硬伤）+
  scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏

- `Skills_Abnormality-a1c10p1.json` 继续（2026-09-17 11:38 checkpoint）：330/425条（饥饿寒冷的病痛异想体
  续作："好冷/好疼我的躯干不听使唤了/饿冷好疼/走开"系列，BloodyMucus/Nutrition/ChargeRouge机制持续），
  apply（无install）+ scan --accept 已推进基线；只在 Workplace/translated/，未装进游戏

- `Skills_Abnormality-a1c10p1.json` 继续（2026-09-17 11:39 checkpoint）：360/425条，累计译文总数破9000条！
  （饥饿系列"好饿/什么能吃的/我听见了那声音/别那样/我想要/我是什么"+新增keyword BuffetFailed，
  收尾"虚弱的召唤：……握住我的手"），apply（无install）+ scan --accept 已推进基线；
  只在 Workplace/translated/，未装进游戏

- **`Skills_Abnormality-a1c10p1.json` ✅ 已完成**（2026-09-17 11:39，累计425条/362字段，第10章全部
  异想体技能：Le Noir百货售货员系列、Le Rouge缝纫邪教系列、马腿系列、缝纫检验员系列、饥饿病痛系列、
  "Voice"信徒系列），apply（无install）+ check 通过（无硬伤）+ scan --accept 已推进基线；
  只在 Workplace/translated/，未装进游戏
  **累计译文总数9002条！**
  剩余：`Skills_personality-04.json`(709)、`Skills_personality-08.json`(577)，共1286条

下一步：`python batch_next.py --size 30 --file Skills_personality-04.json --status todo,stale,outdated_official`

## 2026-09-23 新一轮（空库重开，官方更新后）

用户分配：先 ScenarioModelCodes 名表 → 非人格剧情（从 S1017B「My vision」起，跳过 P* 人格剧情）→ 一楼 RPG dialogue。
**每翻完一个文件立刻 apply.py 出成品**（用户明确要求），默认不带 --install。

- 2026-09-23 `_root/ScenarioModelCodes-AutoCreated.json` —— 82 条，1 批翻完，
  apply（无 install）已出产物；新造译名 18 条记入 glossary/session_terms.json
  （布布/布菲/斯卡蒂/凯尔希/艾丽妮/异端审判庭/梅厄斯/教团主教/深海信徒/深海教会/薛家家仆 等）。
- 2026-09-23 `StoryData/S1017B.json` —— 90 条，分 2 批（60+30）翻完，
  apply（无 install）+ check 通过（无硬伤）。本章称呼定名：Clock=钟、C.H.=钟头（良秀叫但丁）、
  M.P.=记毒（对应下文「记忆中毒」）、Meur=默尔、Fau=小浮（罗佳）、The Fount=泉、Prestige Tier=评级（沿用 pending）。
  尚未 scan --accept。

### 2026-09-23 22:50 断点（准备 clear，接手看这里）

progress.json 共 **1668 条 / 22 个文件**。

**slot a（本会话）已完成并 apply（无 install）：**
- `_root/ScenarioModelCodes-AutoCreated.json` —— 82 条
- `StoryData/S1017B.json` —— 90 条
- `RPGSystem/rpg-loc-dialogue-floor-1-b.json` —— 1044 条
- `StoryData/S1020B.json` —— 16 条
- `StoryData/S1021B.json` —— 10 条
- `StoryData/S1022B.json` —— 54 条

**slot b（另一个 agent 并行）已合批：**
- `RPGSystem/rpg-loc-dialogue-common-a1c10p2.json` —— 93 条
- `RPGSystem/rpg-loc-item-common-a1c10p2.json` —— 20 条
- `RPGSystem/rpg-loc-location-floor-b1-b.json` —— 2 条
- `RPGSystem/rpg-loc-narration-common-warden-boss-a1c10p2.json` —— 1 条
- `RPGSystem/rpg-loc-npc-common-a1c10p2.json` —— 1 条
- `RPGSystem/rpg-loc-npc-common-warden-boss-a1c10p2.json` —— 2 条
- `RPGSystem/rpg-loc-npc-floor-1-b-enemy.json` —— 7 条
- `RPGSystem/rpg-loc-npc-floor-1-b.json` —— 25 条
- `RPGSystem/rpg-loc-npc-floor-b1-b-enemy.json` —— 22 条
- `RPGSystem/rpg-loc-npc-floor-b1-b.json` —— 29 条
- `RPGSystem/rpg-loc-quest-floor-1-b.json` —— 23 条
- `RPGSystem/rpg-loc-swarm-mob-floor-1-b.json` —— 5 条
- `RPGSystem/rpg-loc-ui-common-a1c10p1.json` —— 14 条
- `RPGSystem/rpg-loc-ui-common-a1c10p2.json` —— 20 条
- `StoryData/S1018B.json` —— 58 条
- `StoryData/S1019B.json` —— 50 条

**未完成的在途批次（重要）：**
- `out/slots/a/batch_pending.json` 里有 **90 条未翻**：StoryData/S1023B、S1024B、S1025B，
  这 3 个文件已被 slot a 认领（`out/claims.json`，租约 4h）。
  接手方式：直接读这份 pending 填答案 → `batch_merge.py`；
  或 `python batch_next.py --abandon` 放回池子重新取批。

**用户指定的任务顺序：** 名表 → 非人格剧情（S1017B「My vision」起，**跳过 P\* 人格剧情**）
→ 一楼 RPG dialogue（已完成）→ 继续剧情 S1023B 往后（S1023B/24B/25B/26B/27B/28B/29B/S9992B/E003I3/S308B/E406B）。

**本轮生效的工作规则（用户明确要求）：**
- 每翻完一个文件立刻 `python apply.py`（不带 `--install`），不要攒批。
- **不跑 `check.py` / `consistency.py`**，也不逐条核对官方译法——省时间和 cost。
  只保留 `batch_merge.py` 的硬错误拦截（格式码/标签，不跑会整批崩）。
- 原文读 `Assets/Resources_moved/Localize/en`，官方中文对照读 `Lang/LLC_zh-CN`（已确认干净，无双语残留）。

**本轮新定译名**（全部已写进 `glossary/session_terms.json`，取批时会自动带 `agreed_terms`）：
布布(Pwie)/布菲(Buffet)、钟(Clock)、钟头(C.H.)、记毒(M.P.)、默尔(Meur)、小杜(Dubbs)、刀疤D(Scar D.)、
清仓(Liquidation)、西西弗刑、西西弗塔、快销服饰馆、千鸟格季/条纹季、树季、破灭之世、黄金松脂、
过眼瘾的顾客/护理顾客/拼命的顾客/赤贫的顾客/不耐烦的顾客、皮手套(Leather Glove)、
斯卡蒂/凯尔希/艾丽妮/异端审判庭/梅厄斯/教团主教/深海信徒/深海教会/薛家家仆、经理(当面称呼但丁)。

**尚未 `scan.py --accept`**，基线没推进。state.json 是 22:40 那次 scan 的快照。

## 备注

- `out/progress.json` 是官方译文库，真相以它为准；本文件只是人类可读的进度速览，不代替它。
- **`batch_next.py` 必须带 `--status todo,stale,outdated_official,same_as_en,zh_placeholder`**，
  默认只有 `todo,stale`，会漏掉 `same_as_en`（等于原文=未翻）和 `zh_placeholder`（占位符未翻）两种真正待办状态。
- 单文件流程：`batch_next.py --file X.json --status ...` 取批 → 填 `out/slots/<slot>/batch_answers.json` → `batch_merge.py` 合并
  → 重复直到该文件"没有符合条件的待译条目" → `python apply.py`（**不带 --install**，见上方规则变更）→ `python check.py`
  → `python scan.py --accept` → 本文件才算「完成」，记入上方完成记录，移动清单指针到下一个。
- **重要坑**：`batch_next.py` 读的是 `out/state.json`（上次 `scan.py` 的快照），不是实时 `progress.json`。
  每次 `batch_merge.py` 合并成功后，必须先 `python scan.py`（确认 diff 为 0/0/0）再 `python scan.py --accept`，
  然后才能再跑 `batch_next.py` 取下一批——否则会把已经翻完、刚合并进去的条目重复当作"待译"再拉出来一遍
  （亲测：S1013B 合并后不刷新 state 直接再拉批，原样又给出同一批 id0~19）。
  **2026-09-23 起 `batch_next.py` 会拿 `progress.json` 兜底过滤掉已合批条目**（打印「[过滤] state.json 已过期」），
  重复取批不会再发生；但 state 里的剩余条数仍是旧的，所以照旧先 scan 再取批。
- 每次 `batch_merge.py` 成功合并一批后，在这里追加一行「完成文件/批次 + 时间」（即使还没到 apply 阶段也要记，防止掉线丢批次进度）。
- 双语格式：`out/slots/<slot>/batch_answers.json` 里只填纯中文译文，不要手动拼原文——`apply.py` 会按 `config.BILINGUAL_JOIN`
  自动拼成"译文\n 原文"（译文在前，原文保留在后）。已验证产物如 `"咔嚓\n Thwack"`。
- **2026-09-17 修复**：`apply.py` 曾经每次都无条件整份重写 `Workplace/translated/` 下所有文件，
  导致用户在产物文件里的手改被反复覆盖（出过一次严重事故，靠 Cursor 本地历史才救回来）。
  现在 `apply.py` 会给每个输出文件按其 progress.json 里的译文内容算指纹，存进 `out/apply_state.json`；
  指纹没变化就跳过不重写。也就是说一个文件翻完定稿后，以后随便跑多少次 apply.py 都不会再碰它。
  `--force` 才会强制重写全部（有覆盖手改风险）。**结论：改译文永远只改 `out/progress.json`，
  不要手改 `Workplace/translated/` 或游戏目录里的产物——但即使不小心手改了，只要没触发该文件重新 apply，改动也不会丢。**
- **2026-09-23 流水线修复（6 处，均为脚本改动，不影响已有译文）**：
  1. `scan.py` 读 ZH 侧字段用的是 `zh_item.get(field)`，但 `field` 是路径串
     （`levelList[0].coinlist[2].coindescs[4].desc` / `texts[3].text`），永远读成 `None`
     → 把官方已译的嵌套条目全判成 `todo`。改用 `walk.get_by_path()`。
     实测受影响 **7551 条**（技能文件 + RPGSystem），修复后 7550 条正确识别为 `official`。
     `apply.py` 早就用的是 `get_by_path`，只有 scan 漏了。
  2. `batch_next.py` 取批时用 `progress.json` 过滤掉已合批条目，state 陈旧也不会重复发批。
  3. `batch_next.py` 排序从 `(file, key)` 字符串排改成 `(file, 条目order, 数组下标, 字段)`，
     避免 `texts[1]/texts[10]/texts[2]` 这种乱序把同一段对话打散。
  4. `batch_next.py` 的上下文支持 RPG：邻句在同一条目的 `texts[]` 数组内取，
     说话人读 `texts[N].speaker`，查官方中文按 `item_ids()` 的唯一 id（原来用裸 id，RPG 条目
     id 在 `key` 字段，永远查不到官方中文）。
  5. `batch_merge.py` 合批前检查文件归属：文件正被别的 slot 包着就拒绝合批（`--force` 可越过），
     防止租约过期后旧 agent 用旧答案盖掉对方重译的结果。释放认领时也把 `outdated_official` 算进"还没翻完"。
  6. `scan.py --accept` 在还有 `outdated_official` 时拒绝推进基线（`--force` 可越过）——
     否则 snapshot 一刷新这些条目就判回 `official`，而默认取批状态又取不到它们，等于永久丢失。
     `ourterms.record()` 同词异译改为报冲突并保留旧译名（原来静默覆盖）。
- Model 文件里遇到的专有名词处理：Sephirot（Malkuth/Netzach/Tiphereth/Hod 等）官方 ZH 保持英文不翻，我们跟随；
  LCD/LCB/LCCB 是系列缩写代号，原样保留；"N Corp."→"N公司"、"Kromer"→"克罗默"、"A Distant World"→"另一个世界"
  是术语表命中，已照抄；"Grand Magasin Sisyphe"→"西西弗百货" 是在其它已有官方译文文件里找到的既有译法，非术语表命中，
  以后遇到同名要保持一致。

## 安装包任务（2026-09-17）

用户要求把 `Workplace/translated/` 打包成玩家可下载自动安装的补丁包。已完成：
- `Installer/LLC_zh-CN/`：`Workplace/translated/` 的镜像拷贝，作为安装包 payload。
- `Installer/install.ps1`：Steam库自动检测（注册表 `HKCU:\Software\Valve\Steam` + 解析
  `libraryfolders.vdf` 找所有库盘）→定位 Limbus Company 目录→找不到则手动输路径→校验
  `LimbusCompany_Data\Lang\LLC_zh-CN` 存在→覆盖前备份到 `Installer\backup_时间戳\`→拷贝安装→
  报告结果。多个候选目录时列出让用户选。
- `Installer/install.bat`：双击入口，调用 `powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1`。
- `Installer/README.txt`：给玩家看的说明（前提：游戏内需先切换过一次简体中文，让LLC_zh-CN目录生成）。
- 已用 `Compress-Archive` 打包成 `tempworkplace/LimbusCompany_ZhCN_Patch.zip`（约542KB），
  可直接分发给玩家。
- 未在真实游戏环境测试运行 install.ps1（无法验证注册表自动检测在真实Steam环境下的实际效果），
  逻辑基于标准 Steam library 结构编写，如有问题需玩家反馈后再修。
- 下一步（用户尚未确认是否继续）：回到机制文本翻译，`Skills_personality-04.json`（709条）和
  `Skills_personality-08.json`（577条），共1286条，是本轮"技能翻了吧"任务的剩余部分。

## 2026-09-19 术语/一致性整顿（未 apply）
- glossary.json 手动区从 #275 起插：Sin/Sin Affinity/Peccatulum/Meat Soda/Syndicate/City/The City/Grand Magasin Sisyphe/Sisyphe/Stranger/Mannequin；Gluttony 贪食→暴食；Stranger 怪人→异乡人
- 新约定：键 `!` 前缀 = 大小写敏感（!Ticket !Soda !City !The City）；Glossary 匹配支持复数后缀
- 新增 limbus/ourterms.py + batch 字段 ours/pending_terms；consistency.py 审计；batch_merge 术语漏用软警告
- glossary/pending_terms.json：待定词（RPG 人名、Kaki→建议卡其者、Golden 材料前缀、Prestige Tier、Fount）
- 已修 progress：Fixer 修理者→收尾人、Syndicate 辛迪加→帮派、扭曲体→扭曲 ×2、喷泉→源泉 ×10、美味苏打→苏打/肉苏打 ×7、券券→号码牌/排队号 ×4
- 待处理（consistency.md）：Mannequin 0/39 用"人台"（人偶/模特混用）、Executive Manager、Putty 腻子/普蒂、Annette 裁缝/改衣师、Maison du Noir、Authenticity Certificate

## 2026-09-23 工作区清空 + 多 agent 并行支持
- 官方汉化包 2026-09-20 更新，覆盖了我们 72 个文件 / 6204 条。按约定清空工作区：
  删除 out/、Workplace/translated、Workplace/backup_*。保留 glossary/ 与全部文档、脚本。
- 官方定名已在 2026-09-20 写入 glossary.json #275 起（黑派/红派/褐派、黄金X、泉、小可爱、
  象征界/阴影界、杜布瓦/屠夫/居斯塔夫/含羞草/调色板/欧麦尔 等 73 条）。
- 新增多 agent 并行：LIMBUS_SLOT 环境变量分 slot；批次文件落 out/slots/<slot>/；
  out/claims.json 认领表（租约 4h）防止两个 agent 领到同一批；progress.json 读-改-写加跨进程锁
  （limbus/lock.py）；jsonio.save_json 改成临时文件+os.replace 原子写。
- 验证：两 slot 并发取批零重叠，并发合批 5+5=10 条无丢失，合批后认领自动释放。
- 待办：Prestige Tier 官方无固定译名（评级/客人的等级），下一轮自己定。

## 2026-09-23（续）改为按文件分工
- 认领表 out/claims.json 从条目级改成**文件级**：一个文件整份包给一个 agent，翻完才换下一个，
  保证同一段对话的上下文连续。batch_next 不带 --file 时自动接着翻自己没翻完的文件。
- 跨 agent 一致性三层：glossary.json（已定名）/ ours 字段（含另一 agent **未合批**的批次，
  标 [另一 agent 刚定]）/ glossary/session_terms.json（本轮新造译名共享台账，
  `python -c "from limbus.ourterms import record; record('EN','中文')"` 写入，
  对方下一批在 agreed_terms 字段看到）。
- CLAUDE.md 与 AGENTS.md 曾各自漂移（AGENTS.md 停留在旧版）。现统一：规则全在
  TRANSLATION_GUIDE.md，CLAUDE.md / AGENTS.md 只是 11 行指针。改规则只改一处。
- 验证：两 slot 自动分到不同文件、key 零重叠；并发合批 25+25=50 条无丢失；
  合批后同一 agent 下一批仍落在同一文件；假译文丢 color 标签被正确整批拒绝。

## 2026-09-23（续2）StoryData S1023B/S1024B/S1025B 出货，转 floor-4-b
- 已出货：StoryData/S1023B.json（34字段）、S1024B.json（20字段）、S1025B.json（62字段）——
  布布身世线（第2层→第4层回忆）+ 制鞋馆鞋子线 + 卡尔曼/默尔索阳光回忆线，全部完成。
- 转到 RPGSystem/rpg-loc-dialogue-floor-4-b.json（4楼对话，文件很大，总条目 1715+，
  只推进了开头 D40110/D40210/D40212/D40213 几个对话块，即"布布"被命名的桥段 +
  单脚人/四脚人的制鞋馆职场对话），已出货 120 字段，**剩余 ~1595 条待办未译**。
- 用户打断：暂停 floor-4-b，改做2楼对话。
  排查发现：RPGSystem/rpg-loc-dialogue-floor-2.json（无 -b）已全部 official/完成，
  真正待办在 **RPGSystem/rpg-loc-dialogue-floor-2-b.json**（共 445 条待办）。
- 已出货 floor-2-b 开头 D2002/D2002B/D2002C/D2002D/D2003/D2004/D2005 共 60 字段：
  希斯克利夫/浮士德/但丁一行在奢侈品馆（红派施工/翻新奢侈品馆的往事回忆）+
  浮士德那句神秘"阳光"心声（与 S1025B 卡尔曼线呼应，都市/阳光操控暗线）。
  新定译名（已 record 进 session_terms）：Brand Director → 品牌总监（注意此前
  floor-4-b/item-common 里出现过"品牌主管""品牌总监"两种旧译，以后统一用"品牌总监"）。
  **floor-2-b 剩余 385 条待办**。
- 用户说：以后任务由用户指派，先做完 2 楼对话。下次直接
  `python batch_next.py --file RPGSystem/rpg-loc-dialogue-floor-2-b.json` 接着翻。

## 2026-09-23（续3）转做 3楼B对话
- 用户指派：改做 RPGSystem/rpg-loc-dialogue-floor-3-b.json（3楼对话，共885条待办）。
  floor-2-b 暂停在 325 条剩余。
- floor-3-b 已出货 D3003~D3200C 段共 540 字段（4批），剩余 645 条待办。
  内容：辛克莱/奥提斯/默尔索/但丁在奢侈品馆3楼找剪刀→切开两件套的日常对话；
  一串环境描写（尸体/人台/装置艺术"坠落之微分"系列）；"通讯总机"支线（奥提斯对但丁
  求知欲的捧杀式吹捧）；"不可动摇者"商贩线开场——被钉在地上、眼窝空洞、被神秘红色
  "声音"（<color=#cf0000>）操控，呼应 S1025B 卡尔曼线和 floor-2-b 的浮士德"阳光"心声，
  都是都市操控暗线的一部分。
- 新定：Corp. → 公司（沿用已有"N公司/S公司"惯例）。
- 下次直接 `python batch_next.py --file RPGSystem/rpg-loc-dialogue-floor-3-b.json` 接着翻，
  D3200C 之后是 Flannel 角色登场，尚未查过其称呼/语气，翻前先查 CHARACTER_VOICE.md。

## 2026-09-23（续4）不可动摇者线出货
- floor-3-b 又出货 D3200C~D3205 段共 60 字段，累计 600 字段，剩余 585 条。
  "不可动摇者"商贩线完整译出：被红色声音操控，密谋唆使罪人们杀改衣师安妮特以夺取
  "摇篮"（红派在奢侈品馆造的东西）；辛克莱得知声音其实"住在默尔索怀里"大惊；
  背景一直有默尔索母亲录音带的声音在放，商贩却已"听不见"它了——这是本层楼暗线的
  核心场景，红色声音操控黑派/其他角色的具体机制在这里首次点破。
  法兰绒（Flannel，人台角色，已有译名）在 D3205 登场，尚未查过语气特征。
- 下次同样 `python batch_next.py --file RPGSystem/rpg-loc-dialogue-floor-3-b.json` 接着翻。

## 2026-09-23（续5）floor-3-b 全部翻完
- floor-3-b **已整份翻完**（"已翻完并交还"），累计出货 660 字段，含：法兰绒/毛毡两位
  黑派人台与但丁一行的对峙——黑派威胁"交出神器（默尔索身上那件）否则开战"，
  罪人方拒绝，黑派放话"西西弗百货靠黄金松脂撑着，红派为披上圣松脂正在自我毁灭"；
  辛克莱对"要不要杀改衣师"表示犹豫，奥提斯纯粹按利益（大量眼球报酬）盘算。
  新定：堂吉诃德称呼其他罪人"Young XXX"固定译"小XX"（已写入 CHARACTER_VOICE.md）。
- 用户中途补充规则：堂吉诃德叫别的罪人（Young Rodion等）统一"小XX"，
  已记入 CHARACTER_VOICE.md「堂吉诃德」条目。
- floor-3-b 完工，下一步等用户指派新任务。已出货文件：StoryData/S1023B~S1025B、
  RPGSystem/rpg-loc-dialogue-floor-2-b.json（部分，剩325条）、
  RPGSystem/rpg-loc-dialogue-floor-3-b.json（全部完成）、
  RPGSystem/rpg-loc-dialogue-floor-4-b.json（部分，剩~1595条）。

## 2026-09-23（续6）floor-2-b 全部做完
- 用户指派"2楼把所有内容做完"。floor-2-b 原本 385 条待办全是 same_as_en 状态（官方
  已有条目但等于英文原文，即官方也没翻），batch_next.py 默认 --status todo,stale 不包含
  same_as_en，需要显式加 `--status todo,stale,same_as_en,zh_placeholder,outdated_official`
  才能取到。已记录：以后要"整层/整文件全翻完"，必须带上这个 --status 参数，否则会漏掉
  same_as_en 状态的条目。
- floor-2-b **已完全翻完，0 条剩余**，本轮共出货 8 批，包含：
  希斯克利夫/浮士德/默尔索/但丁一行清理二楼战场找路上楼；茧蛋剪开后布布诞生的完整桥段
  （品牌总监死亡宣告"沉睡者苏醒"→布布从摇篮爬出→不会说话，用手势和呜咽沟通→希斯克利夫
  用"假装抛弃"哄布布跟上→布布想吃血肉被制止）；默尔索与但丁反复讨论"不一样的选择"，
  浮士德察觉但丁知道某种自己接触不到的知识（暗示循环记忆/元叙事）；默尔索边说"小可爱"
  的罐头戏剧往事（呼应默尔索母亲那条录音带线）；进入奢侈品馆财富柜台区，希斯克利夫想顺
  黄金皮革被制止（"头发抵用券事件"梗）。
- floor-2-b 整份完成，与 floor-3-b 一样。当前状态：
  StoryData/S1023B~S1025B（完成）、floor-2-b（完成）、floor-3-b（完成）、
  floor-4-b（剩~1595条，暂停）。等用户下一个任务指派。

## 2026-09-23（续7）用户要求持续自觉认领直到RPG做完
- 用户："把现在未完成的工作做完，然后自觉接着认领，直到rpg内容做完，记得不要冲突。"
- 关键发现：floor-4-b 剩余条目状态多为 same_as_en（官方有条目但等于英文原文），必须用
  `--status todo,stale,same_as_en,zh_placeholder,outdated_official` 才能取到，默认
  `--status todo,stale` 会漏掉。以后整份处理都要带这个参数。
- apply.py 有时会报"写出 0 个文件"（当所有待写文件哈希未变时的误判），此时要加 `--force`
  强制重写，才能把 progress.json 里已合批但因为哈希比对失败没落盘的内容写出来。
  已验证 --force 不会丢内容，只是重新生成 Workplace/translated 下的文件。
- floor-4-b 持续推进中：布布被单脚人辱骂"红派杂种"引发冲突桥段全部译完；布布学会
  "举手提问"礼仪桥段译完，进入下一段（制鞋馆继续探索，堂吉诃德发现"快乐衣橱"）。
  累计本文件已出货 660 字段，剩 1415 条。
- 协作：与 slot b（Bufs-a1c10p2.json / floor-b2-b.json 等）保持文件级认领互不冲突，
  claims.json 是唯一真源，每次 batch_next 前不需要手动检查，脚本自动跳过已被占用的文件。
- 下一步：继续 `python batch_next.py --file RPGSystem/rpg-loc-dialogue-floor-4-b.json
  --status todo,stale,same_as_en,zh_placeholder,outdated_official` 翻完 floor-4-b，
  再用不带 --file 的 batch_next（同样带 --status 全集）自动挑起其他未认领的 RPG 文件，
  直至 RPGSystem 范围全部清零。

## 续8 (2026-09-23)
- 继续按用户指令"未完成做完→自觉接着认领→做完整个RPG"，floor-4-b 继续推进。
- 本轮完成：D40231C(布布无鞋)、D40314/D40310/D40312/D40312B(快乐衣橱初遇)、D40313/D40311/D40311B(驼背落地灯讨衣服戏)、D40311C(布布欲言又止)、D40411/D40610/D40611(快乐衣橱分支复用同场景，需单独翻)。
- floor-4-b 剩余 1295 条（--status todo,stale,same_as_en,zh_placeholder,outdated_official）。
- 常规流程不变：batch_next(带完整status)→翻译→merge(缺key就查pending里的speaker/text字段补全)→apply→scan --accept。
- 下一步：继续 batch_next --file floor-4-b，直到该文件剩余为0，然后去掉 --file 自动认领下一个未认领RPGSystem文件，直到RPG内容全部做完。

## 续9 (2026-09-24)
- floor-4-b 继续推进：D40715(双子台灯买卖)、D40810/D40813(挖心脏碎片、堂吉诃德徽章往事)、D40811/D40814/D40812(家具哄抢快乐衣橱、驼背落地灯抢客)。
- 修正了两处术语遗漏：Fixer→收尾人、Red Mist→殷红迷雾（直接改out/progress.json的zh字段，因为merge后才发现）。Skinhide Couch→人皮沙发 也补过两次，注意以后碰到这个家具第一时间就用"人皮沙发"不要写"皮革沙发"。
- floor-4-b 剩余 935 条左右（--status全集）。继续同样流程。

## 续10 (2026-09-24)
- floor-4-b 继续：D41904-D41929(鞋子展示区flavor文本)、D40740-40755(家具搭话/光线影响交流的发现)、D42030/D42030A/D42030B(多罗西娅身世、家/西西弗刑罚往事、五楼线索伏笔)。
- 剧情向术语记得核对 glossary：red gaze→猩红凝视、Golden Hide→黄金皮革，本轮均发现漏用后手动改了progress.json的zh字段修正。
- floor-4-b 剩余约755条。继续同样流程 batch_next→翻译→merge→apply→scan。

## 续11 (2026-09-24)
- floor-4-b 继续：D42061-D42064(多罗西娅殉道，迷童中心/凑齐心脏碎片做拖鞋/五楼钥匙)、D42070-D42080(新角色蕾妮Renée登场、红派/黑派手袋馆设计师、虚无者Néant设定)。
- 新增专名记入session_terms：Renée→蕾妮，Le Rouge Handbags Hall Designer→红派手袋馆设计师。黑派对应黑派手袋馆设计师同理沿用。
- floor-4-b 剩余约575条。继续同样流程。

## 续12 (2026-09-24)
- 用户提醒检查三楼(floor-3-b)。核实发现之前"0剩余"结论有误——那次用的是窄status过滤(todo,stale)，实际用完整status集合(含same_as_en)查还剩529条(525 same_as_en + 4 todo)，跟floor-2-b同样的坑：官方zh==en，也得我们自己翻。
- floor-3-b未被任何slot claim，后续做完floor-4-b后要记得回去清它，不能再漏。
- floor-4-b继续：D42080-D420831(黑派手袋馆设计师收藏黄金材料造"杰作"包袋子女、布布拆台"没这么好"引出比拼)。剩余约515条。

## 续13 (2026-09-24)
- floor-4-b 继续：D420831-D420846(黑派手袋馆设计师黄金布料执念、勒死"不够好"的孩子们、下降地底找兽皮的疯狂决心)、D420846C-F(布布问但丁们"为什么抛弃"，堂吉诃德讲梦想道理，布布质问五楼后能否留下)。
- 术语修正记录：Golden Fabric→黄金面料（不是黄金布料），Golden Thread→黄金线（不是黄金丝线），已在progress.json里手动订正过。
- floor-4-b 剩余约395条。continue同样流程。三楼(floor-3-b)剩529条仍待补，做完4楼后处理。

## 续14 (2026-09-24)
- floor-4-b 继续：D42087B结尾(默尔索"铭记vs体验"哲思收尾)、D42090/D42091(电梯故障)、D41320(快乐衣橱残骸/心脏发现)、D42063(多罗西娅死后余音，紫罗兰花香)、D42066-D42069(深入救多罗西娅、黄金皮革从墙上剪下)。
- floor-4-b 剩余约275条，接近尾声。做完后转去处理三楼(floor-3-b)剩余529条same_as_en。

## 续15 (2026-09-24)
- 用户提问三楼安装情况：核实LLC_zh-CN/RPGSystem/rpg-loc-dialogue-floor-3-b.json 与 Workplace/translated 内容一致(diff无差异)，已翻部分确实生效；游戏仍显示英文的是那529条same_as_en，属于尚未翻译，不是安装问题。
- floor-4-b继续：D42093尾声(让娜大段"生与死/红派黑派本质"独白)、D4960-D4981(单脚人黑化攻击同伴、家具们被打的惨叫、黑派/红派手袋馆设计师崩溃戏)。
- floor-4-b剩余约155条，快完了。完了立刻处理三楼529条same_as_en。

## 续16 (2026-09-24)
- 用户要求检查是否还有其他文件漏了类似三楼same_as_en的坑。用完整status统计全部actionable，结果：
  - floor-b2-b: 681条same_as_en，已被slot b认领在做，不用管
  - floor-4-b: 剩155条same_as_en(本轮正在清)
  - StoryData零散same_as_en/zh_placeholder：合计数百条，较大的S951B(41)、E519A(40)，其余多为个位数～十几条
  - 其余文件(floor-b1-b/b3-b/5-b、_mech各文件、quest/npc等)都是todo状态，是正常未开始，不是隐藏坑
- 结论：本轮做完floor-4-b后，需依次清理：①三楼525条same_as_en ②StoryData零散same_as_en/zh_placeholder（S951B/E519A优先）。floor-b2-b是b的地盘不用管。

## 续17 (2026-09-24)
- floor-4-b继续：D42094-D42098(布布玩滑梯,温馨戏)、D42099-D42101(寻人启事,但丁看到"脸上有烧伤疤痕"线索伏笔)、D42102-D42106(骰子/积木flavor、多罗西娅安葬)、D4901-D4902(黑派设计师"觉醒孩子们")、DDS401起(异想体战斗前对话)。
- floor-4-b接近尾声，剩余个位数~十几条。做完后转去清三楼(floor-3-b)525条same_as_en。

## 续18 (2026-09-24)
- floor-4-b确认完成（DDS402/403等收尾战斗对话、黑派手袋馆黑暗描写、滑梯flavor全部翻完）。scan后一度冒出149条属正常刷新，非漏译。
- 用户指令：先做完三楼漏的same_as_en，做完后要回查之前完成的工作有没有漏。
- floor-3-b正在清：D32052系列(让娜大段"清仓/评级/罐头体验"设定说明——术语：Liquidation→清仓，Prestige Tier→评级，Canned Experience→罐头体验，Lobotomy Corporation→脑叶公司，ma puce→小可爱)、D3206(改衣师安妮特开场——术语：Annette the Alterationist→改衣师安妮特，Alteration Shop→改衣室)。
- floor-3-b剩余约345条。做完后按用户要求，回查之前"完成"的文件(floor-1-b/2-b/b1-b等slot a认领过的)是否也有same_as_en被漏。

## 续19 (2026-09-24)
- floor-3-b继续：D3206-D3218(改衣师安妮特剪刀线,辛克莱奥提斯拿剪刀反黑派)、D3181/D3182/D3921/D3922(3楼楼层经理拉长音台词——术语Floor Manager→楼层经理，拉长音风格用～～～)、D3001-D3115(辛克莱奥提斯日常互动,默尔索"恋人关系"伏笔线索)。
- floor-3-b剩余225条。继续同样流程。

## 续20 (2026-09-24)
- 用户明确：不用回查之前完成的工作了，遇到问题再说。继续按原计划推进。
- floor-3-b继续：D3115/D3112/D3114(让娜再次登场自我介绍)、D3301-D3303(两件套会议台词、辛克莱奥提斯遇到布布真身)、D3305-D3308(不可动摇者献礼红手帕后自爆——术语L'Inamovible→不可动摇者)、D3923/D3861(黑派尸体、"坠落的微分"装置艺术介绍辛西娅)。
- floor-3-b剩余105条。继续同样流程做完，然后自动认领下一个未认领的RPGSystem文件。

## 续21 (2026-09-24)
- 三楼(floor-3-b)全部做完：主对话文件 + 选项文件(rpg-loc-dialogue-choice-floor-3-b.json)均清零，已apply。
- 用户要求"做完3先停，准备clear"——已完成，等待下一步指示。

## 续22 (2026-09-24，slot b)
- 用户指定顺序：先气泡、再 Boss 技能、最后剩余楼层；每完成一份文件立即输出到 `Workplace/translated/` 并校验。
- 完成 `BattleSpeechBubbleDlg-a1c10p2.json` 19 条；`Skills_Abnormality-a1c10p2.json` 320 条、`Skills_Assist-a1c10p2.json` 113 条。上述三份均已单独 apply、check 无硬伤。
- 完成地下三楼 `rpg-loc-dialogue-floor-b3-b.json` 余下 407 条（全文件共应用 707 字段），统一 Wriggley→蠕蠕；以及 quest 71、npc-enemy 25、npc 10、swarm 9、location 8 条。各文件完成后均单独 apply，check 无硬伤。
- 下一步：slot b 处理五楼及其他尚未分配的楼层文件；slot c、d 分别处理地下一楼、地下二楼，按文件认领避免冲突。

## 续23 (2026-09-24，slot a)
- 用户要求：先做完4楼5楼，再故事(StoryData)做完，再RPG其它剩余做完。当前无任何claim，重新以slot a认领开工。
- 4楼5楼已清零：quest-floor-4-b.json(92条)、swarm-mob-floor-4-a/b.json(5条)全部翻完apply。
- StoryData按剩余条数从大到小推进：P10705.json(72，官方译文直接复用)、S1026B.json(53，手袋馆多罗西娅送鞋/黄金裹布桥段)、
  S951B.json(41，浮士德们の Gesellschaft 集会——标题固定是德语"Gesellschaft"未译)、E519A.json(40，LCA/LCD缩写标题不译)、
  S9992B.json(40，布菲/大百货吞噬主题的诗化独白)全部完成，已apply+scan --accept。
- StoryData剩余 318 条（--status全集），继续从大到小接：S1029B(33)、S1027B(30)、S203B(24)、S308B(24)、S1028B(23)……
- 下一步：继续 batch_next（不带--file，带完整status）自动挑StoryData剩余文件，做完story后转RPGSystem剩余（floor-b1-b 383、floor-b2-b 381、player-route-b 16、npc-route-b 9(slot f占)）。

## 续24 (2026-09-24，slot a)
- 用户中途打断："把RPG翻完，S03这些显然不是这次更新的老StoryData文件以后不要翻了"——已停止StoryData工作，转做RPGSystem剩余；已写feedback memory记录这条规则（S001A/S2xx/S3xx/S7xx/S8xx等老章节same_as_en/zh_placeholder不属于本次更新范围，不要主动认领）。
- 转做 floor-b1-b（地下一楼对话），已推进两批，共翻完~223条明细key（含屠夫/驼背落地灯/浮士德-布布"回家"对话、被堵住的门/血肉苏打/垃圾滑道等场景），merge时联动带出的重复文本一起清零，累计该文件已应用1440字段。
- floor-b1-b 剩余223条左右，继续 batch_next --file floor-b1-b。
- 下一步：做完floor-b1-b后转floor-b2-b(381条)、player-route-b(16条)。npc-route-b(9条)仍是slot f的claim不要碰。不要再碰StoryData老章节。

## 续25 (2026-09-24，slot a)
- floor-b1-b 持续推进：副主厨(Sous Chef)全套戏份翻完（"听见没？"语气词贯穿全程）——猎物反刍肉交涉、黄金皮革索要、副主厨被打后的哭诉台词；水箱幼虫场景（默尔索/布布关于生死的对话，布布觉得"死了就不疼了但还是不喜欢"）。
- floor-b1-b 剩余23条左右，快完了。完了转 floor-b2-b(381条)、player-route-b(16条)。

## 续26 (2026-09-24，slot a)
- floor-b1-b（地下一楼对话）全部完成并apply，scan确认0剩余。全篇涵盖：屠夫/副主厨戏份、水箱幼虫场景、格里高尔手臂变肉块伏笔、沙滩场景、虚无者初现等。
- 下一步：转 floor-b2-b（地下二楼对话，剩余待查，原估381条）。做完后 player-route-b(16条)。npc-route-b(9条)是slot f的地盘不要碰。StoryData老章节不要碰（见feedback memory）。

## 续27 (2026-09-24，slot a)
- floor-b2-b 持续推进：黑派职员经理阵亡台词、调色板/油灰/裁缝之王与针族群像（拟声语"扎扎/舔干净"风格）、地下2层楼层经理死亡场景、克罗默穿墙伏笔纸条、纺织机三功能(提取/纺线/染色)开局。
- floor-b2-b 剩余约261条。继续 batch_next --file floor-b2-b。

## 续28 (2026-09-24，slot a)
- floor-b2-b 持续推进：布布单独进入夹缝场景(听见丝线跑动声/被留意跟随)、染料房(天蓝/绿/黄金色染料样本)、S.I.T./S.E.N.I.T.谐音梗已翻完并apply。
- floor-b2-b 剩余约141条。继续 batch_next --file floor-b2-b。

## 续29 (2026-09-24，slot a)
- floor-b2-b 持续推进：染料房系列(绿/黄/蓝/红染料，良秀对小指父辈走廊蓝光的抵触、T.A.R.T.谐音梗"Torrid and rhapsodic taste"、布布坐沙发/油灰警戒)。
- floor-b2-b 剩余约101条。继续batch_next --file floor-b2-b。

## 续30 (2026-09-24，slot a)
- floor-b2-b 持续推进：染料桶群(紫/蓝紫/红紫/绿/透明疑似无色染料L'Incolore的布布诗意形容"安静的悲伤的哗啦哗啦的"、良秀"艺术不是简单观察再现"梗)、调色板/油灰再遇+黄金松脂交涉开局。
- floor-b2-b 剩余约61条。继续batch_next --file floor-b2-b。

## 续31 (2026-09-24，slot a)
- floor-b2-b 持续推进：调色板/油灰黄金松脂交涉冲突线("我还以为你会不一样呢"重复台词分支)、但丁识破调色板真实诉求是"剪刀"不是黄金面料的伏笔。
- floor-b2-b 剩余约21条，快完了。做完后转player-route-b(16条)。

## 续32 (2026-09-24，slot a)
- floor-b2-b（地下二楼对话）全部完成并apply，scan确认0剩余。收尾内容：油灰重伤/爆炸场景、老木桶纸条(调色板对姐姐的心意"正午蓝")、布布与默尔索关于排队公平性的哲学对话、丝线战斗对策(P.T.谐音梗)。
- 下一步：转 player-route-b(16条)。npc-route-b(9条)是slot f地盘不要碰。StoryData老章节不要碰（见feedback memory）。

## 续33 (2026-09-24，slot a)
- player-route-b.json(16条角色名列表)全部完成并apply。
- RPG范围内未认领剩余：BattleKeywords-a1c10p2.json(125)、Passives_Abnormality-a1c10p2.json(123)、Voice_Rodion_Contem_10917.json(48)、rpg-loc-player-route-a.json(13)、几个swarm-mob零散文件(个位数~十几条)。npc-route-b(9条)是slot f地盘不碰。StoryData老章节(S0xx/S2xx/S3xx等)按用户指示不碰。
- 下一步：继续认领 BattleKeywords-a1c10p2 或 Passives_Abnormality-a1c10p2（这两个是本次更新的机制文本，量最大）。

## 续34 (2026-09-24，slot a)
- BattleKeywords-a1c10p2.json(机制关键词，地下2层裁缝相关buff：染料/剪刀/黑曜神祝福等)推进40条，剩余约45条。

## 续35 (2026-09-24，slot a)
- BattleKeywords-a1c10p2.json（机制关键词）全部完成并apply：染料/剪刀/裁缝相关buff、黑曜神祝福/黑派保存圣域、布布"失控暴走/黄金启示/呕吐"系列(布布黑化描写)全部翻完。
- 下一步：继续 Passives_Abnormality-a1c10p2.json(123条) 或 Voice_Rodion_Contem_10917.json(48条)。

## 续36 (2026-09-24，slot a)
- Voice_Rodion_Contem_10917.json（罗佳裁缝人格语音）全部完成并apply：改衣师/剪刀主题台词，"呼呼"语气词，黑派/红派对黄金面料的觊觎伏笔。
- 下一步：Passives_Abnormality-a1c10p2.json(123条，剩余RPG范围内最大文件)。

## 续37 (2026-09-24，slot a)
- Passives_Abnormality-a1c10p2.json（异想体被动机制）推进40条：远古水族异想体系列(黑线/回归远古之水)、不凋花/春之降临、改衣师被动"改衣"/"调整版型"（TailoringTarget/ScissorsMark/FinishedFabric机制链）。
- 排版标签坑：149501#desc 原文里"Surfile à la Chaîne"整体也被<color><mark><b><u>包裹，一开始漏包被batch_merge硬拦截，已订正。以后遇到多段同类高亮标签，要逐句核对包裹范围，不能只看"意思差不多就行"。
- Passives_Abnormality-a1c10p2.json 剩余约43条。继续batch_next。

## 续38 (2026-09-24，slot a)
- Passives_Abnormality-a1c10p2.json 全部完成并apply：改衣师安妮特(裁剪/永不停歇的剪刀)、黑派面料/保存系列被动(150401-150504大量重复被动，直接复用译文)。
- 下一步：查看剩余RPG范围文件列表，继续清理。

## 续39 (2026-09-24，slot a)
- Passives_Abnormality-a1c10p2.json 继续清理：制革工坊/鞣制囚徒系列(148801-148805)、针族"手工制作"、茧的投诉台词长文本(大量沿用official_zh)、针线之王"刺目阳光之雨"多份重复被动。
- 剩余约3条(该文件)。RPG范围继续：BattleKeywords-a1c10p2.json还剩45条待清。

## 续40 (2026-09-24，slot a)
- BattleKeywords-a1c10p2.json 继续清理：制革厂规则系列(禁止损伤生皮/催促鞣制/攻击/防御行为)、西西弗宝石buff(蓝宝石/缟玛瑙/钻石)、刺目阳光之雨多角色分支(副厨/3F楼层经理)、监管失灵。
- 待办总数剩415条(全RPG+StoryData混合)。继续用 python -c 统计per-file剩余，挑最大文件继续。

## 续41 (2026-09-24，slot a)
- BattleKeywords-a1c10p2.json 全部完成并apply：黑派上级士气低落/恐慌"遁入最初之壳……"、监管失灵。
- 下一步：rpg-loc-player-route-a.json(13条)、rpg-loc-swarm-mob-floor-1/2-a.json(个位数)。

## 续42 (2026-09-24，slot a)
- rpg-loc-player-route-a.json(13条角色名)全部完成并apply。
- 下一步：rpg-loc-swarm-mob-floor-1-a.json / floor-2-a.json（个位数）。RPG范围剩余已很少，之后转向StoryData同类现更新章节文件(P/E/S9xx等，注意甄别是否S03类老章节)。

## 续43 (2026-09-24，slot a)
- ScenarioModelCodes-AutoCreated.json(20条，Sephirah/角色代号昵称，均为英文缩写LCD/LCCB/LCB或音译Malkuth/Netzach/Hod/Tiphereth保持原文)全部完成并apply。
- rpg-loc-swarm-mob-floor-3-a.json(4条)全部完成并apply。
- scan.py --accept 后剩余362条actionable，逐一核对：除 rpg-loc-npc-route-b.json（slot f占用中，跳过）外，全部是StoryData老章节（S1029B/S1027B/S203B/S308B/S1028B/S207A/3D102A/P10116/P10903/S205A/E513A/S209A/P10406/P10804/P11114/P11115/S208B/S219B/3D309A/S001A/S311B/E003I3/P10314/PC07B/S215A/E512A/S204B等）。
- 按用户明确指示"S03这些显然不是这次更新，以后不要翻了"，这些老章节全部跳过不翻。RPG范围内的工作（除f占用文件外）已全部完成。
- 下一步：等待用户确认哪些StoryData文件属于本次a1c10p2更新（如有），或指派新范围；不再自行认领StoryData老章节。

## 续44 (2026-09-24，slot a)
- Passives_Abnormality-a1c10p2.json(151201号，Shower of Stinging Sunshine三条：desc/name/flavor)完成并apply，claims.json释放。
- 至此RPG/_mech/PersonalityVoiceDlg范围内slot a认领工作全部完成，唯一剩余的rpg-loc-npc-route-b.json仍由slot f占用。
- 剩余actionable全是StoryData老章节（S0xx/S1xxx/S2xx/S3xx/E/P/3D/7D旧编号），按用户指示不翻。
- 等待用户指派新范围（如确认哪些StoryData文件属于本次a1c10p2更新）。

## 续45 (2026-09-24，slot a)
- f已离场，接手rpg-loc-npc-route-b.json(9条：Pwie幼儿发音"布布"沿用agreed_terms、黑派祭司/店员/品牌世家/当代服饰馆店员/制鞋馆店员均用ours/官方)全部完成并apply，claims.json释放。
- 至此RPG全域（RPGSystem+_mech+PersonalityVoiceDlg）本次更新范围全部清空。
- 剩余actionable全是StoryData老章节文件，按用户指示不翻，等待新范围指派。

## 续46 (2026-09-24，slot a)
- 用户指出：布布(Pwie)在英文原文中用they/them/their(单数they)指代，中文应译"祂"而非"他/他们"。
- 全库排查所有Pwie相关条目的代词使用，修正5处：
  - StoryData/S1022B.json#53#content
  - RPGSystem/rpg-loc-dialogue-floor-4-b.json#D40110#texts[35].text
  - RPGSystem/rpg-loc-dialogue-floor-4-b.json#D40214#texts[4].text
  - RPGSystem/rpg-loc-dialogue-floor-4-b.json#D42030A#texts[1].text
  - RPGSystem/rpg-loc-quest-floor-b1-b.json#Q-1000#description
  - RPGSystem/rpg-loc-quest-floor-b1-b.json#Q-1010#description
  - RPGSystem/rpg-loc-quest-floor-4-b.json#Q4002#description
- 其余含"他/她"的Pwie相关条目核对后确认指代其他角色（堂吉诃德/默尔索/副主厨等），非误译，未改动。
- 已apply。以后翻译新的Pwie相关条目时，英文they/them/their指Pwie本人时一律用"祂"。
