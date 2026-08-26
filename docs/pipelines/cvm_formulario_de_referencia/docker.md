# Docker — CVM Formulario de Referencia

Comandos Docker específicos para execução e manutenção do pipeline de Formulário de Referência (FRE) da CVM.

---

## Build

```bash
# Constrói a imagem Docker utilizada pelos pipelines do projeto.
docker build -f docker/Dockerfile.pipelines -t financial_pipelines .
```

## Executar via docker run

```bash
# Executa o pipeline de Formulário de Referência (FRE) em ambiente de desenvolvimento.
docker run --rm -it \
  -e PIPELINE_NAME=cvm_formulario_de_referencia \
  -e PIPELINE_ENV=dev \
  -v "$PWD/pipelines/data:/app/pipelines/data" \
  -v "$PWD/pipelines/logs:/app/pipelines/logs" \
  -v "$PWD/pipelines/checkpoints:/app/pipelines/checkpoints" \
  -v "$PWD/pipelines/historical_data:/app/pipelines/historical_data" \
  financial_pipelines
```

## Executar via docker compose

```bash
# Executa o pipeline de Formulário de Referência (FRE) via Docker Compose em ambiente de desenvolvimento.
docker compose -f docker/docker-compose.yml run --rm \
  -e PIPELINE_NAME=cvm_formulario_de_referencia \
  -e PIPELINE_ENV=dev \
  cvm-fre-pipeline
```
