from formatador_imersao import format_days
from formatador_imersao.models import DayText


def test_formats_weekday_and_paragraphs_separated_by_blank_lines():
    days = [
        DayText("SEGUNDA", ("1.Um.", "2.Dois.")),
        DayText("TERÇA", ("1.Três.",)),
    ]

    assert format_days(days) == "SEGUNDA\n\n1.Um.\n\n2.Dois.\n\nTERÇA\n\n1.Três.\n"


def test_wraps_paragraph_lines_at_max_length():
    days = [DayText("SEGUNDA", ("1.Deus havia cumprido a primeira parte",))]

    assert format_days(days, max_line_length=15) == (
        "SEGUNDA\n\n1.Deus havia\ncumprido a\nprimeira parte\n"
    )


def test_does_not_break_words_or_hyphenated_references():
    days = [DayText("SEGUNDA", ("1.Texto (Êx 14:15-16, 21).",))]

    assert format_days(days, max_line_length=8) == "SEGUNDA\n\n1.Texto\n(Êx\n14:15-16,\n21).\n"
