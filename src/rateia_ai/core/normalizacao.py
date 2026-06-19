from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from src.rateia_ai.config.mapeamentos_cc import MAPA_CC_AJUSTADO, MAPA_CC_TEXTO, MAPA_DESCRICOES_CC


def normalizar_texto(valor: Any) -> str:
    if valor is None:
        return ""
    texto = str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def contem_todos(texto_normalizado: str, termos: tuple[str, ...] | list[str]) -> bool:
    return all(termo in texto_normalizado for termo in termos)


def normalizar_codigo_cc(valor: Any) -> str | None:
    """Normaliza códigos de centro de custo para seis dígitos.

    Trata entradas como 110620, 110620.0, "1.10620", "310140 "
    e aplica exceções de MAPA_CC_AJUSTADO quando houver.
    """
    if valor is None:
        return None
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    texto = str(valor).strip()
    if not texto or texto == "--":
        return None
    digitos = re.sub(r"\D", "", texto)
    if len(digitos) < 6:
        return None
    cc = digitos[-6:] if len(digitos) == 7 and digitos.startswith("1") else digitos[:6]
    return MAPA_CC_AJUSTADO.get(cc, cc)


def para_decimal(valor: Any) -> Decimal:
    """Converte valores BR/US para Decimal.

    Aceita formatos como 1.234,56, 1234.56, R$ 1.234,56, número nativo do Excel
    e também os pontos usados no CSV da Uber.
    """
    if valor is None or valor == "" or valor == "--":
        return Decimal("0.00")
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, bool):
        return Decimal("0.00")
    if isinstance(valor, int):
        return Decimal(valor)
    if isinstance(valor, float):
        return Decimal(str(valor))

    texto = str(valor).strip()
    if not texto or texto == "--":
        return Decimal("0.00")

    negativo_parenteses = texto.startswith("(") and texto.endswith(")")
    texto = texto.replace("R$", "")
    texto = re.sub(r"[^0-9,\.\-]", "", texto)

    if texto.count(",") and texto.count("."):
        # O último separador costuma ser o decimal.
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    if negativo_parenteses:
        texto = "-" + texto.lstrip("-")

    try:
        return Decimal(texto)
    except InvalidOperation:
        return Decimal("0.00")


def decimal_moeda(valor: Decimal) -> Decimal:
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def formatar_moeda_br(valor: Decimal) -> str:
    valor = decimal_moeda(valor)
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def extrair_cc_de_texto(valor: Any) -> str | None:
    """Extrai um centro de custo de um texto.

    Exemplos:
    - "1.10622 - GE AEROSPACE" -> "110622"
    - "110620 - VALMET" -> "110620"
    - "valmet" -> "110620" via mapeamento textual
    - vazio -> None
    """
    if valor is None:
        return None
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    texto_original = str(valor).strip()
    if not texto_original or texto_original == "--":
        return None

    texto_norm = normalizar_texto(texto_original)
    if texto_norm in MAPA_CC_TEXTO:
        return MAPA_CC_TEXTO[texto_norm]

    # Procura padrões com pontuação/espaços: 1.10622, 110.622, 110620 etc.
    candidatos = re.findall(r"\d[\d\.\-\s/]{4,}\d", texto_original)
    for candidato in candidatos:
        cc = normalizar_codigo_cc(candidato)
        if cc:
            return cc

    cc = normalizar_codigo_cc(texto_original)
    if cc:
        return cc

    # Procura palavras-chave dentro do texto, sem exigir match exato.
    for chave, cc in MAPA_CC_TEXTO.items():
        chave_norm = normalizar_texto(chave)
        if chave_norm and chave_norm in texto_norm:
            return cc
    return None


def descricao_por_cc_ou_texto(cc: str | None, texto: Any = None) -> str | None:
    """Retorna a descrição oficial do CC, evitando adivinhar pela fatura.

    Prioridade:
    1. Se o CC AJUSTADO existir na tabela oficial, usa a descrição oficial.
    2. Se não houver CC, tenta mapear textos oficiais conhecidos.
    3. Se nada bater, retorna vazio.

    Antes existia um fallback que pegava a primeira palavra do texto da fatura.
    Isso causava descrições erradas como KLABIN/BRACELL quando o CC oficial
    da tabela atual já era outro.
    """
    cc_norm = normalizar_codigo_cc(cc) if cc else None
    if cc_norm and cc_norm in MAPA_DESCRICOES_CC:
        return MAPA_DESCRICOES_CC[cc_norm]
    if texto is None:
        return None
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return None
    for chave, mapped_cc in MAPA_CC_TEXTO.items():
        if normalizar_texto(chave) in texto_norm and mapped_cc in MAPA_DESCRICOES_CC:
            return MAPA_DESCRICOES_CC[mapped_cc]
    return None


def limpar_identificador(valor: Any, tamanho_minimo: int = 3) -> str | None:
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    match = re.search(rf"\d{{{tamanho_minimo},}}", texto)
    if match:
        return match.group(0)
    return None


def identificador_de_nome_arquivo(caminho: Path) -> str:
    """Cria identificador para o arquivo de saída.

    Para Uber, pega os 10 primeiros caracteres alfanuméricos do nome do CSV,
    imitando os exemplos: b2dec9c9-32... -> B2DEC9C932.
    Para arquivos com fatura/FT, pega o primeiro bloco numérico de 3+ dígitos.
    """
    stem = caminho.stem
    numero = limpar_identificador(stem, 3)
    if numero:
        return numero
    alnum = re.sub(r"[^A-Za-z0-9]", "", stem).upper()
    return alnum[:10] if alnum else "SEM_ID"


def nome_seguro_rateio(identificador: str) -> str:
    texto = re.sub(r"[^A-Za-z0-9_\-]", "_", str(identificador).strip().upper())
    texto = re.sub(r"_+", "_", texto).strip("_")
    return texto or "SEM_ID"
