# 翻译工作说明（唯一真本）

> 这份文件是给**所有** agent 看的：Claude Code 从 `CLAUDE.md` 进来，
> 其他 AI 从 `AGENTS.md` 进来，两边都只是指到这里。改规则只改这一份。

这个仓库的翻译**由你在会话里做**，不调翻译 API。你的角色是译者，脚本是你的取料/校验/出货工具。

## 游戏/汉化更新后

官方汉化包更新会盖掉我们译过的条目。装完官方包后清空工作区重来：
删掉整个 `out/` 和 `Workplace/translated`、`Workplace/backup_*`，
保留 `glossary/`、本文件、`CHARACTER_VOICE.md`、`FORMAT_TAGS.md`、`PROGRESS.md` 和全部脚本。
然后按下面的流程从 `scan.py` 重新开始（`tm.json` 会自动按新官方包重建）。

## 多 agent 并行（按文件分工）

**一个文件整份包给一个 agent，从头翻到尾。**同一段对话被两个人各翻一半，
称谓、语气、代词指代必然对不上——这是按文件分而不按条目分的唯一理由。

每个 agent 设一个 slot（环境变量 `LIMBUS_SLOT`，默认 `a`）：

```bash
LIMBUS_SLOT=a python batch_next.py --size 60     # agent A：自动包一个没人要的文件
LIMBUS_SLOT=b python batch_next.py --size 60     # agent B：自动避开 A 的文件
LIMBUS_SLOT=b python batch_next.py --file rpg-loc-dialogue-floor-3.json   # 也可以点名
```

- 批次文件在 `out/slots/<slot>/`，互不覆盖。
- `batch_next` 不给 `--file` 时：先接着翻自己没翻完的文件，没有了再挑待译最多的无主文件。
  **同一个文件会一直发给你，直到翻完**，所以上下文是连续的。
- 认领记在 `out/claims.json`（文件级，租约 4 小时，每次取批/合批自动续租）。
  文件翻完 `batch_merge` 自动交还。中途不干了：`python batch_next.py --abandon`。
- `progress.json` 的读-改-写加了跨进程锁，两边同时合批不会丢译文。
- **`scan.py --accept` 和 `apply.py --install` 只由一个 agent 跑。**

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

翻完一个文件跑 `python consistency.py --file <文件名>` 自查分叉。

## 每次开工

```bash
python scan.py            # 看 out/changes/<最新>.md 和 out/state.json
python batch_next.py --size 60
```

读 `out/slots/<slot>/batch_pending.json`（默认 slot 是 `a`），给每条填 `translation`，
写成同目录的 `batch_answers.json`
（只需 `key` + `translation` 两个字段），然后：

```bash
python batch_merge.py     # 校验不过会整批拒绝，按提示改 answers 重跑
```

批次清空后按这个顺序：`python apply.py` 出产物 → `python check.py` 体检
→ 通过了再 `python scan.py --accept` 推进基线。
**先检查再交付，不要先装进游戏再检查。**
默认**不带 `--install`**：产物只落在 `Workplace/translated/`，装不装由用户决定
（`--install` 会直接拷进游戏 LLC_zh-CN，覆盖前自动备份到 `Workplace/backup_<时间>/`）。
`--accept` 时若还剩 `outdated_official` 会被拒绝——先翻掉，或确认不跟进后加 `--force`。

批次里的 `official_zh` 字段是**翻译记忆库命中**：官方在别处译过这句一模一样的原文，
直接照抄保持一致；标了「多种译法」的要按本处语境判断该用哪个。

**一致性字段**（专名前后不一致是最常见的错，这三样就是治它的）：
- `ours`：句中的专名短语（Golden Skein / Prestige Tier / 人名…）我们在别处已经译过，附前译例句。
  **沿用同一译法**，除非前译明显错。
- `pending_terms`：命中 `glossary/pending_terms.json` 里的待定词（译名还没拍板）。先沿用现译写法。
- merge 时术语表命中词在译文里找不到对应译名会打软警告（`Fixer→收尾人`），看到就回头改。

每译完一个文件跑 `python consistency.py`，看 `out/consistency.md` 有没有新分裂。

## 翻译规则

1. **格式标签**：完整清单见 `FORMAT_TAGS.md`，开工前读一遍（角色语气见 `CHARACTER_VOICE.md`，也读）。要点：
   - **强标记必须一一对应**：`<color=…></color>` `<style=…>` `<mark=…>` `<noparse>`、
     `{0}` `{targets}` 等占位符、`#&#(!@&$` 乱码序列。数量不符 `batch_merge.py` 整批拒绝。
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
   但若该词在本句里只是普通词义（`Stranger` 就是「陌生人」，`Grudge` 就是「怨恨」），
   按普通词自然翻译，不要生搬术语。
7. **单数 they / 角色语气**：但丁性别不明——日常对话用能代表两性的「他」，严肃转述、旁白、报告体用
   「其」（官方用法：「其的话」「引起了其注意」）；**绝不能译「他们」**，只有真复数才是「他们」。
   各罪人的称呼体系和语气（谁用「您」、谁自称「吾」、罗佳的昵称表…）见 `CHARACTER_VOICE.md`，
   翻台词前按 `speaker` 查。**但一切以英文原文为准**：风格表只决定原文里已有的称呼/语气词用哪个中文，
   不许因为「这角色通常这样说话」而增删原文没有/有的内容。
8. **上下文**：`prev` / `next` 是同文件相邻台词（优先显示官方中文），
   用来对齐称谓、语气、代词指代。`speaker` 是说话人。
9. **只输出译文正文**：不加注音、ruby、括号解释、译注、引号前后缀。
10. `previous_zh` 字段（status 为 `stale` / `outdated_official` 时出现）是旧译文，
   官方改了英文原文才让它重进队列 —— 参考旧译保持风格，但按新原文翻。

## 边界

- `out/progress.json` 是译文库，只能通过 `batch_merge.py` 写，不要手改。
- `out/ignore.json` 里的条目是约定好永久不翻的，不要主动去翻。
- `apply.py` 默认只输出到 `Workplace/translated/`；`--install` 才会写游戏目录，
  且覆盖前会把原文件备份到 `Workplace/backup_<时间>/`。
- 机制文本（`_mech`）里 `desc`/`summary`/`flavor` 的 `[Xxx]` 是关键词 ID，**保留英文**；
  `name` 字段里的方括号是名字，要翻。
