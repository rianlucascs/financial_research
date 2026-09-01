# Pipeline - CVM Cias Abertas Informacao Cadastral

Obtém e prepara o cadastro de companhias abertas disponibilizado pela CVM.

---

## Fluxo geral

```
extract → to_interim → load
```

## Execução e snapshots

- Cada execução cria um snapshot datado (`YYYY-MM-DD`).
- O pipeline é executado diariamente e mantém os últimos três dias no disco.

---

## Stages

### 1. Extract

**Entrada:** URL pública da CVM para o arquivo de cadastro de companhias abertas.

**Processamento:** faz download de `cad_cia_aberta.csv` e preserva o arquivo bruto no snapshot.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/raw/csv/   ← arquivos .csv
```

---

### 2. Transform - to_interim

**Entrada:** arquivo CSV em `raw/csv/`, com separador `;` e encoding `iso-8859-1`.

**Processamento:** padroniza tipos, converte datas e faz a limpeza inicial dos campos cadastrais.

**Saída:**
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

**Entrada:** arquivos Parquet de `to_interim/`.

**Processamento:** carrega o dataset em SQLite, com um arquivo `.db` para cada Parquet gerado.

**Saída:**
```
load/<pipeline>/<YYYY-MM-DD>/
    cad_cia_aberta.db
```

---

## Particularidades do pipeline

- O pipeline de cadastro não segue o mesmo padrão de demonstrações por conta contábil.
- A unidade principal é a companhia aberta, e não uma linha contábil por período.
- Os dados cadastrais servem como base de referência para identificar empresas, status regulatório, setor, controle acionário e auditor.
- A estrutura é mais orientada a atributos institucionais e de relacionamento corporativo do que a valores financeiros.

---

## Campos principais

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

## Chaves e identificadores

A base é geralmente identificada por:

| Coluna | Descrição |
|---|---|
| `CNPJ_CIA` | CNPJ da companhia |
| `CD_CVM` | Código da companhia na CVM |
| `DENOM_SOCIAL` | Nome social da companhia |

---

## Qualidade dos dados

- O arquivo bruto vem em `;` e encoding `iso-8859-1`.
- Datas inválidas são convertidas para `NaT` para evitar quebra na leitura.
- O dataset é útil como cadastro mestre de emissoras e para cruzamentos analíticos com demais pipelines da CVM.
