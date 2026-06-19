from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
import re

from src.rateia_ai.core.escritor_excel import criar_workbook_rateio
from src.rateia_ai.core.modelo import ErroRateio, LinhaRateio, RateioArquivo
from src.rateia_ai.core.normalizacao import (
    decimal_moeda,
    descricao_por_cc_ou_texto,
    extrair_cc_de_texto,
    formatar_moeda_br,
    nome_seguro_rateio,
    normalizar_texto,
    para_decimal,
)
from src.rateia_ai.core.rateador import somar_por_cc


def _ler_csv(caminho: Path) -> tuple[list[str], list[list[str]]]:
    with caminho.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))
    header_idx = None
    for idx, row in enumerate(rows):
        if row and normalizar_texto(row[0]) == "id da viagem uber eats":
            header_idx = idx
            break
    if header_idx is None:
        raise ErroRateio("Não encontrei o cabeçalho do CSV da Uber: ID da viagem/Uber Eats.")
    header = rows[header_idx]
    data = rows[header_idx + 1 :]
    return header, data


def _coluna(headers: list[str], nome: str, alternativas: list[str] | None = None) -> int:
    nomes = [nome] + (alternativas or [])
    nomes_norm = [normalizar_texto(n) for n in nomes]
    for idx, h in enumerate(headers):
        if normalizar_texto(h) in nomes_norm:
            return idx
    raise ErroRateio(f"Não encontrei a coluna obrigatória no CSV da Uber: {nome}")



def _identificador_uber(caminho: Path) -> str:
    # O nome do CSV da Uber normalmente começa com um UUID. Os rateios manuais
    # usam os 10 primeiros caracteres alfanuméricos: b2dec9c9-32... -> B2DEC9C932.
    alnum = re.sub(r"[^A-Za-z0-9]", "", caminho.stem).upper()
    return alnum[:10] if alnum else "UBER"


def _formatar_data_uber(valor: Any) -> Any:
    """Converte datas do CSV Uber para padrão brasileiro.

    O CSV vem no padrão americano MM/DD/YYYY. Se for gravado assim no Excel,
    04/01/2026 parece 04/01 para nós, mas na verdade significa 01/04/2026.
    Mantemos como texto em DD/MM/YYYY para evitar interpretação incorreta.
    """
    if valor in (None, "", "--"):
        return valor
    texto = str(valor).strip()
    formatos = (
        ("%m/%d/%Y", "%d/%m/%Y"),
        ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"),
        ("%Y-%m-%d", "%d/%m/%Y"),
    )
    for entrada, saida in formatos:
        try:
            return datetime.strptime(texto, entrada).strftime(saida)
        except ValueError:
            continue
    return valor


def _eh_coluna_data_uber(header: Any) -> bool:
    h = normalizar_texto(header)
    return "data" in h


def _corrigir_datas_base(headers: list[str], row: list[Any]) -> list[Any]:
    corrigida = list(row)
    for idx, header in enumerate(headers):
        if idx < len(corrigida) and _eh_coluna_data_uber(header):
            corrigida[idx] = _formatar_data_uber(corrigida[idx])
    return corrigida


def processar(caminho_entrada: Path, pasta_saida: Path, overwrite: bool = True, identificador_manual: str | None = None) -> list[RateioArquivo]:
    caminho_entrada = Path(caminho_entrada)
    if caminho_entrada.suffix.lower() != ".csv":
        raise ErroRateio("Uber aceita apenas arquivos .csv exportados do portal.")

    headers, rows = _ler_csv(caminho_entrada)
    col_cc = _coluna(headers, "Código da despesa")
    col_valor = _coluna(headers, "Valor da transação: BRL", ["Valor da transação (moeda local)", "Valor total: BRL"])
    col_tipo = _coluna(headers, "Tipo de transação")
    col_detalhe = _coluna(headers, "Detalhamento da despesa")

    linhas: list[LinhaRateio] = []
    dados_base: list[list[Any]] = []
    total_arquivo = Decimal("0.00")
    valor_sem_cc = Decimal("0.00")
    linhas_sem_cc = 0
    linhas_payment_ignoradas = 0

    for row in rows:
        if not any(cell not in (None, "") for cell in row):
            continue
        if len(row) < len(headers):
            row = row + [""] * (len(headers) - len(row))
        else:
            row = row[: len(headers)]

        valor = para_decimal(row[col_valor])
        cc_original = row[col_cc]
        tipo_transacao = row[col_tipo]
        cc = extrair_cc_de_texto(cc_original)
        descricao = descricao_por_cc_ou_texto(cc, cc_original)
        total_arquivo += decimal_moeda(valor)

        incluir = cc is not None and valor != Decimal("0.00")
        motivo = None
        if not cc and valor != Decimal("0.00"):
            linhas_sem_cc += 1
            valor_sem_cc += decimal_moeda(valor)
            motivo = "SEM CC"
            if normalizar_texto(tipo_transacao) == "payment":
                linhas_payment_ignoradas += 1
                motivo = "PAYMENT SEM CC"

        row_base = _corrigir_datas_base(headers, row)

        linha = LinhaRateio(
            cc_original=cc_original,
            cc_ajustado=cc,
            cc_descricao=descricao,
            valor=valor,
            dados={str(headers[i] or f"COLUNA_{i+1}"): row[i] for i in range(len(headers))},
            incluir_no_rateio=incluir,
            motivo_ignorado=motivo,
        )
        linhas.append(linha)
        dados_base.append(row_base + [int(cc) if cc and cc.isdigit() else cc, descricao, motivo])

    if not linhas:
        raise ErroRateio("CSV da Uber sem linhas processáveis.")

    identificador = nome_seguro_rateio(identificador_manual or _identificador_uber(caminho_entrada))
    nome_saida = f"RATEIO_{identificador}.xlsx"
    caminho_saida = pasta_saida / nome_saida
    if caminho_saida.exists() and not overwrite:
        base = caminho_saida.with_suffix("")
        contador = 2
        while caminho_saida.exists():
            caminho_saida = base.with_name(f"{base.name}_{contador}").with_suffix(".xlsx")
            contador += 1
        nome_saida = caminho_saida.name

    totais = somar_por_cc(linhas)
    criar_workbook_rateio(
        caminho_saida=caminho_saida,
        titulo_rateio=f"RATEIO {identificador}",
        nome_aba_base="BASE",
        headers_base=headers + ["CC AJUSTADO", "CC DESCRIÇÃO", "MOTIVO IGNORADO"],
        linhas_base=dados_base,
        totais=totais,
    )

    avisos: list[str] = []
    if linhas_sem_cc:
        avisos.append(
            f"{linhas_sem_cc} linha(s) com valor ficaram sem CC e não entraram no rateio "
            f"({formatar_moeda_br(valor_sem_cc)})."
        )
    if linhas_payment_ignoradas:
        avisos.append(f"{linhas_payment_ignoradas} linha(s) Payment sem CC foram mantidas na BASE, mas ignoradas no RATEIO.")

    total_rateado = sum(totais.values(), Decimal("0.00"))
    return [
        RateioArquivo(
            fornecedor="Uber",
            subtipo="CSV",
            arquivo_origem=caminho_entrada.name,
            identificador=identificador,
            nome_saida=nome_saida,
            arquivo_saida=caminho_saida,
            total_rateado=decimal_moeda(total_rateado),
            total_arquivo=decimal_moeda(total_arquivo),
            valor_sem_cc=decimal_moeda(valor_sem_cc),
            linhas_processadas=len(linhas),
            linhas_rateadas=sum(1 for l in linhas if l.incluir_no_rateio and l.cc_ajustado),
            linhas_sem_cc=linhas_sem_cc,
            quantidade_cc=len(totais),
            avisos=avisos,
        )
    ]
