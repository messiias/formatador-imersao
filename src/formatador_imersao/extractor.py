"""Extração do texto de cada dia da semana a partir do PDF do panfleto.

O panfleto é diagramado em colunas: cada coluna começa com o nome do dia
da semana. A largura das colunas é inferida pela distância entre esses
cabeçalhos, de modo que qualquer conteúdo fora delas (como a ilustração
da capa) é descartado.
"""

import re
from statistics import median

import pymupdf

from formatador_imersao.models import WEEKDAYS, DayText, Word

LINE_TOLERANCE = 3.0
PARAGRAPH_START = re.compile(r"^\d+\.\S")


class NoWeekdayFoundError(ValueError):
    """O PDF não contém nenhum cabeçalho de dia da semana."""


def extract_days(pdf_bytes: bytes) -> list[DayText]:
    """Retorna o texto de cada dia encontrado, na ordem da semana."""
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        pages = [(_read_words(page), page.rect.width) for page in document]

    headers_by_page = [_find_headers(words) for words, _ in pages]
    if not any(headers_by_page):
        raise NoWeekdayFoundError("Nenhum dia da semana encontrado no PDF.")

    column_width = _estimate_column_width(headers_by_page, pages[0][1])
    days = [
        DayText(header.text, _build_paragraphs(_column_words(words, header, column_width)))
        for (words, _), headers in zip(pages, headers_by_page)
        for header in headers
    ]
    return sorted(days, key=lambda day: WEEKDAYS.index(day.weekday))


def _read_words(page: pymupdf.Page) -> list[Word]:
    return [Word(text, x0, y0, x1, y1) for x0, y0, x1, y1, text, *_ in page.get_text("words")]


def _find_headers(words: list[Word]) -> list[Word]:
    return sorted((word for word in words if word.text in WEEKDAYS), key=lambda word: word.x0)


def _estimate_column_width(headers_by_page: list[list[Word]], page_width: float) -> float:
    """Distância típica entre cabeçalhos vizinhos; fallback para 1/4 da página."""
    gaps = [
        right.center_x - left.center_x
        for headers in headers_by_page
        for left, right in zip(headers, headers[1:])
    ]
    return median(gaps) if gaps else page_width / 4


def _column_words(words: list[Word], header: Word, column_width: float) -> list[Word]:
    left = header.center_x - column_width / 2
    right = header.center_x + column_width / 2
    return [
        word
        for word in words
        if left <= word.center_x < right and word.y0 > header.y1 and word is not header
    ]


def _group_lines(words: list[Word]) -> list[str]:
    """Agrupa palavras com a mesma altura em linhas, da esquerda para a direita."""
    lines: list[list[Word]] = []
    for word in sorted(words, key=lambda w: (w.y0, w.x0)):
        if lines and abs(lines[-1][0].y0 - word.y0) <= LINE_TOLERANCE:
            lines[-1].append(word)
        else:
            lines.append([word])
    return [" ".join(w.text for w in sorted(line, key=lambda w: w.x0)) for line in lines]


def _build_paragraphs(words: list[Word]) -> tuple[str, ...]:
    """Junta as linhas em parágrafos, que no panfleto começam com um item numerado ("1.Texto").

    O que vem antes do primeiro item (o "Trecho de referência") é descartado.
    """
    paragraphs: list[str] = []
    for line in _group_lines(words):
        if PARAGRAPH_START.match(line):
            paragraphs.append(line)
        elif paragraphs:
            paragraphs[-1] = _join(paragraphs[-1], line)
    return tuple(paragraphs)


def _join(text: str, continuation: str) -> str:
    separator = "" if text.endswith("-") else " "
    return f"{text}{separator}{continuation}"
