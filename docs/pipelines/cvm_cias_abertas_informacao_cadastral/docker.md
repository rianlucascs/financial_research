# Docker — CVM Cias Abertas Informacao Cadastral

Comandos Docker específicos para execução e manutenção do pipeline de Cadastro de Companhias Abertas da CVM.

---

## Build

```bash
# Constrói a imagem Docker utilizada pelos pipelines do projeto.
docker build -f docker/Dockerfile.pipelines -t financial_pipelines .
```

## Executar via docker run

```bash
# Executa o pipeline de Cadastro de Companhias Abertas em ambiente de desenvolvimento.
docker run --rm -it \
  -e PIPELINE_NAME=cvm_cias_abertas_informacao_cadastral \
  -e PIPELINE_ENV=dev \
  -v "$PWD/pipelines/data:/app/pipelines/data" \
  -v "$PWD/pipelines/logs:/app/pipelines/logs" \
  -v "$PWD/pipelines/checkpoints:/app/pipelines/checkpoints" \
  -v "$PWD/pipelines/historical_data:/app/pipelines/historical_data" \
  financial_pipelines
```

## Executar via docker compose

```bash
# Executa o pipeline de Cadastro de Companhias Abertas via Docker Compose em ambiente de desenvolvimento.
docker compose -f docker/docker-compose.yml run --rm \
  -e PIPELINE_NAME=cvm_cias_abertas_informacao_cadastral \
  -e PIPELINE_ENV=dev \
  cvm-cad-pipeline
```
