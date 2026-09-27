"""Interface Streamlit: upload do PDF, cópia e download do texto formatado."""

import json
from pathlib import Path

import streamlit as st

from formatador_imersao import NoWeekdayFoundError, extract_days, format_days
from formatador_imersao.formatter import DEFAULT_MAX_LINE_LENGTH

ACTION_BUTTONS_TEMPLATE = Path(__file__).parent / "templates" / "action_buttons.html"


def _to_js_string(value: str) -> str:
    """Literal JavaScript seguro para ser embutido dentro de uma tag <script>."""
    return json.dumps(value).replace("</", "<\\/")


def action_buttons(text: str, file_name: str) -> None:
    """Botões "Copiar tudo" e "Baixar .txt" lado a lado e com o mesmo tamanho.

    Ficam no mesmo componente HTML porque o Streamlit não tem botão de copiar
    nativo, e misturar um iframe com um botão nativo desalinha os dois.
    """
    html = (
        ACTION_BUTTONS_TEMPLATE.read_text(encoding="utf-8")
        .replace("__TEXT__", _to_js_string(text))
        .replace("__FILE_NAME__", _to_js_string(file_name))
    )
    st.iframe(html, height=50)


def main() -> None:
    st.set_page_config(page_title="Formatador Imersão Diária", page_icon="📖")
    st.title("📖 Formatador Imersão Diária")
    st.caption("Envie o panfleto em PDF e baixe o texto separado por dia da semana.")

    uploaded = st.file_uploader("Panfleto (PDF)", type="pdf")
    max_line_length = st.number_input(
        "Máximo de caracteres por linha",
        min_value=10,
        max_value=200,
        value=DEFAULT_MAX_LINE_LENGTH,
        help="Ajuste para que as linhas caibam no slide do Holyrics.",
    )
    if uploaded is None:
        return

    try:
        text = format_days(extract_days(uploaded.getvalue()), max_line_length)
    except NoWeekdayFoundError as error:
        st.error(str(error))
        return
    except Exception:
        st.error("Não foi possível ler o PDF. Verifique se o arquivo é válido.")
        return

    action_buttons(text, file_name=f"{Path(uploaded.name).stem}.txt")
    st.text_area("Pré-visualização", text, height=500)


main()
