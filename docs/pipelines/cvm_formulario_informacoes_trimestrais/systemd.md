# Systemd Timers - CVM Formulario Informacoes Trimestrais

Comandos Systemd para configuração e agendamento da execução automática do pipeline de Formulário de Informações Trimestrais (ITR) da CVM.

---

### 1.1 Criar service

```bash
sudo tee /etc/systemd/system/kairos-trap-cvm-itr.service > /dev/null <<'EOF
[Unit]
Description=Kairos Trap - CVM ITR
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=rian
WorkingDirectory=/home/rian/kairos-trap/docker
ExecStart=/usr/bin/docker compose -f /home/rian/kairos-trap/docker/docker-compose.yml run --rm cvm-itr-pipeline
EOF
```

### 1.2 Criar timer

```bash
sudo tee /etc/systemd/system/kairos-trap-cvm-itr.timer > /dev/null <<'EOF
[Unit]
Description=Timer - CVM ITR

[Timer]
OnCalendar=*-*-* 08:30:00
Persistent=true
Unit=kairos-trap-cvm-itr.service

[Install]
WantedBy=timers.target
EOF
```

### 1.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kairos-trap-cvm-itr.timer
```

### 1.4 Verificar

```bash
systemctl status kairos-trap-cvm-itr.timer
systemctl list-timers --all | grep kairos-trap-cvm-itr
journalctl -u kairos-trap-cvm-itr.service -n 200 --no-pager
```