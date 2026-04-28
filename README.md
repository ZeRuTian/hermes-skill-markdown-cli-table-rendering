# hermes-skill-markdown-cli-table-rendering

Hermes skill for rendering Markdown pipe tables as aligned CLI box tables.

## What it solves

Markdown tables often look misaligned in terminal output when they contain:

- Chinese full-width characters
- emoji and variation selectors
- numeric columns
- long text cells that need wrapping

This skill teaches Hermes to render Markdown tables as Unicode box-drawing tables in CLI contexts.

## Files

- `SKILL.md` — Hermes skill definition and workflow
- `scripts/render_markdown_table.py` — standalone renderer for Markdown pipe tables
- `references/test-prompts.json` — test prompts for evaluating behavior
- `references/darwin-results.tsv` — Darwin optimization scoring record

## Usage

```bash
python3 scripts/render_markdown_table.py < table.md
```

## Example

Input Markdown:

```markdown
| 指标类别 | 指标名称 | 当前值 | 趋势 | 说明 |
|---|---|---:|---|---|
| 进度 | 总体完成率 | 38% | ↗️ 上升 | 仍低于计划，后续需要压缩评审和联调周期。 |
```

Output:

```text
┌──────────┬────────────┬────────┬──────────┬──────────────────────────────────────┐
│ 指标类别 │  指标名称  │ 当前值 │   趋势   │                 说明                 │
├──────────┼────────────┼────────┼──────────┼──────────────────────────────────────┤
│ 进度     │ 总体完成率 │    38% │ ↗️ 上升  │ 仍低于计划，后续需要压缩评审和联调周 │
│          │            │        │          │ 期。                                 │
└──────────┴────────────┴────────┴──────────┴──────────────────────────────────────┘
```

## License

MIT
