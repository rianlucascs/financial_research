# Readers

Centraliza as classes de leitura dos dados gerados pelos pipelines do projeto, com acesso via arquivos CSV/artefatos brutos ou via bancos SQLite carregados pelo `load`.

**Cobertura:** BCB, B3, CVM ITR, CVM DFP e Balanço Patrimonial consolidado  
**Formato de acesso:** classes `ReaderCSV...` e `ReaderSQL...`

---

## O que existe nesta pasta?

| Tipo | Origem | Uso principal |
|---|---|---|
| `ReaderCSV...` | Arquivos CSV em `data/pipelines/.../raw` ou `processed` | Inspeção do arquivo gerado pelo pipeline e consumo direto do artefato em disco |
| `ReaderSQL...` | Bancos SQLite em `data/pipelines/.../load` | Consumo analítico após a etapa `load`, sem reler CSVs manualmente |

> Em geral, use `ReaderCSV...` quando quiser trabalhar diretamente com o arquivo gerado pelo pipeline e `ReaderSQL...` quando quiser ler o dado já consolidado pelo `load`.

---

## Pipelines disponíveis

### 1. BCB — Histórico de Taxas de Juros

Arquivo: `pipelines/readers/bcb_historico_taxas_juros.py`

**Classes disponíveis:**
- `ReaderCSVBCBHistoricoTaxasJuros`
- `ReaderSQLBCBHistoricoTaxasJuros`

**Exemplo CSV:**

```python
from pipelines.readers.bcb_historico_taxas_juros import ReaderCSVBCBHistoricoTaxasJuros

reader = ReaderCSVBCBHistoricoTaxasJuros()
df = reader.read(start_date="2020-01-01", end_date="2024-12-31")
```

**Exemplo SQL:**

```python
from pipelines.readers.bcb_historico_taxas_juros import ReaderSQLBCBHistoricoTaxasJuros

reader = ReaderSQLBCBHistoricoTaxasJuros()
df = reader.read(start_date="2020-01-01", end_date="2024-12-31")
```

---

### 2. B3 — Indices e Segmentos Setoriais

Arquivo: `pipelines/readers/b3_indices_segmentos_setoriais.py`

**Classes disponíveis:**
- `ReaderCSVB3IndicesSegmentosSetoriais`
- `ReaderSQLB3IndicesSegmentosSetoriais`

**Exemplo CSV:**

```python
from pipelines.readers.b3_indices_segmentos_setoriais import ReaderCSVB3IndicesSegmentosSetoriais

reader = ReaderCSVB3IndicesSegmentosSetoriais()
df = reader.read(indice="IDIV")
```

**Exemplo SQL:**

```python
from pipelines.readers.b3_indices_segmentos_setoriais import ReaderSQLB3IndicesSegmentosSetoriais

reader = ReaderSQLB3IndicesSegmentosSetoriais()
df = reader.read(indice="IDIV")
```

---

### 3. CVM — Formulário de Informações Trimestrais (ITR)

Arquivo: `pipelines/readers/cvm_formulario_informacoes_trimestrais.py`

**Classes disponíveis:**
- `ReaderCSVCVMFormularioInformacoesTrimestrais`
- `ReaderSQLCVMFormularioInformacoesTrimestrais`

**Exemplo CSV:**

```python
from pipelines.readers.cvm_formulario_informacoes_trimestrais import ReaderCSVCVMFormularioInformacoesTrimestrais

reader = ReaderCSVCVMFormularioInformacoesTrimestrais()
df = reader.read(ticker="VALE3", tipo_arquivo="BPA_con")
```

**Exemplo SQL:**

```python
from pipelines.readers.cvm_formulario_informacoes_trimestrais import ReaderSQLCVMFormularioInformacoesTrimestrais

reader = ReaderSQLCVMFormularioInformacoesTrimestrais()
df = reader.read(ticker="VALE3", tipo_arquivo="BPA_con")
```

---

### 4. CVM — Formulário de Demonstrações Financeiras Padronizadas (DFP)

Arquivo: `pipelines/readers/cvm_formulario_demonstracoes_financeiras_padronizadas.py`

**Classes disponíveis:**
- `ReaderCSVCVMFormularioDemonstracoesFinanceirasPadronizadas`
- `ReaderSQLCVMFormularioDemonstracoesFinanceirasPadronizadas`

**Exemplo CSV:**

```python
from pipelines.readers.cvm_formulario_demonstracoes_financeiras_padronizadas import ReaderCSVCVMFormularioDemonstracoesFinanceirasPadronizadas

reader = ReaderCSVCVMFormularioDemonstracoesFinanceirasPadronizadas()
df = reader.read(ticker="VALE3", tipo_arquivo="BPA_con")
```

**Exemplo SQL:**

```python
from pipelines.readers.cvm_formulario_demonstracoes_financeiras_padronizadas import ReaderSQLCVMFormularioDemonstracoesFinanceirasPadronizadas

reader = ReaderSQLCVMFormularioDemonstracoesFinanceirasPadronizadas()
df = reader.read(ticker="VALE3", tipo_arquivo="BPA_con")
```

---

### 5. CVM — Balanço Patrimonial Consolidado

Arquivo: `pipelines/readers/cvm_balanco_patrimonial.py`

**Classes disponíveis:**
- `ReaderCSVCVMBalancoPatrimonial`
- `ReaderSQLCVMBalancoPatrimonial`

Essas classes combinam dados de ITR e DFP e retornam uma série tratada por conta contábil.

**Exemplo CSV:**

```python
from pipelines.readers.cvm_balanco_patrimonial import ReaderCSVCVMBalancoPatrimonial

reader = ReaderCSVCVMBalancoPatrimonial()
df = reader.read(ticker="VALE3", tipo_arquivo="BPA_con", cd_conta="1")
```

**Exemplo SQL:**

```python
from pipelines.readers.cvm_balanco_patrimonial import ReaderSQLCVMBalancoPatrimonial

reader = ReaderSQLCVMBalancoPatrimonial()
df = reader.read(ticker="VALE3", tipo_arquivo="BPA_con", cd_conta="1")
```

---

## Observações

- Os readers SQL dependem da execução prévia da etapa `load` do pipeline correspondente.
- Os readers CSV dependem da existência dos arquivos brutos ou processados no diretório `data/pipelines/...`.
- Os readers da CVM não aceitam ticker com ponto, por exemplo use `VALE3` e não `VALE3.SA`.
- No caso do Balanço Patrimonial, o parâmetro `cd_conta` controla a conta contábil filtrada na série final.