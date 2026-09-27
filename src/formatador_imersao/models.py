"""Estruturas de dados do domínio."""

from dataclasses import dataclass

WEEKDAYS: tuple[str, ...] = (
    "SEGUNDA",
    "TERÇA",
    "QUARTA",
    "QUINTA",
    "SEXTA",
    "SÁBADO",
    "DOMINGO",
)


@dataclass(frozen=True)
class Word:
    """Palavra do PDF com sua caixa delimitadora (em pontos)."""

    text: str
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2


@dataclass(frozen=True)
class DayText:
    """Texto extraído de um dia da semana, em parágrafos."""

    weekday: str
    paragraphs: tuple[str, ...]
