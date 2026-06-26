# Docker

```bash
docker build -f docker/Dockerfile.pipelines -t financial_pipelines .
```

```bash
docker run --rm -it \
  -e PIPELINE_NAME=cvm_formulario_informacoes_trimestrais \
  -e PIPELINE_ENV=dev \
  -v "$PWD/data:/app/data" \
  -v "$PWD/logs:/app/logs" \
  -v "$PWD/state:/app/state" \
  financial_pipelines
```