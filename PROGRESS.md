# 当前进度

> 这是**当前状态**，每翻完一个文件就改写对应小节，不追加流水账（规矩见 `TRANSLATION_GUIDE.md`「进度记录」）。
> 2026-09-24 以前的完整记录在 `PROGRESS_archive.md`，只作历史参考。

更新：2026-09-24　·　译文库 `out/progress.json` 10289 条　·　`out/claims.json` 无人占用

## 本轮范围：第十章（中）a1c10p2

官方汉化 2026-09-20 更新后空库重开。**只翻下面这些**，其余 StoryData 老章节（S0xx/S2xx/S3xx/S7xx/S8xx、
3D/7D/旧 E/P 系列、第十章（上）的 a1c10p1/S1000–S1016B）不属于本轮，不要认领。
判断新文件是否属于本轮：看剧情是否和下面已完成的章节连续，不能只看编号（S1027–S1029B 曾被误当老章节跳过）。

- 机制：`BattleKeywords` `BattleSpeechBubbleDlg` `Bufs` `Enemies` `PanicInfo` `Passives_Abnormality`
  `Passives_Assist` `Skills_Abnormality` `Skills_Assist`（均为 `-a1c10p2`）
- 剧情：StoryData `S1017B`–`S1029B`、`S9992B`、`P10705`、`P10917`
- 语音：`PersonalityVoiceDlg/Voice_Rodion_Contem_10917`（罗佳 改衣师人格）
- RPG：`RPGSystem/` 下 a1c10p2 相关文件（各楼层 `-b`、`-a` 杂兵、common-a1c10p2、route-a/b 等），共 69 个
- 名表：`ScenarioModelCodes-AutoCreated`

## 已完成

上面范围**全部翻完并 apply**，`Workplace/translated` 共 96 个文件。
2026-09-24 已发布：release `Canto10(2)TheGazeBearing`（仓库 `Cynanchum0109/LimbusCompanyTempLoc`），
附件 `Canto10.2.TheGazeBearing_byBQCynanchum.zip`（玩家安装包，用 `pack.py` 同结构打）。

本轮收尾时做过的全库订正（后续新译照此执行，规则已写进 `TRANSLATION_GUIDE.md`）：
- 布布/布菲/红派的"声音"及快乐衣橱：they/them 指本体时改「祂」
- 去掉 `P10917`、`rpg-loc-dialogue-floor-4` 正文里多加的说话人前缀
- Stranger→「异乡人」（原误作「陌生人」20处），Alterationist→「改衣师」（原误作「改造师」2处）

## 进行中

无。

## 待用户确认

- `E003I3`、`S308B`、`E406B`：09-23 的任务顺序里列在 S1029B 之后，但后来按"S03 这类不是本次更新"跳过了，没翻。要不要翻？
- `glossary/pending_terms.json` 里的待定译名（RPG 人名、Kaki、Golden 材料前缀、Prestige Tier、Fount）还没拍板。
- `glossary/glossary.json` 不在 git 里（`.gitignore` 排除），丢了无法恢复，要不要纳入版本管理或另行备份。
