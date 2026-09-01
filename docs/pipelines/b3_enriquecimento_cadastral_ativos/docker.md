# Docker - B3 Enriquecimento Cadastral de Ativos

Comandos Docker para executar o pipeline que enriquece o cadastro de companhias ativas com dados de negociacao da B3.

---

## Build

```bash
# Constroi a imagem Docker utilizada pelos pipelines do projeto.
docker build -f docker/Dockerfile.pipelines -t financial_pipelines .
```

## Executar via docker run

```bash
# Executa o pipeline B3 em ambiente de desenvolvimento.
docker run --rm -it \
  -e PIPELINE_NAME=b3_enriquecimento_cadastral_ativos \
  -e PIPELINE_ENV=dev \
  -v "$PWD/pipelines/data:/app/pipelines/data" \
  -v "$PWD/pipelines/logs:/app/pipelines/logs" \
  -v "$PWD/pipelines/checkpoints:/app/pipelines/checkpoints" \
  -v "$PWD/pipelines/historical_data:/app/pipelines/historical_data" \
  financial_pipelines
```

## Executar via docker compose

```bash
# Executa o pipeline B3 via Docker Compose em ambiente de desenvolvimento.
docker compose -f docker/docker-compose.yml run --rm \
  -e PIPELINE_ENV=dev \
  b3-cad-pipeline
```