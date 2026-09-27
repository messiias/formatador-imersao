import pymupdf
import pytest

from formatador_imersao import NoWeekdayFoundError, extract_days

COLUMN_WIDTH = 200


def _make_pdf(columns: list[list[str]], extra: str | None = None) -> bytes:
    """Cria um PDF com uma coluna por lista de linhas e, opcionalmente, uma
    coluna decorativa à direita (simulando a ilustração da capa)."""
    document = pymupdf.open()
    page = document.new_page(width=842, height=595)
    for index, lines in enumerate(columns):
        x = 20 + index * COLUMN_WIDTH
        for row, line in enumerate(lines):
            page.insert_text((x, 40 + row * 14), line, fontsize=10)
    if extra:
        page.insert_text((20 + len(columns) * COLUMN_WIDTH + 30, 60), extra, fontsize=10)
    return document.tobytes()


def test_extracts_each_column_under_its_weekday():
    pdf = _make_pdf([["SEGUNDA", "1.Primeiro", "ponto."], ["TERÇA", "1.Outro", "texto."]])

    days = extract_days(pdf)

    assert [day.weekday for day in days] == ["SEGUNDA", "TERÇA"]
    assert days[0].paragraphs == ("1.Primeiro ponto.",)
    assert days[1].paragraphs == ("1.Outro texto.",)


def test_ignores_content_outside_weekday_columns():
    pdf = _make_pdf([["SEGUNDA", "1.a"], ["TERÇA", "1.b"]], extra="ILUSTRACAO")

    days = extract_days(pdf)

    assert [day.paragraphs for day in days] == [("1.a",), ("1.b",)]


def test_splits_paragraphs_on_numbered_items_only():
    pdf = _make_pdf([["SEGUNDA", "1.Um texto", "(Gn 1:1).", "2.Dois"]])

    (day,) = extract_days(pdf)

    assert day.paragraphs == ("1.Um texto (Gn 1:1).", "2.Dois")


def test_discards_text_before_first_numbered_item():
    pdf = _make_pdf([["SEGUNDA", "(Trecho de referência", "da mensagem)", "1.Um"]])

    (day,) = extract_days(pdf)

    assert day.paragraphs == ("1.Um",)


def test_joins_hyphenated_line_break_without_space():
    pdf = _make_pdf([["SEGUNDA", "1.Região de Pi-", "Hairote."]])

    (day,) = extract_days(pdf)

    assert day.paragraphs == ("1.Região de Pi-Hairote.",)


def test_returns_days_in_week_order():
    pdf = _make_pdf([["QUARTA", "c"], ["SEGUNDA", "a"]])

    assert [day.weekday for day in extract_days(pdf)] == ["SEGUNDA", "QUARTA"]


def test_raises_when_no_weekday_is_found():
    with pytest.raises(NoWeekdayFoundError):
        extract_days(_make_pdf([["Sem cabeçalho"]]))
