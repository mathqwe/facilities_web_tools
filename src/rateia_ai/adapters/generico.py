from __future__ import annotations

"""Adapter reservado para o modo genérico/manual assistido.

Nesta primeira etapa, ele ainda não processa arquivos. Vamos implementar depois
que Movida e Uber estiverem validados, porque o genérico precisa de uma tela de
seleção de aba, coluna de CC e coluna de valor.
"""

from src.rateia_ai.core.modelo import ErroRateio


def processar(*args, **kwargs):
    raise ErroRateio("O modo genérico/manual assistido ainda será implementado na próxima etapa.")
