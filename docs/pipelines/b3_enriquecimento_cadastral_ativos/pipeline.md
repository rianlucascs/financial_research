# Pipeline - B3 Enriquecimento Cadastral de Ativos

Obtém dados cadastrais e de negociação da B3 para companhias ativas da CVM.

---

## Fluxo geral

```
extract -> to_interim -> load -> retention
```

## Execução e snapshots

- Cada execução cria um snapshot datado (`YYYY-MM-DD`).
- O extract depende de um snapshot disponível de `cvm_cias_abertas_informacao_cadastral`.

---

## Stages

### 1. Extract

**Entrada:** companhias com `SIT = ATIVO` do snapshot cadastral da CVM e endpoint de detalhe de empresas listadas da B3.

**Processamento:** consulta a B3 por `CD_CVM` e grava uma resposta JSON por companhia.

**Saída:**

```
data/b3_enriquecimento_cadastral_ativos/<YYYY-MM-DD>/raw/json/
    cd_cvm_<codigo>.json
```

Particularidades:

- Arquivos já existentes não são sobrescritos em reexecuções do mesmo snapshot.
- São feitas até quatro tentativas por companhia, com limite total de quatro horas.
- Respostas vazias, empresa não encontrada, rate limit e indisponibilidade da API geram checkpoints de falha ou retentativas.

### 2. Transform - to_interim

**Entrada:** arquivos JSON em `raw/json/`.

**Processamento:** normaliza o objeto principal de cada companhia e separa `otherCodes` em uma tabela própria, preservando códigos de negociação e ISINs adicionais.

**Saída:**

```
data/b3_enriquecimento_cadastral_ativos/<YYYY-MM-DD>/transformed/to_interim/parquet/
    empresas.parquet
    codigos.parquet
```

Particularidades:

- `dateQuotation` e `lastDate` são interpretadas no formato brasileiro (`DD/MM/YYYY`) antes da persistência em Parquet.

### 3. Load

**Entrada:** arquivos Parquet de `to_interim/`.

**Processamento:** carrega os datasets `empresas` e `codigos` separadamente no destino configurado pelo loader.

**Saída:** [detalhar: falta informação sobre o destino e os artefatos gerados].

### 4. Retention

**Entrada:** dados e logs do pipeline.

**Processamento:** aplica as políticas padrão de retenção do projeto.

**Saída:** [detalhar: falta informação sobre o período de retenção].

---

## Particularidades do pipeline

- Apenas companhias em situação `ATIVO` são consultadas na B3.
- O JSON bruto é preservado para rastreabilidade e reprocessamento.

## Qualidade dos dados

- A lista `otherCodes` é normalizada em `codigos`, evitando perda de ativos adicionais.
- Dados ausentes e falhas de consulta são registrados em checkpoints.