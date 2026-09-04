# Systemd Timers

Comandos gerais para gerenciar os timers e services do systemd que agendam a execução dos pipelines CVM.

---

## Visualização de status

```bash
# Ver todos os timers relacionados ao projeto
systemctl list-timers --all | grep kairos-trap-

# Status dos timers
systemctl status kairos-trap-cvm-itr.timer
systemctl status kairos-trap-cvm-dfp.timer
```

## Execução manual

```bash
# Teste manual dos services
sudo systemctl start kairos-trap-cvm-itr.service
sudo systemctl start kairos-trap-cvm-dfp.service
```

## Logs

```bash
journalctl -u kairos-trap-cvm-itr.service -n 200 --no-pager
journalctl -u kairos-trap-cvm-dfp.service -n 200 --no-pager
```

## Recarregar e reiniciar

```bash
# Aplica alterações feitas nos arquivos de service/timer
sudo systemctl daemon-reload

# Reinicia os timers para que as mudanças tenham efeito
sudo systemctl restart kairos-trap-cvm-itr.timer
sudo systemctl restart kairos-trap-cvm-dfp.timer
```
