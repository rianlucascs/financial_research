# Pipeline — CVM Cias Abertas Informacao Cadastral

Como o dado se move, do download até o relatório.

---

## Fluxo geral

```
extract → to_interim → load
```

Cada execução cria um snapshot datado (`YYYY-MM-DD`). O pipeline roda diariamente e mantém os últimos 3 dias no disco.

---

## Stage por stage

### 1. Extract

**Input:** URL pública da CVM para o arquivo de cadastro de companhias abertas.

**O que faz:** Faz o download do arquivo CSV `cad_cia_aberta.csv` e salva o dado bruto na estrutura de snapshots.

**Output:**
```
data/<pipeline>/<YYYY-MM-DD>/raw/csv/   ← arquivos .csv
```

---

### 2. Transform — to_interim

**Input:** `.csv` em `raw/csv/` (separador `;`, encoding `iso-8859-1`).

**O que faz:** Leitura, padronização de tipos, conversão de colunas de data e limpeza inicial dos campos cadastrais. O arquivo final é salvo em parquet para uso analítico.

**Output:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_interim/parquet/
```

Ações principais:
- leitura do CSV bruto;
- conversão de campos textuais para `string`;
- parse de datas como `DT_REG`, `DT_CONST`, `DT_CANCEL`, `DT_INI_SIT` e `DT_INI_RESP`;
- preservação de colunas com valores nulos e alertas de data inválida.

---

### 3. Load

**Input:** `.parquet` de `to_interim/`.

**O que faz:** Carrega o dataset em banco SQLite por tabela, com um arquivo `.db` para cada parquet gerado.

**Output:**
```
load/<pipeline>/<YYYY-MM-DD>/
    cad_cia_aberta.db
```

---

## Observações do fluxo CAD

- O pipeline de cadastro não segue o mesmo padrão de demonstrações por conta contábil.
- A unidade principal é a companhia aberta, e não uma linha contábil por período.
- Os dados cadastrais servem como base de referência para identificar empresas, status regulatório, setor, controle acionário e auditor.
- A estrutura é mais orientada a atributos institucionais e de relacionamento corporativo do que a valores financeiros.

---

## Dados principais

Os campos mais relevantes para uso analítico incluem:

- `CNPJ_CIA`: identificador da empresa
- `DENOM_SOCIAL`: nome oficial da companhia
- `CD_CVM`: código da empresa na CVM
- `SIT`: situação atual da empresa
- `SETOR_ATIV`: setor econômico
- `CATEG_REG`: categoria regulatória
- `DT_INI_SIT`: data de início da situação atual
- `TP_MERC`: tipo de mercado
- `AUDITOR`: nome do auditor independente

---

## Chave composta

A base é geralmente identificada por:

| Coluna | Descrição |
|---|---|
| `CNPJ_CIA` | CNPJ da companhia |
| `CD_CVM` | Código da companhia na CVM |
| `DENOM_SOCIAL` | Nome social da companhia |

---

## Observações de qualidade

- O arquivo bruto vem em `;` e encoding `iso-8859-1`.
- Datas inválidas são convertidas para `NaT` para evitar quebra na leitura.
- O dataset é útil como cadastro mestre de emissoras e para cruzamentos analíticos com demais pipelines da CVM.
