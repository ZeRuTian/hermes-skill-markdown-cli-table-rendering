---
name: markdown-cli-table-rendering
description: >-
  Render Markdown pipe tables as aligned CLI box tables with correct terminal display width for Chinese text, emoji, numeric alignment, and wrapped long cells. Use when the user asks to display/preview Markdown tables in Hermes CLI, complains that Markdown tables are misaligned, or asks for boxed/visualized terminal table output. Trigger phrases include markdown表格对齐, CLI表格显示, 大表格显示效果, emoji表格对齐, 长文字表格换行, box table, terminal table rendering.
version: 1.0.0
---

# Markdown CLI 表格渲染

## 目的

当用户要求“测试/展示 Markdown 表格显示效果”时，不要只输出原始 Markdown pipe table，也不要建议改用 HTML。应把 Markdown 表格在 CLI 中**可视化渲染**为带框线、列宽稳定、内容对齐的终端表格。

核心目标：
- 中文、英文、数字混排时视觉对齐。
- emoji / 变体选择符 / 零宽连接符不破坏列宽。
- 长文字在单元格内自动换行。
- 数字列右对齐，文本列左对齐或表头居中。
- 输出适合终端阅读，而不是适合网页渲染。

## 触发场景

使用本 skill，当用户出现以下意图之一：
1. “测试 markdown 大表格显示效果”。
2. “表格没对齐 / 趋势和说明列没对齐”。
3. “emoji 也应该对齐”。
4. “长文字能对齐吗”。
5. “CLI 里要展示成良好的可视化表格 / 要有框线”。
6. 任何要求把 Markdown 表格预览成终端可读表格的任务。

## 输出原则

1. **直接给可视化表格**：优先输出 box drawing table，不要先解释一大段原因。
2. **不要提 HTML 方案**：用户明确关注 CLI Markdown 可视化，不要把问题转移到网页/HTML。
3. **不要把原始 Markdown 当最终展示**：Markdown pipe table 可以作为输入或附录，但 CLI 展示应渲染成框线表。
4. **保留用户内容**：不要为了对齐删除 emoji、缩短中文或改写业务含义。
5. **用显示宽度，不用字符串长度**：宽度计算必须按终端 cell width，而不是 `len()`、字符数或字节数。

## 渲染工作流

### Step 1：识别表格结构

从 Markdown pipe table 中提取：
- 表头行
- 分隔行，例如 `|---|---:|:---:|`
- 数据行
- 每列对齐方式：
  - `---`：默认文本左对齐
  - `---:`：右对齐
  - `:---:`：居中
  - `:---`：左对齐

如果用户只是要求“测试显示效果”，可以直接构造一个覆盖以下边界的测试表：
- 中文列
- 数字列
- emoji 趋势列
- 长说明列
- 百分比、正负数、≤ 等符号

### Step 2：计算终端显示宽度

按 Unicode 显示宽度计算列宽：
- East Asian Width 为 `W` 或 `F` 的字符按 2 列。
- 普通 ASCII 按 1 列。
- combining mark、变体选择符 `U+FE0E/U+FE0F`、零宽连接符 `U+200D` 按 0 列。
- 含 `U+FE0F` 的 emoji-presentation 序列、含 `U+200D` 的 ZWJ emoji 序列、常见 emoji 按 2 列处理。
- 含 `U+FE0E` 且不含 `U+FE0F/U+200D` 的 text-presentation 序列应按普通文本宽度处理；例如 `↗︎` 通常按 1 列，而 `↗️` 按 2 列。

不要用：
- `len(text)`
- UTF-8 字节长度
- 简单中文字符数 × 2 的粗糙算法

### Step 3：确定列宽

推荐规则：
1. 表头和短文本列：按内容最大显示宽度。
2. 数字列：按内容最大显示宽度，右对齐。
3. 长说明列：设置最大宽度，常用 32-48 cell；超过则换行。
4. 总表宽不要明显超过终端宽度；如列很多，优先压缩长文本列。

默认列宽建议：
- 分类列：8-10
- 名称列：12-16
- 数字列：6-10
- 趋势列：8-10
- 说明列：32-48

### Step 4：单元格换行

对每个单元格按显示宽度 wrap：
- 不能在 emoji 变体选择符中间切断。
- 中文可逐字换行。
- 英文长单词如果超过列宽，可硬切。
- 一个数据行内，如果某个单元格换成 N 行，其他列要补空白行，保证竖线连续对齐。

### Step 5：绘制框线

使用 Unicode box drawing 字符：

```text
┌──┬──┐
│  │  │
├──┼──┤
│  │  │
└──┴──┘
```

推荐完整字符集：
- 顶边：`┌ ┬ ┐ ─`
- 中边：`├ ┼ ┤ ─`
- 底边：`└ ┴ ┘ ─`
- 竖线：`│`

每个单元格左右保留 1 个空格 padding。

### Step 6：输出顺序

推荐格式：

```text
┌──────┬──────┐
│ 表头 │ 表头 │
├──────┼──────┤
│ 内容 │ 内容 │
└──────┴──────┘
```

必要时，在表格后用 2-4 条 bullet 简短说明：
- emoji 已保留并按终端宽度处理。
- 长文字已在单元格内换行。
- 数字列已右对齐。

## 可执行脚本

本 skill 附带 `scripts/render_markdown_table.py`，可把 stdin 中的 Markdown pipe table 渲染成 Unicode 框线表：

```bash
python scripts/render_markdown_table.py < table.md
```

脚本覆盖：
- Markdown 分隔行校验和 `--- / ---: / :---: / :---` 对齐解析。
- 转义竖线 `\|` 的单元格解析。
- ANSI 转义序列剥离，避免隐藏控制字符影响宽度。
- 中文、emoji、变体选择符、ZWJ 序列的终端显示宽度估算。
- 根据终端宽度压缩长文本列并自动换行。

## Python 参考实现片段

用于在需要内联生成稳定 CLI 表格时快速实现。依赖标准库，无需安装第三方包。完整实现优先使用附带脚本。

```python
import unicodedata

VS = {'\ufe0e', '\ufe0f'}
ZWJ = '\u200d'

def char_width(s, i):
    ch = s[i]
    if ch == ZWJ or unicodedata.combining(ch) or ch in VS:
        return 0, 1
    if i + 1 < len(s) and s[i + 1] == '\ufe0f':
        return 2, 2
    return (2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1), 1

def display_width(s):
    i = w = 0
    while i < len(s):
        cw, step = char_width(s, i)
        w += cw
        i += step
    return w

def wrap_cell(s, width):
    lines, cur, curw, i = [], '', 0, 0
    while i < len(s):
        cw, step = char_width(s, i)
        cluster = s[i:i + step]
        if cluster == '\n':
            lines.append(cur); cur, curw = '', 0; i += step; continue
        if cur and curw + cw > width:
            lines.append(cur); cur, curw = cluster, cw
        else:
            cur += cluster; curw += cw
        i += step
    lines.append(cur)
    return lines or ['']

def pad_cell(s, width, align='left'):
    pad = max(0, width - display_width(s))
    if align == 'right':
        return ' ' * pad + s
    if align == 'center':
        left = pad // 2
        return ' ' * left + s + ' ' * (pad - left)
    return s + ' ' * pad
```

## 示例输出

当用户要求“emoji 也要对齐，长文字也要对齐”时，应输出类似：

```text
┌──────────┬──────────────┬────────┬──────────┬──────────────────────────────────────┐
│ 指标类别 │   指标名称   │ 当前值 │   趋势   │                 说明                 │
├──────────┼──────────────┼────────┼──────────┼──────────────────────────────────────┤
│ 进度     │ 总体完成率   │    38% │ ↗️ 上升  │ 仍低于计划，后续需要压缩评审和联调周 │
│          │              │        │          │ 期。                                 │
├──────────┼──────────────┼────────┼──────────┼──────────────────────────────────────┤
│ 沟通     │ 周会参与率   │    88% │ ↘️ 下降  │ 需提醒关键干系人参会，并同步会议结论 │
│          │              │        │          │ 和行动项。                           │
└──────────┴──────────────┴────────┴──────────┴──────────────────────────────────────┘
```

## 常见错误与修正

| 错误 | 为什么不行 | 正确做法 |
|---|---|---|
| 删除 emoji 来换取对齐 | 改变了用户内容 | 保留 emoji，用显示宽度计算 |
| 建议 HTML 表格 | 用户要的是 CLI Markdown 可视化 | 输出 box drawing table |
| 只输出 Markdown pipe table | 在终端里视觉不稳定 | 解析后渲染为框线表 |
| 长文字撑爆整行 | 终端阅读体验差 | 对长文本列设最大宽度并换行 |
| 用 `len()` 算宽度 | 中文和 emoji 会错位 | 用 Unicode display width |

## 文档示例规则

如果把渲染结果写进 README、Skill 示例、GitHub 仓库或其他文档：
1. 不要手写或凭感觉拼接示例 Output。
2. 优先用 `scripts/render_markdown_table.py` 对示例 Markdown 输入真实生成输出。
3. 生成后做一次显示宽度校验：同一个 box table 中每一行的 terminal display width 必须相同。
4. 示例应覆盖真实边界，而不是只放一行玩具数据；至少包含多列、多行、中文、数字右对齐、趋势符号、风险/状态列和长说明换行。
5. GitHub README 的 code block 不是可靠的视觉验收环境：浏览器字体 fallback 会让中文、emoji、变体选择符看起来错位。若需要在 GitHub 页面展示“已对齐”的视觉效果，优先提供由已验证数据生成的 SVG/图片预览，并把真实终端文本另存为 `examples/*-output.txt`。
6. GitHub 图片/SVG 可能被缓存；替换预览时可改文件名（例如 `complex-browser-safe-preview.svg`）或更新引用来避免旧图缓存。
7. 发布安装说明后，用 fresh clone 到临时目录的方式验证 `git clone`、脚本路径和示例输入都能运行，不要只凭路径推测。
8. 如果用户指出示例没对齐，立即修正文档示例，并检查是否是复制/打包流程污染了文件内容。

## 验收清单

最终输出前检查：
- [ ] 表格有完整框线。
- [ ] 所有竖线在视觉上对齐。
- [ ] emoji 没有被删除。
- [ ] 长文字在单元格内换行，且其他列补空白。
- [ ] 数字列右对齐。
- [ ] 没有建议 HTML 作为替代方案。
- [ ] 文档中的示例 Output 是由渲染器生成或通过等宽校验的，不是手写猜测。
