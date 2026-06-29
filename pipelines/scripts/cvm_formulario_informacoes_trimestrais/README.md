# Pipeline: CVM — Formulário de Informações Trimestrais (ITR)

Extrai, consolida, filtra e carrega as informações trimestrais de companhias abertas publicadas pela CVM em um banco de dados SQLite.

**Fonte:** [Portal de Dados Abertos da CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/)  
**Periodicidade da fonte:** trimestral (atualizada pela CVM ao longo do ano corrente)  
**Cobertura:** 2011 até o ano corrente

---

## O que é atualizado a cada execução?

| Processo | O que é atualizado | O que é pulado |
|---|---|---|
| `extract` | ZIPs e CSVs dos **2 anos mais recentes** (ano atual + anterior) | Anos anteriores com checkpoint de sucesso e arquivo presente |
| `transform_1` | **Todos** os 16 arquivos interim são sempre recriados do zero | — |
| `transform_2` | **Todos** os arquivos por ticker são sempre recriados do zero | Em `development_mode`: arquivos que já existem no disco |
| `load` | Todas as 16 tabelas do banco SQLite são sempre recriadas do zero | — |

> Em produção, `transform_1`, `transform_2` e `load` sempre reprocessam tudo. O custo de re-execução está principalmente no `extract`, que é incremental.

---

## Processos

### 1. `extract`

Realiza o download dos arquivos ZIP anuais da CVM e os extrai para a camada `raw/csv`.

**Entrada:** URLs públicas da CVM  
**Saída:** `raw/zip/itr_cia_aberta_{ano}.zip` → `raw/csv/itr_cia_aberta_{demonstracao}_{ano}.csv`

**Comportamento:**
- Baixa um ZIP por ano (`itr_cia_aberta_2011.zip` … `itr_cia_aberta_{ano_atual}.zip`).
- Os dois ZIPs mais recentes (ano atual e anterior) são sempre re-baixados e re-extraídos para garantir que a versão mais atualizada da CVM seja utilizada.
- Demais anos são pulados se já existirem no `raw/` com checkpoint de sucesso.
- Tentativas de download: até `DOWNLOAD_MAX_ATTEMPTS` (padrão: 3).
- Checkpoints gravados em: `state/checkpoints/.../extract/download_zip/` e `.../extract_zip/`.

---

### 2. `transform_1`

Concatena todos os CSVs anuais brutos de cada tipo de demonstração em um único arquivo consolidado por tipo, salvando na camada `interim`.

**Entrada:** `raw/csv/itr_cia_aberta_{demonstracao}_{ano}.csv` (2011 … ano atual)  
**Saída:** `interim/itr_cia_aberta_{demonstracao}_2011-{ano_atual}.csv`

**Demonstrações processadas (16 tipos):**

| Sigla | Descrição |
|---|---|
| `BPA_con` / `BPA_ind` | Balanço Patrimonial Ativo — consolidado / individual |
| `BPP_con` / `BPP_ind` | Balanço Patrimonial Passivo — consolidado / individual |
| `DFC_MD_con` / `DFC_MD_ind` | Demonstração de Fluxo de Caixa (Método Direto) |
| `DFC_MI_con` / `DFC_MI_ind` | Demonstração de Fluxo de Caixa (Método Indireto) |
| `DMPL_con` / `DMPL_ind` | Demonstração das Mutações do Patrimônio Líquido |
| `DRA_con` / `DRA_ind` | Demonstração do Resultado Abrangente |
| `DRE_con` / `DRE_ind` | Demonstração do Resultado do Exercício |
| `DVA_con` / `DVA_ind` | Demonstração do Valor Adicionado |

**Comportamento:**
- O arquivo interim é sempre recriado do zero (arquivo anterior removido antes do processamento).
- Se o CSV de um ano não for encontrado, o erro é registrado em log e o ano é ignorado na concatenação.
- Checkpoints gravados em: `state/checkpoints/.../processed/transform_1/`.

---

### 3. `transform_2`

Filtra os arquivos consolidados da camada `interim` por empresa, salvando os dados de cada ticker em arquivos separados na camada `processed`.

**Entrada:** `interim/itr_cia_aberta_{demonstracao}_2011-{ano_atual}.csv`  
**Saída:** `processed/transform_2/{TICKER}/{TICKER}_itr_cia_aberta_{demonstracao}_2011-{ano_atual}.csv`

**Universo de empresas:** carteira do Índice Brasil IBEP — identificadas por `CNPJ_CIA` (fallback: `DENOM_CIA`, depois `CD_CVM`).

**Comportamento:**
- O arquivo processado é sempre recriado do zero para garantir atualização.
- Em `development_mode`, arquivos já existentes são pulados para acelerar testes.
- Se nenhum dado for encontrado para um ticker após os três critérios de filtro, um checkpoint de falha (`FAILURE_VALIDATION`) é gravado e o ticker é ignorado.
- Checkpoints gravados em: `state/checkpoints/.../processed/transform_2/{TICKER}/`.

---

### 4. `load`

Carrega os CSVs processados pelo `transform_2` em um banco de dados SQLite, criando uma tabela por tipo de demonstração financeira.

**Entrada:** `processed/transform_2/{TICKER}/{TICKER}_itr_cia_aberta_{demonstracao}_2011-{ano_atual}.csv`  
**Saída:** `load/itr.db` (banco SQLite com 16 tabelas)

**Schema das tabelas:**

| Coluna | Descrição |
|---|---|
| `TICKER` | Código do ticker (adicionado no load, ex: `ABEV3`) |
| `CNPJ_CIA` | CNPJ da companhia |
| `DT_REFER` | Data de referência do documento |
| `VERSAO` | Versão do documento |
| `DENOM_CIA` | Denominação da companhia |
| `CD_CVM` | Código CVM |
| `GRUPO_DFP` | Grupo da demonstração |
| `MOEDA` | Moeda dos valores |
| `ESCALA_MOEDA` | Escala da moeda (ex: MIL) |
| `ORDEM_EXERC` | Ordem do exercício (ÚLTIMO / PENÚLTIMO) |
| `DT_FIM_EXERC` | Data de fim do exercício |
| `CD_CONTA` | Código da conta contábil |
| `DS_CONTA` | Descrição da conta contábil |
| `VL_CONTA` | Valor da conta |
| `ST_CONTA_FIXA` | Indica se a conta é fixa |

**Nomes das tabelas:** equivalentes à sigla da demonstração — `BPA_con`, `BPA_ind`, `BPP_con`, `BPP_ind`, `DFC_MD_con`, `DFC_MD_ind`, `DFC_MI_con`, `DFC_MI_ind`, `DMPL_con`, `DMPL_ind`, `DRA_con`, `DRA_ind`, `DRE_con`, `DRE_ind`, `DVA_con`, `DVA_ind`.

**Comportamento:**
- Cada tabela é recriada do zero a cada execução (`if_exists="replace"`).
- Se um CSV não puder ser lido, um checkpoint de falha é gravado para o par `{demonstracao}_{ticker}` e o processamento continua.
- Se nenhum ticker possuir dados para uma demonstração, ela é ignorada com aviso em log.
- Checkpoints gravados em: `state/checkpoints/.../load/load/`.
