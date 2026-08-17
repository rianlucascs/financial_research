# Docker

Comandos gerais de Docker utilizados na operação e manutenção dos pipelines do projeto.

---

## Monitoramento de containers

```bash
# Lista apenas os containers em execução
docker ps
```

```bash
# Mostra em tempo real o consumo de recursos dos containers Docker que estão rodando
docker stats
```

## Build das imagens

```bash
# Reconstrói as imagens sempre que os scripts forem atualizados
docker compose -f docker/docker-compose.yml build --no-cache
```

## Verificação de imagens

```bash
# Confirma a data de criação e o ID da imagem atualizada
docker image inspect docker-cvm-itr-pipeline \
  --format 'Created={{.Created}} Id={{.Id}}'
```
