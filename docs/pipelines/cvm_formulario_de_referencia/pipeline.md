# Pipeline - CVM Formulario de Referencia

Obtém e prepara os dados do Formulário de Referência (FRE) da CVM.

---

## Fluxo geral

```
extract → to_interim → to_processed → load → compare → retention
```

## Execução e snapshots

- Cada execução cria um snapshot datado (`YYYY-MM-DD`).
- O pipeline é executado diariamente e mantém os últimos três dias no disco.

---

## Stages

### 1. Extract

**Entrada:** URLs públicas da CVM (um `.zip` por ano, de 2010 até o ano atual).

**Processamento:** Faz o download dos arquivos `.zip` do Formulário de Referência (FRE), descompacta e salva os `.csv` brutos.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/raw/zip/   ← arquivos .zip
data/<pipeline>/<YYYY-MM-DD>/raw/csv/   ← arquivos .csv descompactados
```

---

### 2. Transform - to_interim

**Entrada:** `.csv` em `raw/csv/` (separador `;`, encoding `iso-8859-1`).

**Processamento:** Leitura, padronização de tipos e colunas, limpeza inicial e conversão de datas e campos textuais/cadastrais/financeiros. Um arquivo `.parquet` por ano e por identificador/tabela.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_interim/parquet/
```

Ações principais:
- leitura dos CSVs brutos referentes a cada submódulo (ex.: `informacao_financeira`, `capital_social`, `posicao_acionaria`, `administrador`, etc.);
- conversão de campos textuais e identificadores (`CNPJ_CIA`, `CD_CVM`, `DENOM_CIA`, `CPF`, `CNPJ`, etc.) para `string`;
- parse de campos de data (`DT_REFER`, `DT_RECEB`, `DT_INI_EXERC`, `DT_FIM_EXERC`, etc.) para `datetime`.

---

### 3. Transform - to_processed

**Entrada:** `.parquet` de `to_interim/`.

**Processamento:** Concatena os dados anuais dos arquivos intermediários de cada identificador (tabela) do Formulário de Referência em arquivos Parquet consolidados abrangendo a série histórica de 2010 até o ano atual.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_processed/parquet/
```

Exemplo de arquivo gerado:
```
fre_cia_aberta_informacao_financeira_2010-2026.parquet
```

---

### 4. Load

**Entrada:** `.parquet` de `to_processed/`.

**Processamento:** Grava os dados no destino final (banco de dados ou camada de consumo).

**Saída:** destino final configurado no ambiente.

---

### 5. Compare

**Entrada:** `.parquet` de `to_processed/` do snapshot atual (`D0`) e do anterior (`D-1`).

**Processamento:** Compara os dois snapshots linha a linha por chave composta e gera três conjuntos: linhas adicionadas, removidas e alteradas.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/snapshot_drift/<arquivo>/
    <arquivo>_added.parquet
    <arquivo>_removed.parquet
    <arquivo>_changed.parquet
```

---

### 6. Retention

**Entrada:** `data/<pipeline>/` e `logs/<pipeline>/`.

**Processamento:** Remove snapshots e logs com mais de 3 dias. Mantém apenas `D0`, `D-1` e `D-2`.

**Saída:** diretórios antigos deletados; checkpoint gravado.

---

## Chaves de comparação

| Coluna | Descrição |
|---|---|
| `CD_CVM` | Código da empresa na CVM |

---

## Particularidades do pipeline

- O Formulário de Referência (FRE) é um documento anual extenso composto por dezenas de tabelas/módulos temáticos (mais de 60 identificadores).
- O processamento em `to_processed` consolida os recortes anuais por identificador (tabela) em arquivos parquet de séries históricas de longo prazo (de 2010 até o ano corrente).
- Algumas tabelas do FRE possuem anos ausentes na origem da CVM para períodos específicos; o pipeline trata arquivos intermediários inexistentes sem interromper o fluxo das demais tabelas.

## Qualidade dos dados

- [detalhar: falta informação sobre validações e tratamento de dados inválidos].
