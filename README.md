# **Financial Research**

## Como usar

### Research (notebooks)

## Instalação no Ubuntu Server

```bash
# 1. Atualize os repositórios
sudo apt update

# 2. Instale o Python 3.10 e os pacotes necessários
sudo apt install -y python3.10 python3.10-venv python3-pip

# 3. Verifique a instalação
python3.10 --version

# 4. Clone o repositório
git clone https://github.com/rianlucascs/financial_research.git
cd financial_research

# 5. Crie o ambiente virtual com Python 3.10
python3.10 -m venv .venv

# 6. Ative o ambiente virtual
source .venv/bin/activate

# 7. Atualize as ferramentas de empacotamento
python -m pip install --upgrade pip setuptools wheel

# 8. Instale as dependências
python -m pip install -r requirements.research.txt

# 9. Instale o pacote local em modo editável
python -m pip install -e .
```

### Pipelines (ETL)

(...)

# Topologia

- Ubuntu Server LTS

- Openssh-server

- Docker e Compose

- VS Code Remote-SSH

- Pasta Samba
/srv/data

- Agende tarefas:
cron ou systemd timers