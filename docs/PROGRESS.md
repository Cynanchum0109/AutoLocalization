# 当前进度

> 这是**当前状态**，每翻完一个文件就改写对应小节，不追加流水账（规矩见 `TRANSLATION_GUIDE.md`「进度记录」）。
> 2026-09-24 以前的完整记录在 `docs/archive/PROGRESS_archive.md`，只作历史参考。

更新：2026-10-28　·　术语表 2748 条

## 本轮范围

新人格：高级定制::红派 裁缝之王 希斯克利夫（10717）、高级定制::黑派 3F广播室 鸿璐（10617）。
`tools/scan.py` 2026-10-28 共 764 条 todo：

- StoryData：`P10617.json`（228）、`P10717.json`（142）
- PersonalityVoiceDlg：`Voice_Honglu_Contem_10617.json`、`Voice_Heathcliff_Contem_10717.json`（各 48）
- `_root`：`BattleSpeechBubbleDlg.json`（14）
- `_tailmech`：Skills_personality-06/07、Passives、Bufs、BattleKeywords、BuffAbilities
- `_tail`：Personalities、GachaTitle、Personality_Get_Condition、EventVerificationUIText、TutorialMirrorDungeon 等杂项

## 已完成

- `StoryData/P10617.json`（slot a，228 条，已 apply）。
  自拟：Golden Tape = 金色磁带（已记 `session_terms.json`）。沿用官方：Public Address Room 广播室、
  Le Noir Public Address Room 黑派广播室（title 字段）、Alterationist 改衣师、Brand Manager 品牌经理、
  old Voice 往昔之声；blanket 毯子（罩鸟笼的毯子，KR 담요，已记 `session_terms.json`）；
  52/56/58 的 order 是生意上的「订单」（KR 발주）；广播句照官方「渴求吧。如这份渴求般，分毫不留地摄取吧。」「汝愈将成为汝」。
- `StoryData/P10717.json`（slot a，142 条，已 apply）。希斯克利夫=B2F 裁缝之王，小人儿称他「王」；
  selvedge 布边、seam allowance 缝份、top-grain 头层修面皮；pillock 蠢货。
- `PersonalityVoiceDlg/Voice_Honglu_Contem_10617.json`、`Voice_Heathcliff_Contem_10717.json`（各 48 条，已 apply）。
  desc 按官方语音文件惯例（人格出战 / EX CLEAR战斗胜利…）；false god 伪神；Stitch per inch 每英寸针数。

- `BattleSpeechBubbleDlg.json`（14）、`_tailmech` 全部（Skills_personality-06/07、Passives、Bufs、BattleKeywords、BuffAbilities）。
  技能/被动名按 KR 原文对官方敌方版（`Skills_Abnormality-a1c10p1`、`Passives_Abnormality-a1c10p1/p2`、`Bufs-a1c10p1`）：
  经纱要如何，纬纱就这样；你说我故意把挑针缝得很显眼？！那就给你也缝成一样的！；咕啊……（으드득，照官方希斯用法）；
  手工缝制？给我手工缝制！！！；仿佛仍能听见的投诉；请侧耳倾听。官方没有的按 KR 拟：倾听时间、朗读准备（官方 낭독자=朗读者）、
  倾听刑罚、黑派 精纺面料大衣。Buf 描述照官方用显示名+空格（「流血 」）。
- 以上全部已 `tools/apply.py --install` 装进游戏（用户要求直接装）。

## 进行中

无。剩余 70 条 `_tail` 杂项（Personalities 人格名、GachaTitle、Personality_Get_Condition、EventVerificationUIText、TutorialMirrorDungeon 等）。

## 待用户确认

无。（`glossary/glossary.json` 按用户决定继续不入 git，靠 `glossary/glossary.json.bak-*` 备份。）
