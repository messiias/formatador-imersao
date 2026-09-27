# Formatador Imersão Diária

Aplicação Streamlit que recebe o panfleto **Imersão Diária** em PDF e gera um
`.txt` com o texto de cada dia da semana, ignorando a ilustração da capa,
pronto para o **Holyrics**: cada ponto numerado vira um bloco (slide) e suas
linhas são quebradas num tamanho máximo configurável (padrão: 40 caracteres).

```
SEGUNDA

1.Deus havia cumprido a primeira parte
da promessa feita a Abraão: já havia a
...

2.O povo que saiu do Egito, após 215
...

TERÇA

...
```

## Como usar

```bash
uv sync
uv run streamlit run app.py
```

Envie o PDF, confira a pré-visualização e use **Copiar tudo** ou **Baixar .txt**.

## Estrutura

```
app.py                          # interface Streamlit (upload, copiar, baixar)
templates/action_buttons.html   # botões "Copiar tudo" e "Baixar .txt"
src/formatador_imersao/
  models.py                     # Word, DayText e a lista de dias da semana
  extractor.py                  # PDF -> texto por dia (detecção de colunas)
  formatter.py                  # texto por dia -> .txt (quebra de linhas)
tests/                          # testes com PDFs gerados em memória
```

Cada coluna do panfleto começa com o nome do dia. A largura das colunas é a
distância entre esses cabeçalhos; tudo fora delas (a ilustração) é descartado.

## Testes

```bash
uv run pytest
```
