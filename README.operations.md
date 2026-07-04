# Operacao do Servidor

Checklist operacional para validar o ambiente do `financial_research` depois de reinicializacao do servidor, manutencao manual ou investigacao de falha.

**Escopo:** saude do servidor, Docker, systemd timers, logs e diretorios de dados do projeto  
**Projeto:** `/home/rian/financial_research`

---

## 1. Verificacao rapida apos ligar o servidor

Execute os comandos abaixo na ordem:

```bash
# Identificacao basica
hostnamectl
date
uptime

# Disco e memoria
df -h
free -h

# Carga e processos mais pesados
ps aux --sort=-%mem | head
ps aux --sort=-%cpu | head
```

**O que validar:**
- horario do servidor correto;
- particoes sem saturacao;
- memoria livre suficiente;
- nenhum processo inesperado consumindo CPU ou RAM de forma anormal.

---

## 2. Validar Docker

```bash
sudo systemctl status docker --no-pager
docker ps -a
docker images
```

**O que validar:**
- servico `docker` ativo;
- comandos Docker executando sem erro;
- imagem `financial_pipelines` disponivel quando necessario.

---

## 3. Validar Docker Compose do projeto

```bash
cd /home/rian/financial_research/docker
docker compose config
```

**O que validar:**
- arquivo `docker-compose.yml` sem erro de sintaxe;
- servicos dos pipelines aparecendo corretamente.

---

## 4. Validar timers e services

```bash
systemctl list-timers --all | grep financial-research-

systemctl status financial-research-b3-indices.timer --no-pager
systemctl status financial-research-bcb.timer --no-pager
systemctl status financial-research-cvm-itr.timer --no-pager
systemctl status financial-research-cvm-dfp.timer --no-pager
```

**O que validar:**
- timers ativos e com proxima execucao agendada;
- units sem estado de erro;
- agendamentos coerentes com a rotina esperada.

---

## 5. Ver logs recentes dos pipelines

```bash
journalctl -u financial-research-b3-indices.service -n 100 --no-pager
journalctl -u financial-research-bcb.service -n 100 --no-pager
journalctl -u financial-research-cvm-itr.service -n 100 --no-pager
journalctl -u financial-research-cvm-dfp.service -n 100 --no-pager
```

**O que validar:**
- ausencia de erro recorrente;
- ultima execucao concluida com sucesso;
- sem falha de permissao, Docker, rede ou espaco em disco.

---

## 6. Validar diretorios criticos do projeto

```bash
ls -ld /home/rian/financial_research/data
ls -ld /home/rian/financial_research/logs
ls -ld /home/rian/financial_research/state

du -sh /home/rian/financial_research/data
du -sh /home/rian/financial_research/logs
du -sh /home/rian/financial_research/state
```

**O que validar:**
- diretorios existem;
- usuario correto tem permissao de leitura e escrita;
- crescimento de dados dentro do esperado.

---

## 7. Teste manual de um pipeline

Quando houver duvida sobre a saude do ambiente, rode manualmente um pipeline em modo `dev`.

### Exemplo: B3 Indices e Segmentos Setoriais

```bash
cd /home/rian/financial_research

docker run --rm -it \
  -e PIPELINE_NAME=b3_indices_segmentos_setoriais \
  -e PIPELINE_ENV=dev \
  -v "$PWD/data:/app/data" \
  -v "$PWD/logs:/app/logs" \
  -v "$PWD/state:/app/state" \
  financial_pipelines
```

### Exemplo: BCB Historico Taxas Juros

```bash
cd /home/rian/financial_research

docker run --rm -it \
  -e PIPELINE_NAME=bcb_historico_taxas_juros \
  -e PIPELINE_ENV=dev \
  -v "$PWD/data:/app/data" \
  -v "$PWD/logs:/app/logs" \
  -v "$PWD/state:/app/state" \
  financial_pipelines
```

---

## 8. Comandos uteis de correção

### Reiniciar Docker

```bash
sudo systemctl restart docker
sudo systemctl status docker --no-pager
```

### Recarregar units do systemd

```bash
sudo systemctl daemon-reload
```

### Reiniciar timers do projeto

```bash
sudo systemctl restart financial-research-b3-indices.timer
sudo systemctl restart financial-research-bcb.timer
sudo systemctl restart financial-research-cvm-itr.timer
sudo systemctl restart financial-research-cvm-dfp.timer
```

### Testar service manualmente

```bash
sudo systemctl start financial-research-b3-indices.service
sudo systemctl start financial-research-bcb.service
sudo systemctl start financial-research-cvm-itr.service
sudo systemctl start financial-research-cvm-dfp.service
```

---

## 9. Sinais de alerta

Investigue imediatamente se houver qualquer um destes sintomas:

- `docker compose config` falhando;
- timer sem proxima execucao;
- erro recorrente em `journalctl`;
- particao perto de 100%;
- `data/`, `logs/` ou `state/` sem permissao de escrita;
- imagem `financial_pipelines` ausente ou desatualizada.

---

## 10. Referencias relacionadas

- `README.md`
- `README.Docker.md`
- `README.systemd.md`
- `pipelines/readers/README.md`