# Pipeline - B3 Enriquecimento Cadastral de Ativos

Como os dados cadastrais e de negociacao da B3 sao obtidos e preparados para consulta.

---

## Fluxo geral

```
extract -> to_interim -> load -> retention
```

Cada execucao cria um snapshot datado (`YYYY-MM-DD`). O extract usa o snapshot de `cvm_cias_abertas_informacao_cadastral` como fonte de companhias ativas.

---

## Stage por stage

### 1. Extract

**Input:** companhias com `SIT = ATIVO` do snapshot cadastral da CVM e endpoint de detalhe de empresas listadas da B3.

**O que faz:** consulta a B3 por `CD_CVM`, grava uma resposta JSON por companhia e mantém arquivos ja existentes no mesmo snapshot. A consulta tem ate quatro tentativas por empresa e limite total de quatro horas.

**Output:**

```
data/b3_enriquecimento_cadastral_ativos/<YYYY-MM-DD>/raw/json/
    cd_cvm_<codigo>.json
```

### 2. Transform - to_interim

**Input:** arquivos JSON em `raw/json/`.

**O que faz:** normaliza o objeto principal de cada companhia e separa a lista `otherCodes` em uma tabela propria. Isso preserva todos os codigos de negociacao e ISINs de empresas que possuem mais de um ativo.

**Output:**

```
data/b3_enriquecimento_cadastral_ativos/<YYYY-MM-DD>/transformed/to_interim/parquet/
    empresas.parquet
    codigos.parquet
```

As datas `dateQuotation` e `lastDate` sao interpretadas no formato brasileiro (`DD/MM/YYYY`) antes da persistencia em parquet.

### 3. Load

**Input:** parquets de `to_interim/`.

**O que faz:** carrega cada parquet no destino configurado pelo loader, mantendo os datasets `empresas` e `codigos` separados.

### 4. Retention

**O que faz:** aplica as politicas padrao de retencao de dados e logs do projeto.

---

## Dependencia

- `cvm_cias_abertas_informacao_cadastral` deve ter um snapshot disponivel, pois fornece `CD_CVM` e `SIT` usados no extract.
- Apenas companhias com situacao `ATIVO` sao consultadas na B3.

## Observacoes de qualidade

- O JSON bruto e preservado para rastreabilidade e reprocessamento.
- Arquivos ja baixados nao sao sobrescritos numa reexecucao do mesmo snapshot.
- Respostas vazias, empresa nao encontrada, rate limit e indisponibilidade da API geram checkpoints de falha ou retentativas.