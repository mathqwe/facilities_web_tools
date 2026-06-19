# Facilities Web Tools

Suíte web simples para automações de Facilities envolvendo planilhas.

## Ferramentas da versão 0.4

- **Biztrip / Toptur**: gera rateio a partir de arquivos `.xlsx` de FT ou fatura.
- **Movida**: lê medição `.xlsx` com abas `LOCAÇÃO` e `MULTAS` e gera um rateio separado por fatura.
- **Uber**: lê CSV exportado do Uber for Business e gera rateio por `Código da despesa`.


## Identidade visual

A interface do app segue uma aplicação simples do manual visual Rio Verde:

- Cores principais: verde `#00B388`, verde escuro `#007860`, azul `#05B3CB`, cinza `#333333`.
- Fontes web sugeridas: Inter e Manrope, com fallback para Segoe UI/sans-serif.
- Logos usados no app: `assets/facilities_tools_logo_green.png` e `assets/facilities_tools_logo_gray.png`.

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura

```text
facilities_web_tools/
├─ app.py
├─ requirements.txt
├─ README.md
└─ src/
   └─ rateia_ai/
      ├─ adapters/
      │  ├─ biztrip.py
      │  ├─ movida.py
      │  ├─ uber.py
      │  └─ generico.py
      ├─ config/
      │  └─ mapeamentos_cc.py
      └─ core/
         ├─ modelo.py
         ├─ normalizacao.py
         ├─ rateador.py
         └─ escritor_excel.py
```

## Regras importantes

### Centros de custo

- A coluna `CC DESCRIÇÃO` agora é preenchida pela tabela oficial em `src/rateia_ai/config/mapeamentos_cc.py`.
- O app não usa mais a primeira palavra do texto da fatura como descrição quando o `CC AJUSTADO` já existe na tabela oficial.
- Isso evita descrições antigas ou incorretas vindas do fornecedor, como `KLABIN` ou `BRACELL` em centros que hoje devem aparecer com outra descrição oficial.
- Se surgir um centro de custo novo, inclua o código em `MAPA_DESCRICOES_CC`.


### Movida

- Aba `LOCAÇÃO`: usa `CENTRO DE CUSTO` e `TOTAL FATURA`.
- Aba `MULTAS`: usa `CENTRO DE CUSTO` e `VALOR DA MULTA`.
- Linhas sem centro de custo ficam em branco na base para conferência manual e não entram no total rateado.
- Linhas de total/rodapé são ignoradas para não duplicar o valor.
- Na aba de base gerada, zeros de colunas auxiliares sem cobrança ficam em branco para facilitar conferência visual. A coluna principal do rateio continua preservada.

### Uber

- Usa `Código da despesa` como centro de custo.
- Usa `Valor da transação: BRL` como valor.
- Linhas `Payment` sem CC ficam na base e não entram no rateio.
- Datas do CSV no padrão americano `MM/DD/YYYY` são convertidas para `DD/MM/YYYY` na aba de base gerada.

### Biztrip / Toptur

- Localiza o cabeçalho automaticamente.
- Tenta identificar coluna de valor e coluna de centro de custo pelo nome.
- Se a planilha tiver várias FTs, tenta filtrar pelo número do nome do arquivo.

## Não subir arquivos reais

O repositório deve conter apenas código. Não suba planilhas reais, CSVs de fatura ou dados internos da empresa.
