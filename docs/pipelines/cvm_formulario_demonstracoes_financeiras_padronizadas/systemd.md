# Systemd Timers - CVM Formulario Demonstracoes Financeiras Padronizadas

Comandos Systemd para configuração e agendamento da execução automática do pipeline de Formulário de Demonstrações Financeiras Padronizadas (DFP) da CVM.

---

### 1.1 Criar service

```bash
sudo tee /etc/systemd/system/kairos-trap-cvm-dfp.service > /dev/null <<'EOF
[Unit]
Description=Kairos Trap - CVM DFP
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=rian
WorkingDirectory=/home/rian/kairos-trap/docker
ExecStart=/usr/bin/docker compose -f /home/rian/kairos-trap/docker/docker-compose.yml run --rm cvm-dfp-pipeline
EOF
```

### 1.2 Criar timer

```bash
sudo tee /etc/systemd/system/kairos-trap-cvm-dfp.timer > /dev/null <<'EOF
[Unit]
Description=Timer - CVM DFP

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true
Unit=kairos-trap-cvm-dfp.service

[Install]
WantedBy=timers.target
EOF
```

### 1.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kairos-trap-cvm-dfp.timer
```

### 1.4 Verificar

```bash
systemctl status kairos-trap-cvm-dfp.timer
systemctl list-timers --all | grep kairos-trap-cvm-dfp
journalctl -u kairos-trap-cvm-dfp.service -n 200 --no-pager
```