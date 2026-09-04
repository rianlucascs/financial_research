# Systemd Timers - CVM Formulario de Referencia

Comandos Systemd para configuração e agendamento da execução automática do pipeline de Formulário de Referência (FRE) da CVM.

---

### 1.1 Criar service

```bash
sudo tee /etc/systemd/system/kairos-trap-cvm-fre.service > /dev/null <<'EOF
[Unit]
Description=Kairos Trap - CVM FRE
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=rian
WorkingDirectory=/home/rian/kairos-trap/docker
ExecStart=/usr/bin/docker compose -f /home/rian/kairos-trap/docker/docker-compose.yml run --rm cvm-fre-pipeline
EOF
```

### 1.2 Criar timer

```bash
sudo tee /etc/systemd/system/kairos-trap-cvm-fre.timer > /dev/null <<'EOF
[Unit]
Description=Timer - CVM FRE

[Timer]
OnCalendar=*-*-* 19:00:00
Persistent=true
Unit=kairos-trap-cvm-fre.service

[Install]
WantedBy=timers.target
EOF
```

### 1.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kairos-trap-cvm-fre.timer
```

### 1.4 Verificar

```bash
systemctl status kairos-trap-cvm-fre.timer
systemctl list-timers --all | grep kairos-trap-cvm-fre
journalctl -u kairos-trap-cvm-fre.service -n 200 --no-pager
```
