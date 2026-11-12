# 当前进度

> 这是**当前状态**，每翻完一个文件就改写对应小节，不追加流水账（规矩见 `TRANSLATION_GUIDE.md`「进度记录」）。
> 2026-09-24 以前的完整记录在 `docs/archive/PROGRESS_archive.md`，只作历史参考。

更新：2026-11-11

## 本轮范围

新人格：楔子事务所收尾人 堂吉诃德（10316）、辛克莱（11017）、奥提斯（11116）；另有 E100X~E103X 剧情、walpu10 活动。
本轮开工时 `tools/scan.py` 共 1942 条 todo：

- StoryData：`P10316.json`（155）、`P11017.json`（155）、`P11116.json`（45）、`E100X.json`（135）、`E101X.json`（40）、`E102X.json`（12）、`E103X.json`（18）
- PersonalityVoiceDlg：`Voice_DonQuixote_Wedge_10316.json`、`Voice_Sinclair_Wedge_11017.json`、`Voice_Outis_Wedge_11116.json`（各 48）
- `_root`：`BattleSpeechBubbleDlg.json`（35）、`BattleSpeechBubbleDlg-walpu10.json`（56）、`ScenarioModelCodes-AutoCreated.json`（16）
- `_tailmech`：Skills_personality-03/10/11、Skills_Abnormality-walpu10、Passives、Bufs、BattleKeywords（含 walpu10）等
- `_tail`：Walpu10EventText、ActionEvents/AbEvents/EGOgift-walpu10、Announcer、Personalities 等杂项

## 已完成

- `StoryData/P10316.json`（slot a，155 条，已 apply）。
  自拟：Wedge Office = 楔子事务所（KR 쐐기 사무소，已记 `session_terms.json`），Fixer/Rep = 楔子事务所收尾人/代表。
  这个人格的辛克莱对堂吉诃德不用敬语、很冲；堂吉诃德仿古腔用吾/汝，称「小辛克莱」。
  结尾照官方 P11213：「正于此地，愿您找到想要的书。」；Invitation 邀请函、Library 图书馆。
- `StoryData/P11017.json`（slot a，155 条，已 apply）。原文与 P10316 逐条相同，直接沿用同一套译文。
- `StoryData/E100X.json`（slot a，135 条，已 apply）。浮士德对但丁用「您」、自称「浮士德」。
  沿用官方：Patron Librarian 指定司书、Floor of History 历史层、Reception 接待（KR 접대）、Gesellschaft / Malkuth 保留英文、
  Impuritas Civitatis =「杂质」（KR 불순물，照官方 PC13B）、the former L Corp. 旧L公司、Zwei协会、烙印工坊、美食广场；
  黎明事务所成员：尤娜、菲利普（称萨尔瓦多「师父」，KR 스승님 / JP 師匠；称尤娜「前辈」）、Salvador 萨尔瓦多（自拟）；
  用户指定 Oscar 奥斯卡、Pameli 帕梅莉、Pamela 帕梅菈。以上都已记 `session_terms.json`。
- `StoryData/P11116.json`（slot a，45 条，已 apply）。奥提斯=楔子事务所代表，报告体。
  自拟：8 o'clock Circus = 8点档马戏团、ringmaster 团长、troupe members 团员（KR 8시 서커스 / 단장，已记台账）；
  Hana Association 照官方写「하나协会」；ssanghwa-cha 双和茶（官方）。
- `StoryData/E101X.json`（40）、`E102X.json`（12）、`E103X.json`（18）（slot a，已 apply）。
  Effloresce/Efflorescence = 绽放（官方）；Bus's Backdoor 巴士的后门；C.H. 钟·头。
- **StoryData 全部完成。**
- `PersonalityVoiceDlg/Voice_DonQuixote_Wedge_10316.json`、`Voice_Sinclair_Wedge_11017.json`、`Voice_Outis_Wedge_11116.json`（各 48，slot a，已 apply）。
  desc 照官方语音文件惯例。堂吉诃德与辛克莱两份大部分是同一组对话、只是互换上色方，译文共用。
  午间问候是食物词尾接龙：用户定为菜名直译、括号附英文原词（`<i>` 标在括号里的词尾），如「糖醋肉（Tangsu<i>yuk</i>）」；
  接龙引子（Re……/Tang……/O……）和「Ble？Bro？」保留英文。
- announcer：`BattleAnnouncerDlg/Announcer_Hokma_59.json`（32）、`Announcer_Walpu10_90008.json`（6，Malkuth）、
  `Announcer.json`（Hokma，照官方 Sephirah 名留英文）、`Announcer-walpu10.json`（指定司书Malkuth[历史层]）（slot a，已 apply）。
  用户手改定了：prudent = 谨慎、deterrence = 抑制。
- `_root`：`ScenarioModelCodes-AutoCreated`（16）、`BattleSpeechBubbleDlg`（35）、`BattleSpeechBubbleDlg-walpu10`（56）（slot a，已 apply）。
- `_tail` 全部（slot a，已 apply）：Walpu10EventText、AbEvents/ActionEvents/EGOgift-walpu10、Egos、Personalities 等杂项。
  沿用官方：The Sword Sharpened with Tears = 泪锋之剑、Knight of Despair = 绝望骑士、blessing = 加护、Hollow Pride = 空洞的自尊；
  Sword Laced with Grief = 浸透悲伤之剑（自拟，与泪锋之剑是两件饰品）。
- `_tailmech` 全部（slot a，已 apply）：BattleKeywords/Bufs（含 walpu10）、Passives、Passive_Ego、Passives_Abnormality-walpu10、
  Skills_personality-03/10/11、Skills_Abnormality-walpu10、Skills_Ego_Personality-06、Enemies-walpu10、SkillTag、UnitKeyword。
  机制句式照官方技能文本；`[Keyword]` ID 一律留英文。官方已有的照抄：黎明之火 / 炎蝶之棺 flavor、晨炎 / 炎蝶[烙印工坊]、
  烙印工造、激情、不稳定的自我外壳、黎明将至、正午的解体、联合（Seconded Offensive）、黎明闪光。
  Blazing Strike 改用官方技能名「爆炎一击」（原「炽烈打击」已全部替换）。新造名都已记 `session_terms.json`。

## 进行中

无。`tools/scan.py` 2026-11-11：todo 0，ours 1942。产物已 apply 到 `Workplace/translated/`，未 install。

## 待用户确认

- （`glossary/glossary.json` 按用户决定继续不入 git，靠 `glossary/glossary.json.bak-*` 备份。）
