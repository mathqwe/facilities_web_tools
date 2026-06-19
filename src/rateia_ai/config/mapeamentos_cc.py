"""
Mapeamentos oficiais e manuais de centros de custo.

Este arquivo concentra os de/para usados por todos os módulos do app.

A regra principal é a seguinte: quando o CC AJUSTADO for conhecido, a coluna
CC DESCRIÇÃO consulta a tabela oficial abaixo, e não do texto livre da fatura.
Isso evita casos como o fornecedor enviar descrições antigas ou incorretas

-> É necessário atualização manual dessa tabela quando houver mudanças oficiais de CC, para garantir que as descrições fiquem corretas.

"""
# Quando o arquivo vem com um CC, mas o rateio correto deveria cair em outro.
MAPA_CC_AJUSTADO = {
    "120103": "110622",  # Forçando a utilizar o cc novo da GE MRO
}

# Descrição por centro de custo.
MAPA_DESCRICOES_CC = {
    "110620": "VALMET",
    "110621": "NOURYON",
    "110622": "GE MRO",
    "110612": "KOMATSU",
    "310175": "GESTÃO DE TERCEIROS",
    "310170": "ACELERE RH",
    "310168": "PROJETOS",
    "310166": "MARKETING",
    "310163": "DIR. CONTRATO - EA",
    "310143": "SSMA",
    "310142": "QUALIDADE",
    "310140": "FACILITIES",
    "310139": "FISCAL - TAX",
    "310138": "CONTABILIDADE",
    "310137": "FINANCEIRO",
    "310136": "CONTRATOS",
    "310135": "JURIDICO",
    "310134": "TI",
    "310133": "RH/DHO",
    "310129": "RELAÇÕES INSTITUCIONAIS",
    "310123": "ASSISTÊNCIA TÉCNICA",
    "310122": "SUPRIMENTOS",
    "310118": "DIR. DE CONTRATO - RT",
    "310117": "DIR. DE CONTRATO - JL",
    "310116": "DIR. CONTRATO - JR",
    "310113": "PROPOSTAS ORCAMENTOS",
    "310107": "INCORPORAÇÃO",
    "110619": "NOVO NORDISK",
    "110618": "BRAINFARMA CIVIL",
    "110617": "ADAMI",
    "110616": "ACHE",
    "110615": "CS INFRA",
    "110614": "DAIICHI SANKYO",
    "110611": "HEINEKEN",
    "510101": "PRESIDÊNCIA",
    "410102": "COMERCIAL CORPORATIVO"
}

# Quando o campo vem como texto em vez de número.
# Deixamos somente descrições oficiais e exceções conhecidas. Se o texto não bater, o campo ficará em branco
MAPA_CC_TEXTO = {
    "valmet": "110620",
    "valmet arauco": "110620",
    "nouryon": "110621",
    "ge mro": "110622",
    "ge aerospace mro": "110622",
    "komatsu": "110612",
    "gestao de terceiros": "310175",
    "gestão de terceiros": "310175",
    "acelere rh": "310170",
    "projetos": "310168",
    "marketing": "310166",
    "dir contrato ea": "310163",
    "diretoria contrato ea": "310163",
    "ssma": "310143",
    "qualidade": "310142",
    "facilities": "310140",
    "fiscal tax": "310139",
    "contabilidade": "310138",
    "financeiro": "310137",
    "contratos": "310136",
    "juridico": "310135",
    "jurídico": "310135",
    "ti": "310134",
    "rh dho": "310133",
    "relacoes institucionais": "310129",
    "relações institucionais": "310129",
    "assistencia tecnica": "310123",
    "assistência técnica": "310123",
    "suprimentos": "310122",
    "dir de contrato rt": "310118",
    "dir de contrato jl": "310117",
    "dir contrato jr": "310116",
    "propostas orcamentos": "310113",
    "propostas orçamentos": "310113",
    "incorporacao": "310107",
    "incorporação": "310107",
    "novo nordisk": "110619",
    "brainfarma civil": "110618",
    "adami": "110617",
    "ache": "110616",
    "aché": "110616",
    "cs infra": "110615",
    "daiichi sankyo": "110614",
    "heineken": "110611",
    "presidencia": "510101",
    "presidência": "510101",
    "comercial corporativo": "410102",
}
