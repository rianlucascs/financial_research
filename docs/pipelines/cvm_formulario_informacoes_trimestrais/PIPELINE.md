# Pipeline — CVM Formulario Informacoes Trimestrais

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

**Input:** URLs públicas da CVM (um `.zip` por ano, de 2011 até o ano atual).

**O que faz:** Faz o download dos arquivos `.zip` do formulário ITR, descompacta e salva os `.csv` brutos.

**Output:**
```
data/<pipeline>/<YYYY-MM-DD>/raw/zip/   ← arquivos .zip
data/<pipeline>/<YYYY-MM-DD>/raw/csv/   ← arquivos .csv descompactados
```

---

### 2. Transform — to_interim

**Input:** `.csv` em `raw/csv/` (separador `;`, encoding `iso-8859-1`).

**O que faz:** Leitura, padronização de tipos e colunas, limpeza inicial e conversão de datas e valores numéricos. Um arquivo `.parquet` por ano e por arquivo bruto.

**Output:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_interim/parquet/
```

Ações principais:
- leitura com fallback de parser quando necessário;
- conversão de `VL_CONTA` para `float64`;
- conversão de campos textuais para tipos internos padronizados;
- parse de `DT_REFER`, `DT_INI_EXERC` e `DT_FIM_EXERC` para `datetime`.

---

### 3. Transform — to_processed

**Input:** `.parquet` de `to_interim/`.

**O que faz:** Concatena os dados anuais de cada demonstração financeira e adiciona colunas derivadas. O dataset principal é montado por código de demonstração, com a marcação `ORIGEM_FORMULARIO = "ITR"` e cálculo de `INTERVALO_EXERC`.

**Output:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_processed/parquet/
```

Exemplo de arquivo gerado:
```
itr_cia_aberta_DRE_con_2011-2026.parquet
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
| `DT_REFER` | Data de referência do trimestre |
| `VERSAO` | Versão do documento |
| `GRUPO_DFP` | Grupo da demonstração |
| `ORDEM_EXERC` | Ordem do exercício/intervalo comparado |
| `DT_INI_EXERC` | Data inicial do exercício |
| `DT_FIM_EXERC` | Data final do exercício |
| `CD_CONTA` | Código da conta contábil |

---

## Observações do fluxo ITR

- A origem da ITR é semelhante à DFP, mas a granularidade contábil inclui o período contábil (`DT_INI_EXERC` e `DT_FIM_EXERC`).
- O processamento principal é realizado por demonstração (`BPA`, `DRE`, `DVA`, etc.), não por arquivo completo de todos os tipos em um único dataset.
- O passo de `to_processed` agrega anos de dados em um único arquivo parquet por demonstração, simplificando leitura analítica.
- O dataset final também carrega metadados de origem e intervalos de exercício que são úteis para comparações intertemporais.
