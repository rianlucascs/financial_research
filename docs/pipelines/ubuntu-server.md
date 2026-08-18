# Ubuntu Server — Configurações, Verificações e Monitoramento

Comandos do Ubuntu Server para configuração do sistema, verificação de data e hora, tempo de atividade e monitoramento de recursos de hardware.

---

```bash
# Verificar data/hora atual
date

# Definir fuso horário
sudo timedatectl set-timezone America/Sao_Paulo

# Confirmar configuração aplicada
timedatectl status
```

```bash
# Mostra a data e hora exata em que o sistema foi ligado (boot time).
uptime -s
```

```bash
# Monitoramento de hardware: Mostra o uso atual da CPU, da memória RAM e da memória Swap 
htop -s
```