#!/usr/bin/env python3
"""Render a Markdown pipe table as a Unicode box table for CLI output.

Usage:
  python render_markdown_table.py < table.md
"""
from __future__ import annotations

import re
import shutil
import sys
import unicodedata

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
VS = {"\ufe0e", "\ufe0f"}
ZWJ = "\u200d"


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def is_zero_width(ch: str) -> bool:
    return ch == ZWJ or ch in VS or bool(unicodedata.combining(ch))


def is_emojiish(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x1F000 <= cp <= 0x1FAFF
        or 0x2600 <= cp <= 0x27BF
        or cp in (0x2194, 0x2195, 0x2196, 0x2197, 0x2198, 0x2199)
    )


def clusters(text: str):
    """Yield rough grapheme clusters, preserving emoji variation and ZWJ sequences."""
    text = strip_ansi(text)
    i = 0
    while i < len(text):
        cluster = text[i]
        i += 1
        while i < len(text) and (text[i] in VS or unicodedata.combining(text[i])):
            cluster += text[i]
            i += 1
        while i < len(text) and text[i] == ZWJ:
            cluster += text[i]
            i += 1
            if i < len(text):
                cluster += text[i]
                i += 1
            while i < len(text) and (text[i] in VS or unicodedata.combining(text[i])):
                cluster += text[i]
                i += 1
        yield cluster


def cluster_width(cluster: str) -> int:
    if not cluster or all(is_zero_width(ch) for ch in cluster):
        return 0
    if ZWJ in cluster or "\ufe0f" in cluster or any(is_emojiish(ch) for ch in cluster):
        return 2
    width = 0
    for ch in cluster:
        if is_zero_width(ch):
            continue
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def display_width(text: str) -> int:
    return sum(cluster_width(c) for c in clusters(text))


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]

    cells, cur, escaped = [], [], False
    for ch in line:
        if escaped:
            cur.append(ch)
            escaped = False
        elif ch == "\\":
            escaped = True
        elif ch == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if escaped:
        cur.append("\\")
    cells.append("".join(cur).strip())
    return cells


def parse_separator(cells: list[str]) -> list[str] | None:
    aligns = []
    for cell in cells:
        raw = cell.replace(" ", "")
        if not re.fullmatch(r":?-{3,}:?", raw):
            return None
        if raw.startswith(":") and raw.endswith(":"):
            aligns.append("center")
        elif raw.endswith(":"):
            aligns.append("right")
        else:
            aligns.append("left")
    return aligns


def parse_markdown_table(text: str):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    for i in range(len(lines) - 1):
        header = split_row(lines[i])
        sep_cells = split_row(lines[i + 1])
        aligns = parse_separator(sep_cells)
        if aligns and len(header) == len(aligns):
            rows = []
            for ln in lines[i + 2 :]:
                if "|" not in ln:
                    break
                row = split_row(ln)
                if len(row) < len(header):
                    row += [""] * (len(header) - len(row))
                rows.append(row[: len(header)])
            return header, aligns, rows
    raise SystemExit("No valid Markdown pipe table found on stdin.")


def wrap_cell(text: str, width: int) -> list[str]:
    out, cur, curw = [], "", 0
    for cluster in clusters(text):
        if cluster == "\n":
            out.append(cur)
            cur, curw = "", 0
            continue
        cw = cluster_width(cluster)
        if cur and curw + cw > width:
            out.append(cur)
            cur, curw = cluster, cw
        else:
            cur += cluster
            curw += cw
    out.append(cur)
    return out or [""]


def pad(text: str, width: int, align: str = "left") -> str:
    gap = max(0, width - display_width(text))
    if align == "right":
        return " " * gap + text
    if align == "center":
        left = gap // 2
        return " " * left + text + " " * (gap - left)
    return text + " " * gap


def choose_widths(header: list[str], rows: list[list[str]], aligns: list[str]) -> list[int]:
    columns = list(zip(header, *rows)) if rows else [(h,) for h in header]
    widths = [max(display_width(str(cell)) for cell in col) for col in columns]
    widths = [max(3, w) for w in widths]

    # Cap naturally long text columns first.
    for idx, align in enumerate(aligns):
        if align != "right" and widths[idx] > 48:
            widths[idx] = 48

    term_width = shutil.get_terminal_size((100, 24)).columns
    max_table_width = max(40, term_width - 2)

    def total_width() -> int:
        return sum(widths) + 3 * len(widths) + 1

    while total_width() > max_table_width:
        candidates = [i for i, a in enumerate(aligns) if a != "right" and widths[i] > 8]
        if not candidates:
            candidates = [i for i in range(len(widths)) if widths[i] > 5]
        if not candidates:
            break
        i = max(candidates, key=lambda n: widths[n])
        widths[i] -= 1
    return widths


def border(left: str, mid: str, right: str, widths: list[int]) -> str:
    return left + mid.join("─" * (w + 2) for w in widths) + right


def render_row(cells: list[str], widths: list[int], aligns: list[str], header: bool = False) -> list[str]:
    wrapped = [wrap_cell(str(cell), widths[i]) for i, cell in enumerate(cells)]
    height = max(len(lines) for lines in wrapped)
    out = []
    for line_idx in range(height):
        parts = []
        for i, lines in enumerate(wrapped):
            text = lines[line_idx] if line_idx < len(lines) else ""
            align = "center" if header else aligns[i]
            parts.append(" " + pad(text, widths[i], align) + " ")
        out.append("│" + "│".join(parts) + "│")
    return out


def render_table(header: list[str], aligns: list[str], rows: list[list[str]]) -> str:
    widths = choose_widths(header, rows, aligns)
    lines = [border("┌", "┬", "┐", widths)]
    lines.extend(render_row(header, widths, aligns, header=True))
    lines.append(border("├", "┼", "┤", widths))
    for idx, row in enumerate(rows):
        lines.extend(render_row(row, widths, aligns))
        if idx != len(rows) - 1:
            lines.append(border("├", "┼", "┤", widths))
    lines.append(border("└", "┴", "┘", widths))
    return "\n".join(lines)


def main() -> None:
    header, aligns, rows = parse_markdown_table(sys.stdin.read())
    print(render_table(header, aligns, rows))


if __name__ == "__main__":
    main()
