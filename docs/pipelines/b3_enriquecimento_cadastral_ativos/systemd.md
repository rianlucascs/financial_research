# Systemd Timers - B3 Enriquecimento Cadastral de Ativos

Comandos para configurar uma execucao unica do pipeline de enriquecimento cadastral de ativos da B3.

---

### 1.1 Criar service

```bash
sudo tee /etc/systemd/system/kairos-trap-b3-cad.service > /dev/null <<'EOF
[Unit]
Description=Kairos Trap - B3 CAD
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=rian
WorkingDirectory=/home/rian/kairos-trap/docker
ExecStart=/usr/bin/docker compose -f /home/rian/kairos-trap/docker/docker-compose.yml run --rm b3-cad-pipeline
EOF
```

### 1.2 Criar timer

```bash
sudo tee /etc/systemd/system/kairos-trap-b3-cad.timer > /dev/null <<'EOF
[Unit]
Description=Timer - B3 CAD

[Timer]
OnCalendar=2026-09-01 22:00:00
Persistent=true
Unit=kairos-trap-b3-cad.service

[Install]
WantedBy=timers.target
EOF
```

### 1.3 Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kairos-trap-b3-cad.timer
```

O timer dispara uma unica vez em 1 de setembro de 2026, as 22:00:00. Depois da execucao, desative-o para evitar que permaneça habilitado sem proxima ocorrencia:

```bash
sudo systemctl disable --now kairos-trap-b3-cad.timer
```

### 1.4 Verificar

```bash
systemctl status kairos-trap-b3-cad.timer
systemctl list-timers --all | grep kairos-trap-b3-cad
journalctl -u kairos-trap-b3-cad.service -n 200 --no-pager
```