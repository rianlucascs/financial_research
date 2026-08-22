# System Times — CVM Cias Abertas Informacao Cadastral

Comandos Systemd para configuração e agendamento da execução automática do pipeline de Cadastro de Companhias Abertas da CVM.

---

### 1.1 Criar service

```bash
sudo tee /etc/systemd/system/financial-research-cvm-cad.service > /dev/null <<'EOF'
[Unit]
Description=Financial Research - CVM CAD
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=rian
WorkingDirectory=/home/rian/financial_research/docker
ExecStart=/usr/bin/docker compose -f /home/rian/financial_research/docker/docker-compose.yml run --rm cvm-cad-pipeline
EOF
```

### 1.2 Criar timer

```bash
sudo tee /etc/systemd/system/financial-research-cvm-cad.timer > /dev/null <<'EOF'
[Unit]
Description=Timer - CVM CAD

[Timer]
OnCalendar=*-*-* 09:10:00
Persistent=true
Unit=financial-research-cvm-cad.service

[Install]
WantedBy=timers.target
EOF
```

### 1.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now financial-research-cvm-cad.timer
```
