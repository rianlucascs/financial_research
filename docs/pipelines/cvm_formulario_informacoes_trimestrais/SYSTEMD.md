# System Times — CVM Formulario Informacoes Trimestrais

Comandos Systemd para configuração e agendamento da execução automática do pipeline de Formulário de Informações Trimestrais (ITR) da CVM.

---

### 1.1 Criar service

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

### 1.2 Criar timer

```bash
sudo tee /etc/systemd/system/financial-research-cvm-itr.timer > /dev/null <<'EOF'
[Unit]
Description=Timer - CVM ITR

[Timer]
OnCalendar=*-*-* 08:30:00
Persistent=true
Unit=financial-research-cvm-itr.service

[Install]
WantedBy=timers.target
EOF
```

### 1.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now financial-research-cvm-itr.timer
```