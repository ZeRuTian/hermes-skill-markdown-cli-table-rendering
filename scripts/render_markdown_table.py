     1|#!/usr/bin/env python3
     2|"""Render a Markdown pipe table as a Unicode box table for CLI output.
     3|
     4|Usage:
     5|  python render_markdown_table.py < table.md
     6|"""
     7|from __future__ import annotations
     8|
     9|import re
    10|import shutil
    11|import sys
    12|import unicodedata
    13|
    14|ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
    15|VS = {"\ufe0e", "\ufe0f"}
    16|ZWJ = "\u200d"
    17|
    18|
    19|def strip_ansi(text: str) -> str:
    20|    return ANSI_RE.sub("", text)
    21|
    22|
    23|def is_zero_width(ch: str) -> bool:
    24|    return ch == ZWJ or ch in VS or bool(unicodedata.combining(ch))
    25|
    26|
    27|def is_emojiish(ch: str) -> bool:
    28|    cp = ord(ch)
    29|    return (
    30|        0x1F000 <= cp <= 0x1FAFF
    31|        or 0x2600 <= cp <= 0x27BF
    32|        or cp in (0x2194, 0x2195, 0x2196, 0x2197, 0x2198, 0x2199)
    33|    )
    34|
    35|
    36|def clusters(text: str):
    37|    """Yield rough grapheme clusters, preserving emoji variation and ZWJ sequences."""
    38|    text = strip_ansi(text)
    39|    i = 0
    40|    while i < len(text):
    41|        cluster = text[i]
    42|        i += 1
    43|        while i < len(text) and (text[i] in VS or unicodedata.combining(text[i])):
    44|            cluster += text[i]
    45|            i += 1
    46|        while i < len(text) and text[i] == ZWJ:
    47|            cluster += text[i]
    48|            i += 1
    49|            if i < len(text):
    50|                cluster += text[i]
    51|                i += 1
    52|            while i < len(text) and (text[i] in VS or unicodedata.combining(text[i])):
    53|                cluster += text[i]
    54|                i += 1
    55|        yield cluster
    56|
    57|
    58|def cluster_width(cluster: str) -> int:
    59|    if not cluster or all(is_zero_width(ch) for ch in cluster):
    60|        return 0
    61|    if ZWJ in cluster or "\ufe0f" in cluster or any(is_emojiish(ch) for ch in cluster):
    62|        return 2
    63|    width = 0
    64|    for ch in cluster:
    65|        if is_zero_width(ch):
    66|            continue
    67|        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    68|    return width
    69|
    70|
    71|def display_width(text: str) -> int:
    72|    return sum(cluster_width(c) for c in clusters(text))
    73|
    74|
    75|def split_row(line: str) -> list[str]:
    76|    line = line.strip()
    77|    if line.startswith("|"):
    78|        line = line[1:]
    79|    if line.endswith("|"):
    80|        line = line[:-1]
    81|
    82|    cells, cur, escaped = [], [], False
    83|    for ch in line:
    84|        if escaped:
    85|            cur.append(ch)
    86|            escaped = False
    87|        elif ch == "\\":
    88|            escaped = True
    89|        elif ch == "|":
    90|            cells.append("".join(cur).strip())
    91|            cur = []
    92|        else:
    93|            cur.append(ch)
    94|    if escaped:
    95|        cur.append("\\")
    96|    cells.append("".join(cur).strip())
    97|    return cells
    98|
    99|
   100|def parse_separator(cells: list[str]) -> list[str] | None:
   101|    aligns = []
   102|    for cell in cells:
   103|        raw = cell.replace(" ", "")
   104|        if not re.fullmatch(r":?-{3,}:?", raw):
   105|            return None
   106|        if raw.startswith(":") and raw.endswith(":"):
   107|            aligns.append("center")
   108|        elif raw.endswith(":"):
   109|            aligns.append("right")
   110|        else:
   111|            aligns.append("left")
   112|    return aligns
   113|
   114|
   115|def parse_markdown_table(text: str):
   116|    lines = [ln for ln in text.splitlines() if ln.strip()]
   117|    for i in range(len(lines) - 1):
   118|        header = split_row(lines[i])
   119|        sep_cells = split_row(lines[i + 1])
   120|        aligns = parse_separator(sep_cells)
   121|        if aligns and len(header) == len(aligns):
   122|            rows = []
   123|            for ln in lines[i + 2 :]:
   124|                if "|" not in ln:
   125|                    break
   126|                row = split_row(ln)
   127|                if len(row) < len(header):
   128|                    row += [""] * (len(header) - len(row))
   129|                rows.append(row[: len(header)])
   130|            return header, aligns, rows
   131|    raise SystemExit("No valid Markdown pipe table found on stdin.")
   132|
   133|
   134|def wrap_cell(text: str, width: int) -> list[str]:
   135|    out, cur, curw = [], "", 0
   136|    for cluster in clusters(text):
   137|        if cluster == "\n":
   138|            out.append(cur)
   139|            cur, curw = "", 0
   140|            continue
   141|        cw = cluster_width(cluster)
   142|        if cur and curw + cw > width:
   143|            out.append(cur)
   144|            cur, curw = cluster, cw
   145|        else:
   146|            cur += cluster
   147|            curw += cw
   148|    out.append(cur)
   149|    return out or [""]
   150|
   151|
   152|def pad(text: str, width: int, align: str = "left") -> str:
   153|    gap = max(0, width - display_width(text))
   154|    if align == "right":
   155|        return " " * gap + text
   156|    if align == "center":
   157|        left = gap // 2
   158|        return " " * left + text + " " * (gap - left)
   159|    return text + " " * gap
   160|
   161|
   162|def choose_widths(header: list[str], rows: list[list[str]], aligns: list[str]) -> list[int]:
   163|    columns = list(zip(header, *rows)) if rows else [(h,) for h in header]
   164|    widths = [max(display_width(str(cell)) for cell in col) for col in columns]
   165|    widths = [max(3, w) for w in widths]
   166|
   167|    # Cap naturally long text columns first.
   168|    for idx, align in enumerate(aligns):
   169|        if align != "right" and widths[idx] > 48:
   170|            widths[idx] = 48
   171|
   172|    term_width = shutil.get_terminal_size((100, 24)).columns
   173|    max_table_width = max(40, term_width - 2)
   174|
   175|    def total_width() -> int:
   176|        return sum(widths) + 3 * len(widths) + 1
   177|
   178|    while total_width() > max_table_width:
   179|        candidates = [i for i, a in enumerate(aligns) if a != "right" and widths[i] > 8]
   180|        if not candidates:
   181|            candidates = [i for i in range(len(widths)) if widths[i] > 5]
   182|        if not candidates:
   183|            break
   184|        i = max(candidates, key=lambda n: widths[n])
   185|        widths[i] -= 1
   186|    return widths
   187|
   188|
   189|def border(left: str, mid: str, right: str, widths: list[int]) -> str:
   190|    return left + mid.join("─" * (w + 2) for w in widths) + right
   191|
   192|
   193|def render_row(cells: list[str], widths: list[int], aligns: list[str], header: bool = False) -> list[str]:
   194|    wrapped = [wrap_cell(str(cell), widths[i]) for i, cell in enumerate(cells)]
   195|    height = max(len(lines) for lines in wrapped)
   196|    out = []
   197|    for line_idx in range(height):
   198|        parts = []
   199|        for i, lines in enumerate(wrapped):
   200|            text = lines[line_idx] if line_idx < len(lines) else ""
   201|            align = "center" if header else aligns[i]
   202|            parts.append(" " + pad(text, widths[i], align) + " ")
   203|        out.append("│" + "│".join(parts) + "│")
   204|    return out
   205|
   206|
   207|def render_table(header: list[str], aligns: list[str], rows: list[list[str]]) -> str:
   208|    widths = choose_widths(header, rows, aligns)
   209|    lines = [border("┌", "┬", "┐", widths)]
   210|    lines.extend(render_row(header, widths, aligns, header=True))
   211|    lines.append(border("├", "┼", "┤", widths))
   212|    for idx, row in enumerate(rows):
   213|        lines.extend(render_row(row, widths, aligns))
   214|        if idx != len(rows) - 1:
   215|            lines.append(border("├", "┼", "┤", widths))
   216|    lines.append(border("└", "┴", "┘", widths))
   217|    return "\n".join(lines)
   218|
   219|
   220|def main() -> None:
   221|    header, aligns, rows = parse_markdown_table(sys.stdin.read())
   222|    print(render_table(header, aligns, rows))
   223|
   224|
   225|if __name__ == "__main__":
   226|    main()
   227|
