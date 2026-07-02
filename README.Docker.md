# Docker

## Build

```bash
docker build -f docker/Dockerfile.pipelines -t financial_pipelines .
```

---

## Executar via docker run

### BCB Historico Taxas Juros

```bash
docker run --rm -it \
  -e PIPELINE_NAME=bcb_historico_taxas_juros \
  -e PIPELINE_ENV=dev \
  -v "$PWD/data:/app/data" \
  -v "$PWD/logs:/app/logs" \
  -v "$PWD/state:/app/state" \
  financial_pipelines
```

### CVM Formulario Informacoes Trimestrais (ITR)

```bash
docker run --rm -it \
  -e PIPELINE_NAME=cvm_formulario_informacoes_trimestrais \
  -e PIPELINE_ENV=dev \
  -v "$PWD/data:/app/data" \
  -v "$PWD/logs:/app/logs" \
  -v "$PWD/state:/app/state" \
  financial_pipelines
```

### CVM Formulario Demonstracoes Financeiras Padronizadas (DFP)

```bash
docker run --rm -it \
  -e PIPELINE_NAME=cvm_formulario_demonstracoes_financeiras_padronizadas \
  -e PIPELINE_ENV=dev \
  -v "$PWD/data:/app/data" \
  -v "$PWD/logs:/app/logs" \
  -v "$PWD/state:/app/state" \
  financial_pipelines
```

---

## Executar via Docker Compose

### BCB Historico Taxas Juros

```bash
docker compose -f docker/docker-compose.yml run --rm bcb-historico-taxas-juros-pipeline
```

### CVM ITR

```bash
docker compose -f docker/docker-compose.yml run --rm cvm-itr-pipeline
```

### CVM DFP

```bash
docker compose -f docker/docker-compose.yml run --rm cvm-dfp-pipeline
```

### Todos os pipelines em sequencia (via depends_on)

```bash
docker compose -f docker/docker-compose.yml up
```

---

## Variaveis de ambiente

| Variavel       | Valores aceitos | Descricao                        |
|----------------|-----------------|----------------------------------|
| PIPELINE_NAME  | ver abaixo      | Nome do pipeline a executar      |
| PIPELINE_ENV   | dev / prod      | Ambiente de execucao             |

Valores validos para PIPELINE_NAME:

- `bcb_historico_taxas_juros`
- `cvm_formulario_informacoes_trimestrais`
- `cvm_formulario_demonstracoes_financeiras_padronizadas`