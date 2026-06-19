# Facilities Web Tools

Suíte web simples para automações de Facilities envolvendo planilhas.

## Ferramentas da versão 0.4

- **Biztrip / Toptur**: gera rateio a partir de arquivos `.xlsx` de FT ou fatura.
- **Movida**: lê medição `.xlsx` com abas `LOCAÇÃO` e `MULTAS` e gera um rateio separado por fatura.
- **Uber**: lê CSV exportado do Uber for Business e gera rateio por `Código da despesa`.


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
