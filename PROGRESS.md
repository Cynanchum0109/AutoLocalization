# 当前进度

> 这是**当前状态**，每翻完一个文件就改写对应小节，不追加流水账（规矩见 `TRANSLATION_GUIDE.md`「进度记录」）。
> 2026-09-24 以前的完整记录在 `PROGRESS_archive.md`，只作历史参考。

更新：2026-10-06　·　术语表 2748 条

## 本轮范围

**无。**第十章（下）a1c10p3 一轮已结束：2026-10-05 官方汉化更新已覆盖本轮范围，我们的译文不再安装。
等下次游戏/官方汉化更新后，按 `TRANSLATION_GUIDE.md`「游戏/汉化更新后」从 `scan.py` 重新开始。

## 2026-10-05 对照官方后的术语表改动

- `session_terms.json` / `pending_terms.json` 里官方已定名的 30 条已按官方写进 `glossary.json`
  （如 The Sedimented 堆积之物、Thumping Pulse 搏动、Compunction 罪恶感、Hammernail [Judgment] 锤之钉[审判]、
  Fresh Meat Section 新鲜精肉区、Ionesco 尤内斯库）。`session_terms.json` 只剩官方仍未出现的 7 个自拟词，`pending_terms.json` 已清空。
- 新出现的官方定名：Instructor 教官、Tannery 鞣制室、Le Rouge Staff 红派 工作人员、Le Noir Officer 黑派的干部、
  Lost Child Center 走失儿童保护所、Owner's Momma 老板的妈妈、A Certain Castle 某城堡、Inquisitor 审判官。Maman 保留「妈妈」。
- 常见词清理：76 个按语境翻的常见词已删（含保护区的 Sister/Father/Clan/Jar/Host/Assistant/Thief），Student/Flesh/Fear 也已删；
  专名兼常见词改成 `!` 大小写敏感，一词多义的在值里写明用法（参考 `!Rain`、`!Mentor`、`!Wings`=翼、`!Boss`）；Child 固定「孩子」。
  复查工具：`glossary/case_audit.py`（大小写审计）、`glossary/usage_report.py`（单词的官方用法分布）。
- 人格剧情归章规则已写进 `TRANSLATION_GUIDE.md`（基线 `glossary/p_story_baseline.json`）。

## 进行中

无。

## 待用户确认

无。（`glossary/glossary.json` 按用户决定继续不入 git，靠 `glossary/glossary.json.bak-*` 备份。）
