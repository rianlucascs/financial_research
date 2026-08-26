# System Times — CVM Formulario de Referencia

Comandos Systemd para configuração e agendamento da execução automática do pipeline de Formulário de Referência (FRE) da CVM.

---

### 1.1 Criar service

```bash
sudo tee /etc/systemd/system/financial-research-cvm-fre.service > /dev/null <<'EOF'
[Unit]
Description=Financial Research - CVM FRE
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=rian
WorkingDirectory=/home/rian/financial_research/docker
ExecStart=/usr/bin/docker compose -f /home/rian/financial_research/docker/docker-compose.yml run --rm cvm-fre-pipeline
EOF
```

### 1.2 Criar timer

```bash
sudo tee /etc/systemd/system/financial-research-cvm-fre.timer > /dev/null <<'EOF'
[Unit]
Description=Timer - CVM FRE

[Timer]
OnCalendar=*-*-* 19:00:00
Persistent=true
Unit=financial-research-cvm-fre.service

[Install]
WantedBy=timers.target
EOF
```

### 1.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now financial-research-cvm-fre.timer
```
