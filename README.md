# hermes-skill-markdown-cli-table-rendering

Hermes skill for rendering Markdown pipe tables as aligned CLI box tables.

## What it solves

Markdown tables often look misaligned in terminal output when they contain:

- Chinese full-width characters
- emoji and variation selectors
- numeric columns
- long text cells that need wrapping

This skill teaches Hermes to render Markdown tables as Unicode box-drawing tables in CLI contexts.

## Install as a Hermes skill

Clone this repository into your Hermes skills directory using the skill name as the target folder:

```bash
mkdir -p ~/.hermes/skills/productivity
git clone https://github.com/ZeRuTian/hermes-skill-markdown-cli-table-rendering.git \
  ~/.hermes/skills/productivity/markdown-cli-table-rendering
```

If it is already installed, update it with:

```bash
git -C ~/.hermes/skills/productivity/markdown-cli-table-rendering pull
```

Then start a new Hermes session so the skill list is reloaded.

## Use the standalone renderer

After installation:

```bash
python3 ~/.hermes/skills/productivity/markdown-cli-table-rendering/scripts/render_markdown_table.py < table.md
```

From a local clone of this repository:

```bash
python3 scripts/render_markdown_table.py < table.md
```

## Verify installation

```bash
python3 ~/.hermes/skills/productivity/markdown-cli-table-rendering/scripts/render_markdown_table.py \
  < ~/.hermes/skills/productivity/markdown-cli-table-rendering/examples/emoji-cli-sample.md
```

You should see a Unicode box table with aligned columns.

## GitHub README display note

GitHub web code blocks may render emoji through a browser fallback font, so an emoji table can look misaligned on GitHub even when its terminal cell widths are correct.

For that reason, the README preview below uses a text-presentation arrow (`↗︎`) instead of an emoji-presentation arrow (`↗️`). The renderer still supports emoji in real CLI / TUI output; use `examples/emoji-cli-sample.md` to test that locally.

## Browser-safe preview

Input Markdown:

```markdown
| 指标类别 | 指标名称 | 当前值 | 趋势 | 说明 |
|---|---|---:|---|---|
| 进度 | 总体完成率 | 38% | ↗︎ 上升 | 仍低于计划，后续需要压缩评审和联调周期。 |
```

Output:

```text
┌──────────┬────────────┬────────┬────────┬──────────────────────────────────────────┐
│ 指标类别 │  指标名称  │ 当前值 │  趋势  │                   说明                   │
├──────────┼────────────┼────────┼────────┼──────────────────────────────────────────┤
│ 进度     │ 总体完成率 │    38% │ ↗︎ 上升 │ 仍低于计划，后续需要压缩评审和联调周期。 │
└──────────┴────────────┴────────┴────────┴──────────────────────────────────────────┘
```

## Files

- `SKILL.md` — Hermes skill definition and workflow
- `scripts/render_markdown_table.py` — standalone renderer for Markdown pipe tables
- `examples/browser-safe-sample.md` — README-safe text-presentation arrow example
- `examples/browser-safe-sample-output.txt` — generated browser-safe output
- `examples/emoji-cli-sample.md` — emoji test input for CLI / TUI
- `examples/emoji-cli-sample-output.txt` — generated emoji CLI output
- `references/test-prompts.json` — test prompts for evaluating behavior
- `references/darwin-results.tsv` — Darwin optimization scoring record

## License

MIT
