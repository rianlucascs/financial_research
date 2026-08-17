# System Times — CVM Formulario Demonstracoes Financeiras Padronizadas

Comandos Systemd para configuração e agendamento da execução automática do pipeline de Formulário de Demonstrações Financeiras Padronizadas (DFP) da CVM.

---

### 1.1 Criar service

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

### 1.2 Criar timer

```bash
sudo tee /etc/systemd/system/financial-research-cvm-dfp.timer > /dev/null <<'EOF'
[Unit]
Description=Timer - CVM DFP

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true
Unit=financial-research-cvm-dfp.service

[Install]
WantedBy=timers.target
EOF
```

### 1.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now financial-research-cvm-dfp.timer
```