     1|---
     2|name: markdown-cli-table-rendering
     3|description: >-
     4|  Render Markdown pipe tables as aligned CLI box tables with correct terminal display width for Chinese text, emoji, numeric alignment, and wrapped long cells. Use when the user asks to display/preview Markdown tables in Hermes CLI, complains that Markdown tables are misaligned, or asks for boxed/visualized terminal table output. Trigger phrases include markdown表格对齐, CLI表格显示, 大表格显示效果, emoji表格对齐, 长文字表格换行, box table, terminal table rendering.
     5|version: 1.0.0
     6|---
     7|
     8|# Markdown CLI 表格渲染
     9|
    10|## 目的
    11|
    12|当用户要求“测试/展示 Markdown 表格显示效果”时，不要只输出原始 Markdown pipe table，也不要建议改用 HTML。应把 Markdown 表格在 CLI 中**可视化渲染**为带框线、列宽稳定、内容对齐的终端表格。
    13|
    14|核心目标：
    15|- 中文、英文、数字混排时视觉对齐。
    16|- emoji / 变体选择符 / 零宽连接符不破坏列宽。
    17|- 长文字在单元格内自动换行。
    18|- 数字列右对齐，文本列左对齐或表头居中。
    19|- 输出适合终端阅读，而不是适合网页渲染。
    20|
    21|## 触发场景
    22|
    23|使用本 skill，当用户出现以下意图之一：
    24|1. “测试 markdown 大表格显示效果”。
    25|2. “表格没对齐 / 趋势和说明列没对齐”。
    26|3. “emoji 也应该对齐”。
    27|4. “长文字能对齐吗”。
    28|5. “CLI 里要展示成良好的可视化表格 / 要有框线”。
    29|6. 任何要求把 Markdown 表格预览成终端可读表格的任务。
    30|
    31|## 输出原则
    32|
    33|1. **直接给可视化表格**：优先输出 box drawing table，不要先解释一大段原因。
    34|2. **不要提 HTML 方案**：用户明确关注 CLI Markdown 可视化，不要把问题转移到网页/HTML。
    35|3. **不要把原始 Markdown 当最终展示**：Markdown pipe table 可以作为输入或附录，但 CLI 展示应渲染成框线表。
    36|4. **保留用户内容**：不要为了对齐删除 emoji、缩短中文或改写业务含义。
    37|5. **用显示宽度，不用字符串长度**：宽度计算必须按终端 cell width，而不是 `len()`、字符数或字节数。
    38|
    39|## 渲染工作流
    40|
    41|### Step 1：识别表格结构
    42|
    43|从 Markdown pipe table 中提取：
    44|- 表头行
    45|- 分隔行，例如 `|---|---:|:---:|`
    46|- 数据行
    47|- 每列对齐方式：
    48|  - `---`：默认文本左对齐
    49|  - `---:`：右对齐
    50|  - `:---:`：居中
    51|  - `:---`：左对齐
    52|
    53|如果用户只是要求“测试显示效果”，可以直接构造一个覆盖以下边界的测试表：
    54|- 中文列
    55|- 数字列
    56|- emoji 趋势列
    57|- 长说明列
    58|- 百分比、正负数、≤ 等符号
    59|
    60|### Step 2：计算终端显示宽度
    61|
    62|按 Unicode 显示宽度计算列宽：
    63|- East Asian Width 为 `W` 或 `F` 的字符按 2 列。
    64|- 普通 ASCII 按 1 列。
    65|- combining mark、变体选择符 `U+FE0E/U+FE0F`、零宽连接符 `U+200D` 按 0 列。
    66|- 常见 emoji 或 emoji+FE0F 序列按 2 列处理。
    67|
    68|不要用：
    69|- `len(text)`
    70|- UTF-8 字节长度
    71|- 简单中文字符数 × 2 的粗糙算法
    72|
    73|### Step 3：确定列宽
    74|
    75|推荐规则：
    76|1. 表头和短文本列：按内容最大显示宽度。
    77|2. 数字列：按内容最大显示宽度，右对齐。
    78|3. 长说明列：设置最大宽度，常用 32-48 cell；超过则换行。
    79|4. 总表宽不要明显超过终端宽度；如列很多，优先压缩长文本列。
    80|
    81|默认列宽建议：
    82|- 分类列：8-10
    83|- 名称列：12-16
    84|- 数字列：6-10
    85|- 趋势列：8-10
    86|- 说明列：32-48
    87|
    88|### Step 4：单元格换行
    89|
    90|对每个单元格按显示宽度 wrap：
    91|- 不能在 emoji 变体选择符中间切断。
    92|- 中文可逐字换行。
    93|- 英文长单词如果超过列宽，可硬切。
    94|- 一个数据行内，如果某个单元格换成 N 行，其他列要补空白行，保证竖线连续对齐。
    95|
    96|### Step 5：绘制框线
    97|
    98|使用 Unicode box drawing 字符：
    99|
   100|```text
   101|┌──┬──┐
   102|│  │  │
   103|├──┼──┤
   104|│  │  │
   105|└──┴──┘
   106|```
   107|
   108|推荐完整字符集：
   109|- 顶边：`┌ ┬ ┐ ─`
   110|- 中边：`├ ┼ ┤ ─`
   111|- 底边：`└ ┴ ┘ ─`
   112|- 竖线：`│`
   113|
   114|每个单元格左右保留 1 个空格 padding。
   115|
   116|### Step 6：输出顺序
   117|
   118|推荐格式：
   119|
   120|```text
   121|┌────┬────┐
   122|│ 表头 │ 表头 │
   123|├────┼────┤
   124|│ 内容 │ 内容 │
   125|└────┴────┘
   126|```
   127|
   128|必要时，在表格后用 2-4 条 bullet 简短说明：
   129|- emoji 已保留并按终端宽度处理。
   130|- 长文字已在单元格内换行。
   131|- 数字列已右对齐。
   132|
   133|## 可执行脚本
   134|
   135|本 skill 附带 `scripts/render_markdown_table.py`，可把 stdin 中的 Markdown pipe table 渲染成 Unicode 框线表：
   136|
   137|```bash
   138|python scripts/render_markdown_table.py < table.md
   139|```
   140|
   141|脚本覆盖：
   142|- Markdown 分隔行校验和 `--- / ---: / :---: / :---` 对齐解析。
   143|- 转义竖线 `\|` 的单元格解析。
   144|- ANSI 转义序列剥离，避免隐藏控制字符影响宽度。
   145|- 中文、emoji、变体选择符、ZWJ 序列的终端显示宽度估算。
   146|- 根据终端宽度压缩长文本列并自动换行。
   147|
   148|## Python 参考实现片段
   149|
   150|用于在需要内联生成稳定 CLI 表格时快速实现。依赖标准库，无需安装第三方包。完整实现优先使用附带脚本。
   151|
   152|```python
   153|import unicodedata
   154|
   155|VS = {'\ufe0e', '\ufe0f'}
   156|ZWJ = '\u200d'
   157|
   158|def char_width(s, i):
   159|    ch = s[i]
   160|    if ch == ZWJ or unicodedata.combining(ch) or ch in VS:
   161|        return 0, 1
   162|    if i + 1 < len(s) and s[i + 1] == '\ufe0f':
   163|        return 2, 2
   164|    return (2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1), 1
   165|
   166|def display_width(s):
   167|    i = w = 0
   168|    while i < len(s):
   169|        cw, step = char_width(s, i)
   170|        w += cw
   171|        i += step
   172|    return w
   173|
   174|def wrap_cell(s, width):
   175|    lines, cur, curw, i = [], '', 0, 0
   176|    while i < len(s):
   177|        cw, step = char_width(s, i)
   178|        cluster = s[i:i + step]
   179|        if cluster == '\n':
   180|            lines.append(cur); cur, curw = '', 0; i += step; continue
   181|        if cur and curw + cw > width:
   182|            lines.append(cur); cur, curw = cluster, cw
   183|        else:
   184|            cur += cluster; curw += cw
   185|        i += step
   186|    lines.append(cur)
   187|    return lines or ['']
   188|
   189|def pad_cell(s, width, align='left'):
   190|    pad = max(0, width - display_width(s))
   191|    if align == 'right':
   192|        return ' ' * pad + s
   193|    if align == 'center':
   194|        left = pad // 2
   195|        return ' ' * left + s + ' ' * (pad - left)
   196|    return s + ' ' * pad
   197|```
   198|
   199|## 示例输出
   200|
   201|当用户要求“emoji 也要对齐，长文字也要对齐”时，应输出类似：
   202|
   203|```text
   204|┌──────────┬──────────────┬────────┬──────────┬──────────────────────────────────────┐
   205|│ 指标类别 │   指标名称   │ 当前值 │   趋势   │                 说明                 │
   206|├──────────┼──────────────┼────────┼──────────┼──────────────────────────────────────┤
   207|│ 进度     │ 总体完成率   │    38% │ ↗️ 上升  │ 仍低于计划，后续需要压缩评审和联调周 │
   208|│          │              │        │          │ 期。                                 │
   209|├──────────┼──────────────┼────────┼──────────┼──────────────────────────────────────┤
   210|│ 沟通     │ 周会参与率   │    88% │ ↘️ 下降  │ 需提醒关键干系人参会，并同步会议结论 │
   211|│          │              │        │          │ 和行动项。                           │
   212|└──────────┴──────────────┴────────┴──────────┴──────────────────────────────────────┘
   213|```
   214|
   215|## 常见错误与修正
   216|
   217|| 错误 | 为什么不行 | 正确做法 |
   218||---|---|---|
   219|| 删除 emoji 来换取对齐 | 改变了用户内容 | 保留 emoji，用显示宽度计算 |
   220|| 建议 HTML 表格 | 用户要的是 CLI Markdown 可视化 | 输出 box drawing table |
   221|| 只输出 Markdown pipe table | 在终端里视觉不稳定 | 解析后渲染为框线表 |
   222|| 长文字撑爆整行 | 终端阅读体验差 | 对长文本列设最大宽度并换行 |
   223|| 用 `len()` 算宽度 | 中文和 emoji 会错位 | 用 Unicode display width |
   224|
   225|## 验收清单
   226|
   227|最终输出前检查：
   228|- [ ] 表格有完整框线。
   229|- [ ] 所有竖线在视觉上对齐。
   230|- [ ] emoji 没有被删除。
   231|- [ ] 长文字在单元格内换行，且其他列补空白。
   232|- [ ] 数字列右对齐。
   233|- [ ] 没有建议 HTML 作为替代方案。
   234|
