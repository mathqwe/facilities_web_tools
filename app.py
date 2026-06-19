from __future__ import annotations

import base64
import io
import tempfile
import zipfile
from decimal import Decimal
from pathlib import Path

import pandas as pd
import streamlit as st

from src.rateia_ai.adapters import biztrip, movida, uber
from src.rateia_ai.core.modelo import RateioArquivo
from src.rateia_ai.core.normalizacao import formatar_moeda_br


APP_DIR = Path(__file__).resolve().parent
ASSETS_DIR = APP_DIR / "assets"
LOGO_VERDE = ASSETS_DIR / "facilities_tools_logo_green.png"
LOGO_CINZA = ASSETS_DIR / "facilities_tools_logo_gray.png"


def _resultado_para_dict(resultado: RateioArquivo) -> dict:
    return {
        "fornecedor": resultado.fornecedor,
        "subtipo": resultado.subtipo,
        "arquivo_origem": resultado.arquivo_origem,
        "identificador": resultado.identificador,
        "nome_saida": resultado.nome_saida,
        "total_rateado": str(resultado.total_rateado),
        "total_rateado_formatado": formatar_moeda_br(resultado.total_rateado),
        "total_arquivo": str(resultado.total_arquivo),
        "total_arquivo_formatado": formatar_moeda_br(resultado.total_arquivo),
        "valor_sem_cc": str(resultado.valor_sem_cc),
        "valor_sem_cc_formatado": formatar_moeda_br(resultado.valor_sem_cc),
        "linhas_processadas": resultado.linhas_processadas,
        "linhas_rateadas": resultado.linhas_rateadas,
        "linhas_sem_cc": resultado.linhas_sem_cc,
        "quantidade_cc": resultado.quantidade_cc,
        "avisos": resultado.avisos,
        "bytes": resultado.arquivo_saida.read_bytes(),
    }


def _imagem_base64(caminho: Path) -> str:
    if not caminho.exists():
        return ""
    return base64.b64encode(caminho.read_bytes()).decode("utf-8")


st.set_page_config(
    page_title="Facilities Web Tools",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

logo_verde_b64 = _imagem_base64(LOGO_VERDE)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Manrope:wght@600;700;800&display=swap');

    :root {
        --rv-green: #00B388;
        --rv-green-dark: #007860;
        --rv-green-deep: #006954;
        --rv-blue: #05B3CB;
        --rv-blue-deep: #0047BB;
        --rv-gray: #333333;
        --rv-gray-soft: #777777;
        --rv-yellow: #E1E000;
        --rv-bg: #F7FBFA;
        --rv-card: #FFFFFF;
        --rv-line: rgba(0, 120, 96, 0.18);
        --rv-shadow: 0 16px 45px rgba(0, 105, 84, 0.10);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Montserrat', 'Segoe UI', sans-serif;
        color: var(--rv-gray);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(0, 179, 136, 0.11), transparent 34rem),
            linear-gradient(180deg, #FFFFFF 0%, var(--rv-bg) 100%);
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1180px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F4FAF8 100%);
        border-right: 1px solid var(--rv-line);
    }

    .rv-hero {
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        gap: 1.25rem;
        padding: 1.45rem 1.55rem;
        border: 1px solid var(--rv-line);
        border-radius: 24px;
        background:
            linear-gradient(135deg, rgba(0,179,136,0.13), rgba(5,179,203,0.07) 52%, rgba(255,255,255,0.94)),
            #FFFFFF;
        box-shadow: var(--rv-shadow);
        margin-bottom: 1.2rem;
    }

    .rv-hero:after {
        content: "";
        position: absolute;
        right: -5rem;
        bottom: -6rem;
        width: 18rem;
        height: 18rem;
        border-radius: 50%;
        background: rgba(0, 179, 136, 0.10);
    }

    .rv-logo-wrap {
        z-index: 1;
        min-width: 86px;
        width: 86px;
        height: 86px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 22px;
        background: rgba(255,255,255,0.86);
        border: 1px solid rgba(0,120,96,0.12);
    }

    .rv-logo-wrap img {
        max-width: 72px;
        max-height: 72px;
        object-fit: contain;
    }

    .rv-hero-content {
        z-index: 1;
    }

    .rv-kicker {
        margin-bottom: .28rem;
        color: var(--rv-green-dark);
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .11em;
        text-transform: uppercase;
    }

    .rv-hero h1 {
        margin: 0;
        font-family: 'Manrope', 'Inter', sans-serif;
        color: var(--rv-gray);
        font-weight: 800;
        font-size: clamp(2rem, 4vw, 3rem);
        line-height: 1.02;
    }

    .rv-hero p {
        margin: .45rem 0 0 0;
        max-width: 720px;
        color: rgba(51,51,51,0.76);
        font-size: 1.02rem;
    }

    .rv-strip {
        width: 54px;
        height: 6px;
        border-radius: 99px;
        background: linear-gradient(90deg, var(--rv-green), var(--rv-blue-deep));
        margin: .85rem 0 0 0;
    }

    .rv-section-card {
        padding: 1.1rem 1.25rem;
        border: 1px solid var(--rv-line);
        border-radius: 18px;
        background: rgba(255,255,255,0.88);
        box-shadow: 0 10px 28px rgba(0, 105, 84, 0.06);
        margin: 1rem 0;
    }

    .rv-section-card h3 {
        margin: 0 0 .3rem 0;
        font-family: 'Manrope', 'Inter', sans-serif;
        color: var(--rv-green-deep);
        font-size: 1.18rem;
    }

    .rv-muted {
        color: rgba(51,51,51,0.66);
        font-size: .94rem;
    }

    div[role="radiogroup"] {
        gap: .75rem;
    }

    div[role="radiogroup"] label {
        min-height: 4rem;
        padding: .85rem 1rem !important;
        border: 1px solid rgba(0,120,96,0.18) !important;
        border-radius: 16px !important;
        background: #FFFFFF !important;
        box-shadow: 0 8px 20px rgba(0,105,84,0.06);
    }

    div[role="radiogroup"] label:hover {
        border-color: var(--rv-green) !important;
        box-shadow: 0 10px 24px rgba(0,179,136,0.14);
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 13px !important;
        font-weight: 700 !important;
        border: 1px solid rgba(0,120,96,0.18) !important;
    }

    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--rv-green), var(--rv-green-dark)) !important;
        color: white !important;
        border: none !important;
    }

    [data-testid="stFileUploader"] section {
        border: 1.5px dashed rgba(0,120,96,0.35) !important;
        border-radius: 18px !important;
        background: rgba(255,255,255,0.76) !important;
    }

    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(0,120,96,0.14);
        border-radius: 16px;
        padding: .75rem .9rem;
    }

    .rv-footer {
        margin-top: 1.5rem;
        padding-top: .9rem;
        border-top: 1px solid var(--rv-line);
        color: rgba(51,51,51,0.58);
        font-size: .88rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

logo_html = (
    f'<img src="data:image/png;base64,{logo_verde_b64}" alt="Facilities Web Tools">'
    if logo_verde_b64
    else "🛠️"
)

st.markdown(
    f"""
    <div class="rv-hero">
      <div class="rv-logo-wrap">{logo_html}</div>
      <div class="rv-hero-content">
        <div class="rv-kicker">Rio Verde · Facilities</div>
        <h1>Facilities Web Tools</h1>
        <p>Suíte simples para automatizar rateios e pequenos processos com planilhas.</p>
        <div class="rv-strip"></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

TIPOS = {
    "Biztrip / Toptur": {
        "titulo": "Biztrip / Toptur - FT ou Fatura (.xlsx)",
        "extensoes": ["xlsx"],
        "help": "Use para arquivos PLANILHA FT, FATURA ou planilhas exportadas da Biztrip/Toptur.",
        "processor": biztrip.processar,
    },
    "Movida": {
        "titulo": "Movida - Medição com abas LOCAÇÃO e MULTAS (.xlsx)",
        "extensoes": ["xlsx"],
        "help": "Use para medição da Movida. O app gera um rateio para LOCAÇÃO e outro para MULTAS quando existirem dados.",
        "processor": movida.processar,
    },
    "Uber": {
        "titulo": "Uber - CSV de transações (.csv)",
        "extensoes": ["csv"],
        "help": "Use para CSV exportado do Uber for Business.",
        "processor": uber.processar,
    },
}

with st.sidebar:
    if LOGO_CINZA.exists():
        st.image(str(LOGO_CINZA), width=112)
    st.markdown("### Facilities Web Tools")
    st.caption("Rateio de custos para Facilities usando planilhas.")
    st.divider()
    st.markdown("**Ferramentas disponíveis**")
    st.markdown("- Biztrip / Toptur\n- Movida\n- Uber")
    st.divider()
    st.caption("Versão 0.4 · Processamento temporário na sessão do app")

st.markdown(
    """
    <div class="rv-section-card">
      <h3>1. Escolha o tipo de rateio</h3>
      <span class="rv-muted">Selecione a origem do arquivo para aplicar a regra correta de processamento.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

tipo_escolhido = st.radio(
    "Tipo de rateio",
    list(TIPOS.keys()),
    horizontal=True,
    label_visibility="collapsed",
)
config_tipo = TIPOS[tipo_escolhido]
st.caption(config_tipo["help"])
st.subheader(config_tipo["titulo"])

with st.expander("Como usar", expanded=False):
    if tipo_escolhido == "Movida":
        st.markdown(
            """
            1. Envie o arquivo `.xlsx` de medição da Movida.
            2. O script procura as abas **LOCAÇÃO** e **MULTAS**.
            3. Para **LOCAÇÃO**, usa **CENTRO DE CUSTO** + **TOTAL FATURA**.
            4. Para **MULTAS**, usa **CENTRO DE CUSTO** + **VALOR DA MULTA**.
            5. Linhas sem centro de custo ficam **em branco na base** para conferência manual e **não entram no total rateado**.
            """
        )
    elif tipo_escolhido == "Uber":
        st.markdown(
            """
            1. Envie o CSV do Uber for Business.
            2. O app localiza a tabela de transações dentro do CSV.
            3. Usa **Código da despesa** como CC e **Valor da transação: BRL** como valor.
            4. Linhas sem CC, como **Payment**, ficam na aba BASE, mas não entram no RATEIO.
            """
        )
    else:
        st.markdown(
            """
            1. Envie arquivos `.xlsx` de FT/Fatura da Biztrip/Toptur.
            2. O app localiza cabeçalho, centro de custo, valor e número da fatura/FT.
            3. Se uma planilha tiver várias FTs, o app filtra pelo número do arquivo quando possível.
            """
        )

st.markdown(
    """
    <div class="rv-section-card">
      <h3>2. Envie os arquivos</h3>
      <span class="rv-muted">Os arquivos são processados apenas temporariamente na sessão do app.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Arraste ou selecione os arquivos",
    type=config_tipo["extensoes"],
    accept_multiple_files=True,
    help="Você pode enviar vários arquivos de uma vez.",
)

identificador_uber = None
if tipo_escolhido == "Uber":
    identificador_uber = st.text_input(
        "Identificador manual para o nome do arquivo de saída (opcional)",
        placeholder="Ex.: UBER_MAIO_2026. Se ficar vazio, uso o ID do nome do CSV.",
    ).strip() or None

col_acao, col_limpar = st.columns([1, 1])
with col_acao:
    gerar = st.button("Gerar rateio", type="primary", use_container_width=True, disabled=not uploaded_files)
with col_limpar:
    limpar = st.button("Limpar resultados", use_container_width=True)

if limpar:
    st.session_state.pop("resultados_facilities", None)
    st.rerun()

if gerar and uploaded_files:
    sucessos: list[dict] = []
    erros: list[dict[str, str]] = []
    processor = config_tipo["processor"]

    with st.spinner("Processando arquivos..."):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            entrada_dir = tmp / "entrada"
            saida_dir = tmp / "saida"
            entrada_dir.mkdir(parents=True, exist_ok=True)
            saida_dir.mkdir(parents=True, exist_ok=True)

            for arquivo in uploaded_files:
                caminho_entrada = entrada_dir / arquivo.name
                caminho_entrada.write_bytes(arquivo.getbuffer())
                try:
                    if processor is uber.processar:
                        resultados = processor(caminho_entrada, saida_dir, overwrite=True, identificador_manual=identificador_uber)
                    else:
                        resultados = processor(caminho_entrada, saida_dir, overwrite=True)
                    for resultado in resultados:
                        sucessos.append(_resultado_para_dict(resultado))
                except Exception as exc:
                    erros.append({"arquivo": arquivo.name, "erro": str(exc)})

    st.session_state["resultados_facilities"] = {"sucessos": sucessos, "erros": erros, "tipo": tipo_escolhido}
    st.rerun()


def _exibir_resultados(sucessos: list[dict], erros: list[dict[str, str]]) -> None:
    if sucessos:
        st.success(f"{len(sucessos)} arquivo(s) de rateio gerado(s) com sucesso.")
        total_rateado = sum(Decimal(item["total_rateado"]) for item in sucessos)
        total_sem_cc = sum(Decimal(item["valor_sem_cc"]) for item in sucessos)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rateios gerados", len(sucessos))
        c2.metric("Total rateado", formatar_moeda_br(total_rateado))
        c3.metric("Valor sem CC", formatar_moeda_br(total_sem_cc))
        c4.metric("Linhas sem CC", sum(item["linhas_sem_cc"] for item in sucessos))

        tabela = pd.DataFrame(
            [
                {
                    "Fornecedor": item["fornecedor"],
                    "Tipo": item["subtipo"],
                    "Origem": item["arquivo_origem"],
                    "Gerado": item["nome_saida"],
                    "ID/Fatura": item["identificador"],
                    "Total rateado": item["total_rateado_formatado"],
                    "Valor sem CC": item["valor_sem_cc_formatado"],
                    "CCs": item["quantidade_cc"],
                    "Linhas sem CC": item["linhas_sem_cc"],
                }
                for item in sucessos
            ]
        )
        st.dataframe(tabela, use_container_width=True, hide_index=True)

        if any(item["avisos"] for item in sucessos):
            st.warning("Alguns arquivos foram processados com avisos. Confira antes de usar o rateio final.")
            for item in sucessos:
                for aviso in item["avisos"]:
                    st.markdown(f"- **{item['nome_saida']}**: {aviso}")

        st.subheader("Downloads")
        for item in sucessos:
            with st.container(border=True):
                st.markdown(f"**{item['nome_saida']}**")
                st.markdown(
                    f"<span class='rv-muted'>Origem: {item['arquivo_origem']} · Total rateado: {item['total_rateado_formatado']}</span>",
                    unsafe_allow_html=True,
                )
                st.download_button(
                    label="Baixar Excel",
                    data=item["bytes"],
                    file_name=item["nome_saida"],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_{item['nome_saida']}",
                    use_container_width=True,
                )

        if len(sucessos) > 1:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for item in sucessos:
                    zipf.writestr(item["nome_saida"], item["bytes"])
            st.download_button(
                label="Baixar todos em ZIP",
                data=zip_buffer.getvalue(),
                file_name="rateios_gerados.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True,
            )

    if erros:
        st.error(f"{len(erros)} arquivo(s) não foram processados.")
        for erro in erros:
            st.markdown(f"- **{erro['arquivo']}**: {erro['erro']}")


estado = st.session_state.get("resultados_facilities")
if estado:
    _exibir_resultados(estado.get("sucessos", []), estado.get("erros", []))
else:
    st.info("Selecione uma ferramenta, envie os arquivos e clique em **Gerar rateio**.")

st.markdown(
    """
    <div class="rv-footer">
      Os arquivos são processados temporariamente na sessão do app. Não suba planilhas reais para o GitHub.
    </div>
    """,
    unsafe_allow_html=True,
)
