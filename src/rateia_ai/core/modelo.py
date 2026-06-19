from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any


class ErroRateio(Exception):
    """Erro esperado durante a leitura/processamento de um arquivo de rateio."""


@dataclass
class LinhaRateio:
    """Linha normalizada usada pelo motor comum de rateio."""

    cc_original: Any
    cc_ajustado: str | None
    cc_descricao: str | None
    valor: Decimal
    dados: dict[str, Any] = field(default_factory=dict)
    incluir_no_rateio: bool = True
    motivo_ignorado: str | None = None


@dataclass
class RateioArquivo:
    """Resultado gerado por um adapter.

    Um arquivo de entrada pode gerar mais de um RateioArquivo. Ex.: Movida gera
    um rateio para LOCAÇÃO e outro para MULTAS quando as duas abas existem.
    """

    fornecedor: str
    subtipo: str
    arquivo_origem: str
    identificador: str
    nome_saida: str
    arquivo_saida: Path
    total_rateado: Decimal
    total_arquivo: Decimal
    valor_sem_cc: Decimal
    linhas_processadas: int
    linhas_rateadas: int
    linhas_sem_cc: int
    quantidade_cc: int
    avisos: list[str] = field(default_factory=list)


@dataclass
class ProcessamentoLote:
    """Resumo de um lote processado pelo app."""

    arquivos: list[RateioArquivo] = field(default_factory=list)
    erros: list[dict[str, str]] = field(default_factory=list)
