# Pipeline - CVM Formulario Demonstracoes Financeiras Padronizadas

Obtém e prepara as Demonstrações Financeiras Padronizadas (DFP) da CVM.

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

**Processamento:** Faz o download dos arquivos `.zip`, descompacta e salva os `.csv` brutos.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/raw/zip/   ← arquivos .zip
data/<pipeline>/<YYYY-MM-DD>/raw/csv/   ← arquivos .csv descompactados
```

---

### 2. Transform - to_interim

**Entrada:** `.csv` em `raw/csv/` (separador `;`, encoding `iso-8859-1`).

**Processamento:** Leitura, padronização de tipos e colunas, limpeza inicial. Um arquivo `.parquet` por ano.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_interim/parquet/
```

---

### 3. Transform - to_processed

**Entrada:** `.parquet` de `to_interim/`.

**Processamento:** Aplica regra de negócio (ex.: filtros por código de demonstração, consolidação por `GRUPO_DFP`). Um arquivo `.parquet` por grupo/ano.

**Saída:**
```
data/<pipeline>/<YYYY-MM-DD>/transformed/to_processed/parquet/
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
| `DT_REFER` | Data de referência |
| `VERSAO` | Versão do documento |
| `GRUPO_DFP` | Grupo da demonstração |
| `ORDEM_EXERC` | Ordem do exercício |
| `DT_FIM_EXERC` | Data de fim do exercício |
| `CD_CONTA` | Código da conta contábil |

## Particularidades do pipeline

- `to_processed` aplica filtros por código de demonstração e consolida os dados por `GRUPO_DFP`.

## Qualidade dos dados

- [detalhar: falta informação sobre conversões de tipos, validações e tratamento de dados inválidos].
