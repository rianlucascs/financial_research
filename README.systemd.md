# Systemd Timers para Pipelines (Docker Compose)

Este guia mostra como agendar os pipelines com systemd timers no Ubuntu Server, executando sempre via Docker Compose.

## 1) Pre-requisitos

```bash
# Docker e Compose funcionando
cd /home/rian/financial_research/docker
docker compose config
```

## 2) Estrutura usada

- Projeto: /home/rian/financial_research
- Compose: /home/rian/financial_research/docker/docker-compose.yml
- Units systemd: /etc/systemd/system

## 3) Pipeline BCB Historico Taxas Juros

### 3.1 Criar service

```bash
sudo tee /etc/systemd/system/financial-research-bcb.service > /dev/null <<'EOF'
[Unit]
Description=Financial Research - BCB Historico Taxas Juros
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=rian
WorkingDirectory=/home/rian/financial_research/docker
ExecStart=/usr/bin/docker compose -f /home/rian/financial_research/docker/docker-compose.yml run --rm bcb-historico-taxas-juros-pipeline
EOF
```

### 3.2 Criar timer

```bash
sudo tee /etc/systemd/system/financial-research-bcb.timer > /dev/null <<'EOF'
[Unit]
Description=Timer - BCB Historico Taxas Juros

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true
Unit=financial-research-bcb.service

[Install]
WantedBy=timers.target
EOF
```

### 3.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now financial-research-bcb.timer
```

## 4) Pipeline CVM ITR

### 4.1 Criar service

```bash
sudo tee /etc/systemd/system/financial-research-cvm-itr.service > /dev/null <<'EOF'
[Unit]
Description=Financial Research - CVM ITR
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=rian
WorkingDirectory=/home/rian/financial_research/docker
ExecStart=/usr/bin/docker compose -f /home/rian/financial_research/docker/docker-compose.yml run --rm cvm-itr-pipeline
EOF
```

### 4.2 Criar timer

```bash
sudo tee /etc/systemd/system/financial-research-cvm-itr.timer > /dev/null <<'EOF'
[Unit]
Description=Timer - CVM ITR

[Timer]
OnCalendar=*-*-* 09:20:00
Persistent=true
Unit=financial-research-cvm-itr.service

[Install]
WantedBy=timers.target
EOF
```

### 4.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now financial-research-cvm-itr.timer
```

## 5) Pipeline CVM DFP

### 5.1 Criar service

```bash
sudo tee /etc/systemd/system/financial-research-cvm-dfp.service > /dev/null <<'EOF'
[Unit]
Description=Financial Research - CVM DFP
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=rian
WorkingDirectory=/home/rian/financial_research/docker
ExecStart=/usr/bin/docker compose -f /home/rian/financial_research/docker/docker-compose.yml run --rm cvm-dfp-pipeline
EOF
```

### 5.2 Criar timer

```bash
sudo tee /etc/systemd/system/financial-research-cvm-dfp.timer > /dev/null <<'EOF'
[Unit]
Description=Timer - CVM DFP

[Timer]
OnCalendar=*-*-* 09:40:00
Persistent=true
Unit=financial-research-cvm-dfp.service

[Install]
WantedBy=timers.target
EOF
```

### 5.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now financial-research-cvm-dfp.timer
```

## 6) Comandos de operacao

```bash
# Ver timers
systemctl list-timers --all | grep financial-research-

# Teste manual dos services
sudo systemctl start financial-research-bcb.service
sudo systemctl start financial-research-cvm-itr.service
sudo systemctl start financial-research-cvm-dfp.service

# Status
systemctl status financial-research-bcb.timer
systemctl status financial-research-cvm-itr.timer
systemctl status financial-research-cvm-dfp.timer

# Logs
journalctl -u financial-research-bcb.service -n 200 --no-pager
journalctl -u financial-research-cvm-itr.service -n 200 --no-pager
journalctl -u financial-research-cvm-dfp.service -n 200 --no-pager
```

## 7) Observacoes

- Troque User=rian para o usuario correto do seu servidor.
- Se quiser outro horario, altere OnCalendar e rode:

```bash
sudo systemctl daemon-reload
sudo systemctl restart financial-research-bcb.timer
sudo systemctl restart financial-research-cvm-itr.timer
sudo systemctl restart financial-research-cvm-dfp.timer
```
