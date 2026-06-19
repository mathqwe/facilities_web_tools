from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from src.rateia_ai.core.modelo import LinhaRateio
from src.rateia_ai.core.normalizacao import decimal_moeda


def somar_por_cc(linhas: Iterable[LinhaRateio]) -> dict[str, Decimal]:
    totais: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for linha in linhas:
        if not linha.incluir_no_rateio:
            continue
        if not linha.cc_ajustado:
            continue
        valor = decimal_moeda(linha.valor)
        if valor == Decimal("0.00"):
            continue
        totais[linha.cc_ajustado] += valor
    return dict(totais)


def chave_ordenacao_cc(cc: str):
    texto = str(cc)
    return (0, int(texto)) if texto.isdigit() else (1, texto)
