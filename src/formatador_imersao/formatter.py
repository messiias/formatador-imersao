"""Formatação do texto extraído no layout de saída, pronto para o Holyrics.

No Holyrics, cada bloco separado por linha em branco vira um slide; por isso
cada ponto numerado é um bloco, quebrado em linhas de tamanho máximo.
"""

import textwrap

from formatador_imersao.models import DayText

DEFAULT_MAX_LINE_LENGTH = 40


def format_days(days: list[DayText], max_line_length: int = DEFAULT_MAX_LINE_LENGTH) -> str:
    """Gera o texto final: dia da semana e seus parágrafos, separados por linha em branco."""
    return "\n\n".join(_format_day(day, max_line_length) for day in days) + "\n"


def _format_day(day: DayText, max_line_length: int) -> str:
    paragraphs = (_wrap(paragraph, max_line_length) for paragraph in day.paragraphs)
    return "\n\n".join((day.weekday, *paragraphs))


def _wrap(paragraph: str, max_line_length: int) -> str:
    """Quebra apenas entre palavras, preservando referências como "14:1-2"."""
    return "\n".join(
        textwrap.wrap(
            paragraph,
            width=max_line_length,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )
