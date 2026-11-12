# 翻译工作说明（唯一真本）

> 这份文件是给**所有** agent 看的：Claude Code 从 `CLAUDE.md` 进来，
> 其他 AI 从 `AGENTS.md` 进来，两边都只是指到这里。改规则只改这一份。

这个仓库的翻译**由你在会话里做**，不调翻译 API。你的角色是译者，脚本是你的取料/校验/出货工具。

## 游戏/汉化更新后

官方汉化包更新会盖掉我们译过的条目。装完官方包后清空工作区重来：
删掉整个 `out/` 和 `Workplace/translated`、`Workplace/backups/`，以及 `Installer/LLC_zh-CN/` 里的全部文件，
保留 `glossary/`、本文件、`CHARACTER_VOICE.md`、`FORMAT_TAGS.md` 和全部脚本；
`PROGRESS.md` 按下文「进度记录」的规矩重写成新一轮的状态。
然后按下面的流程从 `tools/scan.py` 重新开始（`tm.json` 会自动按新官方包重建）。

## 多 agent 并行（按文件分工）

**一个文件整份包给一个 agent，从头翻到尾。**同一段对话被两个人各翻一半，
称谓、语气、代词指代必然对不上——这是按文件分而不按条目分的唯一理由。

**只有两个 agent，slot 固定：Claude Code = `a`，Codex = `b`。**（环境变量 `LIMBUS_SLOT`，默认 `a`；
只认这两个字母，写别的脚本直接报错。）不管中断重开多少次，都用自己固定的字母。

```bash
python tools/batch_next.py --size 60                   # Claude Code（默认就是 a）
LIMBUS_SLOT=b python tools/batch_next.py --size 60     # Codex：每条命令都要带 LIMBUS_SLOT=b
LIMBUS_SLOT=b python tools/batch_next.py --file rpg-loc-dialogue-floor-3.json   # 也可以点名
```

- 批次文件在 `out/slots/<slot>/`，互不覆盖。
- `batch_next` 不给 `--file` 时：先接着翻自己没翻完的文件，没有了再挑待译最多的无主文件。
  **同一个文件会一直发给你，直到翻完**，所以上下文是连续的。
- 认领记在 `out/claims.json`（文件级，**不过期**）：文件一直归认领的 agent，翻完 `batch_merge` 自动交还。
- **中断后重开**：自己还有没合批的批次时，`batch_next` 不取新批，只提示你接着把
  `batch_pending.json` 翻完（`batch_answers.json` 里已填的都还在）。
- 不想做了：`tools/batch_next.py --abandon`，释放认领，没合批的批次改名 `*.abandoned` 留档。
- 只有用户明确说「接手另一个 agent 的活」时，才用 `tools/batch_next.py --adopt <另一个字母>`，
  把对方没合批的批次和已填答案搬过来。
- `progress.json` 的读-改-写加了跨进程锁，两边同时合批不会丢译文。
- **`tools/scan.py --accept` 和 `tools/apply.py --install` 只由一个 agent 跑。**

### 跨 agent 的一致性

分了文件，专名还是会分叉（A 的 floor-1 和 B 的 floor-3 都出现 `Golden Skein`）。
三层兜着：

1. `glossary/glossary.json` —— 已定名的术语，两边都读。**`!` 前缀是大小写敏感专名。**
2. `ours` 字段 —— 这个专名我们（含**另一个 agent 手上还没合批的批次**）译过什么，
   带例句。标了 `[另一 agent 刚定]` 的是对方刚做的决定，**直接跟**。
3. `glossary/session_terms.json` —— 本轮新造译名的共享台账。
   **术语表里没有、你自己拍板的专名，当场记进去**，另一个 agent 的下一批就会在
   `agreed_terms` 字段里看到并照用：

   ```bash
   python -c "from limbus.ourterms import record; record('Golden Skein','黄金线团','b2 层材料')"
   ```

拿不准某个词有没有定名、在别处怎么出现，用 `tools/term.py` 查（中英互查，也查上面第 3 层的台账）：

```bash
python tools/term.py Golden               # 译名 + 所属章 + 类型 + 出现在哪些章节
python tools/term.py --chap 10            # 第10章的术语，按类型分组（8.5 = 间章8.5）
python tools/term.py --chap 10 --cat 组织
```

所属章和类型只是查找用的标签，不影响 `glossary` 字段的匹配。改了 `glossary.json` 之后跑一次
`python tools/glossary/categorize.py` 刷新（约 1 分钟）。

术语表默认**不分大小写**匹配，常见词会误命中（rain → 雷恩）。加新词或官方更新后复查：
`python tools/glossary/case_audit.py` 按官方译文给出 敏感/删/留/改译名 建议（输出 `case_audit.tsv`）；
一词多义的用 `python tools/glossary/usage_report.py 词1 词2` 看官方用法分布，在值里写明「仅…时；其他按语境」。

**人格剧情归章**：2026-10-05 起新增的人格剧情（`StoryData/P*.json`，不含联动 `PC*`）都属第10章（N公司/西西弗百货），
从中提取的名词也归第10章。判定靠 `glossary/p_story_baseline.json`：表里是旧文件，不归章；
不在表里的自动算「第10章·人格剧情」。**不要往基线里加新文件。**

## 每次开工

```bash
python tools/scan.py            # 看 out/changes/<最新>.md 和 out/state.json
python tools/batch_next.py --size 60
```

**兜底扫描（tail）**：`tools/scan.py` 除了 `tools/config.py` 里点名的 tier0 范围，还会递归扫描 EN 目录里**其余所有文件**，
scope 记作 `_tail`（机制类文件名如 Skills/Passive/Bufs/BattleKeywords 记作 `_tailmech`，方括号关键词保留英文）。
这些按「条目」判断，只翻官方中文端缺的条目。`batch_next` 排序时 **tail 永远排在最后**——tier0 翻完才轮到它们。
**收工前必须看 `tools/scan.py` 输出的 todo 里有没有 `_tail`/`_tailmech`**，别把「tier0 待办 0」当成「全部翻完」。

**只翻「中文没有、英文有」的部分**，这条由 `tools/scan.py` 判定，队列里只会出现 `todo`：
- `StoryData/`、`PersonalityVoiceDlg/`：**按文件**。中文侧没有这个文件才翻；文件已存在，
  哪怕里面有英文没翻的条目，也整份不翻。
- 其余目录：**按 JSON 条目**。中文侧没有这个条目才翻；条目已存在就不翻，哪怕内容是英文或占位符。
  例外：条目里有我们译过的字段时，同条目其余与英文相同的字段算 `todo`（游戏里装的是我们的包，那是漏翻）。
- 我们译过的条目，之后英文原文改了也**不重翻**。
不要手动去翻 `same_as_en` / `zh_placeholder` / `has_zh` 这些统计状态里的条目。

读 `out/slots/<slot>/batch_pending.json`（默认 slot 是 `a`），给每条填 `translation`，
写成同目录的 `batch_answers.json`
（只需 `key` + `translation` 两个字段），然后：

```bash
python tools/batch_merge.py     # 校验不过会整批拒绝，按提示改 answers 重跑
```

**每翻完一个文件就 `python tools/apply.py`**，不要攒批。然后 `python tools/scan.py` 刷新 `out/state.json`
（不刷新 `batch_next` 会重复吐旧批次）；需要推进基线时再 `python tools/scan.py --accept`。
用户要求流程从简：**不跑 `tools/check.py` / `tools/consistency.py`**，只靠 `tools/batch_merge.py` 的硬拦截，
除非用户点名要查。
`tools/apply.py` 默认输出「中文 + 换行 + 英文」双语；技能/被动/Buff/关键词和 `_tail` 杂项（人格名、抽卡标题等）只放中文，名单在 `config.MONOLINGUAL_SCOPES`；
例外是 `_tail` 里的台词目录 `BattleAnnouncerDlg/`、`EGOVoiceDig/`（播报员、E.G.O 语音），照样双语，名单在 `config.BILINGUAL_SUBDIRS`。
默认**不带 `--install`**：产物只落在 `Workplace/translated/`，装不装由用户决定
（`--install` 会直接拷进游戏 LLC_zh-CN，覆盖前自动备份到 `Workplace/backups/<时间>/`）。

批次里的 `official_zh` 字段是**翻译记忆库命中**：官方在别处译过这句一模一样的原文，
直接照抄保持一致；标了「多种译法」的要按本处语境判断该用哪个。

**一致性字段**（专名前后不一致是最常见的错，这三样就是治它的）：
- `ours`：句中的专名短语（Golden Skein / Prestige Tier / 人名…）我们在别处已经译过，附前译例句。
  **沿用同一译法**，除非前译明显错。
- `pending_terms`：命中 `glossary/pending_terms.json` 里的待定词（译名还没拍板）。先沿用现译写法。
- merge 时术语表命中词在译文里找不到对应译名会打软警告（`Fixer→收尾人`），看到就回头改。

## 进度记录

`PROGRESS.md` 是**当前状态**，不是日志，接手的人只看它就能开工。每翻完一个文件就更新：
**改写**对应小节（本轮范围 / 已完成 / 进行中 / 待用户确认），不要在末尾追加「续N」流水账。
规则变了就改 `TRANSLATION_GUIDE.md` 本身，不写进 PROGRESS。
旧记录在 `docs/archive/PROGRESS_archive.md`，只作历史参考，不要按它干活。

## 翻译规则

1. **格式标签**：完整清单见 `FORMAT_TAGS.md`，开工前读一遍（角色语气见 `CHARACTER_VOICE.md`，也读）。要点：
   - **强标记必须一一对应**：`<color=…></color>` `<style=…>` `<mark=…>` `<noparse>`、
     `{0}` `{targets}` 等占位符、`#&#(!@&$` 乱码序列。数量不符 `tools/batch_merge.py` 整批拒绝。
   - **排版标签原样照抄，不丢也不加**：`<i> <b> <u> <s> <size> <ruby> <voffset> <link> <font>`。
     官方中文常把 `<i>` 丢掉，**我们不学**。丢一个、或自己多加一个，都是硬错误整批拒绝。
     唯一放行的新增是良秀注音 `<ruby=Yoshihide>良秀</ruby>`。
   - **`<尖括号>` 和 `[方括号]` 通常不是标签，是引号**：`<Uh...>` 是心声、
     `[INITIATING SITE BURIAL.]` 是广播、`[Activating]` 是音效标注。
     **里面的话要翻译，括号本身保留。** batch 里会用 `quote_brackets` 字段点名提醒。
   - `keep_verbatim` 字段列出的才是真要原样抄的东西。
2. **换行**：原文的 `\n` 是刻意排版，默认保留。合并两行只在中文明显更顺时做（会有警告，不拦）。
   绝不能输出字面 `\n` 两个字符，游戏不认。
3. **语体**：当代自然简体中文，第一人称用「我」。除非原文本身是仿古腔（thee/thou/圣经体），
   否则不许用文言。夸张中二的台词用有张力的现代汉语表现，不要文言化。
4. **忠实**：不增不减。`grudge` 就是「怨恨」，不要扩写成「复仇决意」。
5. **地道**：按中文习惯重组语序，不逐词硬对。`suffering itself` → 「苦难本身」，
   不是「饱受折磨的本身」。
6. **术语**：`glossary` 字段给出命中的术语表条目（键带 `!` 前缀的是大小写敏感专名，如 `!Ticket` 券券、`!Soda` 美味苏打；小写形式是普通词，按语境译）。**专有名词（人名/地名/组织）必须采用**；
   但若该词在本句里只是普通词义（`Grudge` 就是「怨恨」），
   按普通词自然翻译，不要生搬术语。
7. **单数 they**：先按指代对象判断单复数，不看词形——前文只有一个人/物、出现 `themself`、
   或上下文里只有它一个，就是单数；真指多个人才译「他们」。单数时：
   - 吱咿（Pwie）→「它」；红派的 Crimson God / the Voice / New Voice 指那个存在时 →「那位」
     （照官方 2026-09-28 汉化；官方不用「祂」，我们也不用）。
   - 其他性别不明的单一个体（但丁、快乐衣橱……）→ 旁白、转述、报告体用「其」
     （官方用法：「其的话」「引起了其注意」）；对话里或拿不准时**直接用名字**（「但丁说……」）。
   - 新出现的性别不明角色默认同上；若是神格级存在，先查官方怎么称呼，拿不准问用户。
     定下来后加进 `tools/config.py` 的 `SINGULAR_THEY`，批次里就会自动出现 `they_note` 提醒。
   - 同句里 he/she/they 指别的角色时照常译。
   **角色语气**：各罪人的称呼体系和语气（谁用「您」、谁自称「吾」、罗佳的昵称表…）见 `CHARACTER_VOICE.md`，
   翻台词前按 `speaker` 查。**但一切以英文原文为准**：风格表只决定原文里已有的称呼/语气词用哪个中文，
   不许因为「这角色通常这样说话」而增删原文没有/有的内容。
8. **上下文**：`prev` / `next` 是同文件相邻台词（优先显示官方中文），
   用来对齐称谓、语气、代词指代。`speaker` 是说话人。
9. **只输出译文正文**：不加注音、ruby、括号解释、译注、引号前后缀。
10. **引号**：英文双引号 `"…"` 照译成中文双引号，**不要**换成『』或「」。
   （都市 / 妈妈等专名的固定译法在术语表里，批次 `glossary` 字段会带出来。）
11. **不要在正文里加说话人前缀**：StoryData 的 `teller`、RPG 对话的 `speaker` 是独立字段，
   UI 自己会显示名字。`content`/`text` 里只写台词本身，写成「杜布瓦：……」会显示成两遍名字。

## 机制文本句式

翻 Skills/Passives/Bufs/BattleKeywords 时按官方既有句式，没把握就先看批次里的 `official_zh`，
或去上一赛季同类官方文件（如 `Skills_Enemy-a1c9p1.json`）里搜同一句原文照抄，不要凭感觉造句。

- SP→理智值，Final Power→最终威力，Coin Power→硬币威力，Base Power→基础威力
- 强度型 `Inflict N [X]` →「使目标增加N级[X]强度」；层数型 `Inflict +N [X] Count` →「对目标施加N层[X]」
- `If target has N+ [X], Final Power +Y` →「若目标的[X]强度不低于N级，则使本技能的最终威力+Y」
  （带 Count 的走「[X]层数不低于N层」）
- `Final Power +1 for every N [X] on target (max M)` →「目标每带有N级[X]强度，使本技能的最终威力+1(最多+M)」
- `Heal N SP` →「使自身恢复N点理智值」；`Deal +30% damage on Critical Hit` →「使本硬币暴击时造成的伤害+30%」
- `convert all Coins to [SuperCoin]s` →「使本技能的所有硬币转化为[SuperCoin]」
- `desc`/`summary`/`flavor` 里的 `[Xxx]`（含 `[StartBattle]` `[WhenUse]` `[OnSucceedAttack]` 等触发词）
  是关键词 ID，**保留英文**；`name` 字段里的方括号是名字的一部分，要翻（`Shade of Reflection [Rouge]`→`映射[红色]`）
- `[Xxx]` 是关键词 **ID**，不等于显示名（`Burst` 显示 Rupture、`Laceration` 显示 Bleed、`Breath` 显示 Poise）。
  要知道某个 ID 在中文里叫什么，查 EN `EN_BattleKeywords.json` 与 `LLC_zh-CN/BattleKeywords.json` 同 id 的 name。

## 边界

- `out/progress.json` 是译文库，只能通过 `tools/batch_merge.py` 和 `tools/apply.py`（收用户手改）写，不要手改。
- `out/ignore.json` 里的条目是约定好永久不翻的，不要主动去翻。
- `tools/apply.py` 默认只输出到 `Workplace/translated/`；`--install` 才会写游戏目录，
  且覆盖前会把原文件备份到 `Workplace/backups/<时间>/`。
- **用户会直接在 `Workplace/translated/` 里改文案**（agent 自己不改，改译文只走 `progress.json`）。
  `tools/apply.py` 每次写出前先把用户手改收回 `progress.json`（标 `by: "user"`），再重新生成，所以不会覆盖；
  同一条用户和 agent 都改了，以用户为准，脚本会打印「冲突」两版对照。
  手改过的文件覆盖前整份备份到 `Workplace/backups/<时间>-手改/`。
- **用户让你统一改译文时，动手前先跑 `python tools/apply.py --import-only`**，
  在 `progress.json` 里用户版的基础上改（`by: "user"` 的条目是用户亲手定的，没让改就别动）。
- 已知坑：合批后 apply 偶尔报「写出 0 个文件」，这时用 `tools/apply.py --force` 重写（手改照样先收回）。

## 发布

发布的 zip 是**玩家安装包**：`install.bat`、`install.ps1`、`README.txt`、`LLC_zh-CN/` 四项
（`install.ps1` 靠同级的 `LLC_zh-CN/` 工作，缺了装不上）。**只用脚本打，不要手动压缩：**

```bash
python tools/apply.py
python tools/pack.py <线上同名附件>.zip    # 例：Canto10.2.TheGazeBearing_byBQCynanchum.zip
```

`tools/pack.py` 会用 `Workplace/translated` 重建 `Installer/LLC_zh-CN`（不会混进旧章节），
在 `release/` 生成 zip 并校验结构，不对就报错不出包。上传要**先问用户**，再执行它最后打印的
`gh release upload ... --clobber`（同名附件原地替换，release 页只留一个包）。
正式仓库是 `Cynanchum0109/LimbusCompanyTempLoc`，不是代码仓库。
