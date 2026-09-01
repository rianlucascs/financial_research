# Pipeline - CVM Formulario Informacoes Trimestrais

Obtém e prepara as Informações Trimestrais (ITR) da CVM.

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

**Entrada:** URLs públicas da CVM (um `.zip` por ano, de 2011 até o ano atual).

**Processamento:** Faz o download dos arquivos `.zip` do formulário ITR, descompacta e salva os `.csv` brutos.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/raw/zip/   ← arquivos .zip
data/<pipeline>/<YYYY-MM-DD>/raw/csv/   ← arquivos .csv descompactados
```

---

### 2. Transform - to_interim

**Entrada:** `.csv` em `raw/csv/` (separador `;`, encoding `iso-8859-1`).

**Processamento:** Leitura, padronização de tipos e colunas, limpeza inicial e conversão de datas e valores numéricos. Um arquivo `.parquet` por ano e por arquivo bruto.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_interim/parquet/
```

Ações principais:
- leitura com fallback de parser quando necessário;
- conversão de `VL_CONTA` para `float64`;
- conversão de campos textuais para tipos internos padronizados;
- parse de `DT_REFER`, `DT_INI_EXERC` e `DT_FIM_EXERC` para `datetime`.

---

### 3. Transform - to_processed

**Entrada:** `.parquet` de `to_interim/`.

**Processamento:** Concatena os dados anuais de cada demonstração financeira e adiciona colunas derivadas. O dataset principal é montado por código de demonstração, com a marcação `ORIGEM_FORMULARIO = "ITR"` e cálculo de `INTERVALO_EXERC`.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_processed/parquet/
```

Exemplo de arquivo gerado:
```
itr_cia_aberta_DRE_con_2011-2026.parquet
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
| `DT_REFER` | Data de referência do trimestre |
| `VERSAO` | Versão do documento |
| `GRUPO_DFP` | Grupo da demonstração |
| `ORDEM_EXERC` | Ordem do exercício/intervalo comparado |
| `DT_INI_EXERC` | Data inicial do exercício |
| `DT_FIM_EXERC` | Data final do exercício |
| `CD_CONTA` | Código da conta contábil |

---

## Particularidades do pipeline

- A origem da ITR é semelhante à DFP, mas a granularidade contábil inclui o período contábil (`DT_INI_EXERC` e `DT_FIM_EXERC`).
- O processamento principal é realizado por demonstração (`BPA`, `DRE`, `DVA`, etc.), não por arquivo completo de todos os tipos em um único dataset.
- O passo de `to_processed` agrega anos de dados em um único arquivo parquet por demonstração, simplificando leitura analítica.
- O dataset final também carrega metadados de origem e intervalos de exercício que são úteis para comparações intertemporais.

## Qualidade dos dados

- [detalhar: falta informação sobre validações e tratamento de dados inválidos].
