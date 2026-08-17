# Systemd Timers

Comandos gerais para gerenciar os timers e services do systemd que agendam a execução dos pipelines CVM.

---

## Visualização de status

```bash
# Ver todos os timers relacionados ao projeto
systemctl list-timers --all | grep financial-research-

# Status dos timers
systemctl status financial-research-cvm-itr.timer
systemctl status financial-research-cvm-dfp.timer
```

## Execução manual

```bash
# Teste manual dos services
sudo systemctl start financial-research-cvm-itr.service
sudo systemctl start financial-research-cvm-dfp.service
```

## Logs

```bash
journalctl -u financial-research-cvm-itr.service -n 200 --no-pager
journalctl -u financial-research-cvm-dfp.service -n 200 --no-pager
```

## Recarregar e reiniciar

```bash
# Aplica alterações feitas nos arquivos de service/timer
sudo systemctl daemon-reload

# Reinicia os timers para que as mudanças tenham efeito
sudo systemctl restart financial-research-cvm-itr.timer
sudo systemctl restart financial-research-cvm-dfp.timer
```
