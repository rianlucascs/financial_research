# Pipeline — CVM Formulario de Referencia

Como o dado se move, do download até o relatório.

---

## Fluxo geral

```
extract → to_interim → to_processed → load → compare → retention
```

Cada execução cria um snapshot datado (`YYYY-MM-DD`). O pipeline roda diariamente e mantém os últimos 3 dias no disco.

---

## Stage por stage

### 1. Extract

**Input:** URLs públicas da CVM (um `.zip` por ano, de 2010 até o ano atual).

**O que faz:** Faz o download dos arquivos `.zip` do Formulário de Referência (FRE), descompacta e salva os `.csv` brutos.

**Output:**
```
data/<pipeline>/<YYYY-MM-DD>/raw/zip/   ← arquivos .zip
data/<pipeline>/<YYYY-MM-DD>/raw/csv/   ← arquivos .csv descompactados
```

---

### 2. Transform — to_interim

**Input:** `.csv` em `raw/csv/` (separador `;`, encoding `iso-8859-1`).

**O que faz:** Leitura, padronização de tipos e colunas, limpeza inicial e conversão de datas e campos textuais/cadastrais/financeiros. Um arquivo `.parquet` por ano e por identificador/tabela.

**Output:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_interim/parquet/
```

Ações principais:
- leitura dos CSVs brutos referentes a cada submódulo (ex.: `informacao_financeira`, `capital_social`, `posicao_acionaria`, `administrador`, etc.);
- conversão de campos textuais e identificadores (`CNPJ_CIA`, `CD_CVM`, `DENOM_CIA`, `CPF`, `CNPJ`, etc.) para `string`;
- parse de campos de data (`DT_REFER`, `DT_RECEB`, `DT_INI_EXERC`, `DT_FIM_EXERC`, etc.) para `datetime`.

---

### 3. Transform — to_processed

**Input:** `.parquet` de `to_interim/`.

**O que faz:** Concatena os dados anuais dos arquivos intermediários de cada identificador (tabela) do Formulário de Referência em arquivos Parquet consolidados abrangendo a série histórica de 2010 até o ano atual.

**Output:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_processed/parquet/
```

Exemplo de arquivo gerado:
```
fre_cia_aberta_informacao_financeira_2010-2026.parquet
```

---

### 4. Load

**Input:** `.parquet` de `to_processed/`.

**O que faz:** Grava os dados no destino final (banco de dados ou camada de consumo).

**Output:** destino final configurado no ambiente.

---

### 5. Compare

**Input:** `.parquet` de `to_processed/` do snapshot atual (`D0`) e do anterior (`D-1`).

**O que faz:** Compara os dois snapshots linha a linha por chave composta e gera três conjuntos: linhas adicionadas, removidas e alteradas.

**Output:**
```
data/<pipeline>/<YYYY-MM-DD>/snapshot_drift/<arquivo>/
    <arquivo>_added.parquet
    <arquivo>_removed.parquet
    <arquivo>_changed.parquet
```

---

### 6. Retention

**Input:** `data/<pipeline>/` e `logs/<pipeline>/`.

**O que faz:** Remove snapshots e logs com mais de 3 dias. Mantém apenas `D0`, `D-1` e `D-2`.

**Output:** diretórios antigos deletados; checkpoint gravado.

---

## Chave composta (Compare)

| Coluna | Descrição |
|---|---|
| `CD_CVM` | Código da empresa na CVM |

---

## Observações do fluxo FRE

- O Formulário de Referência (FRE) é um documento anual extenso composto por dezenas de tabelas/módulos temáticos (mais de 60 identificadores).
- O processamento em `to_processed` consolida os recortes anuais por identificador (tabela) em arquivos parquet de séries históricas de longo prazo (de 2010 até o ano corrente).
- Algumas tabelas do FRE possuem anos ausentes na origem da CVM para períodos específicos; o pipeline trata arquivos intermediários inexistentes sem interromper o fluxo das demais tabelas.
