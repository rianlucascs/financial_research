# **Financial Research**

## Sobre o projeto

Repositório para coleta, processamento e análise de dados financeiros públicos brasileiros.
Os pipelines (ETL) alimentam os notebooks de pesquisa quantitativa com dados de mercado, balanços e indicadores macroeconômicos.

## Como usar

### Research (notebooks)

Os notebooks ficam em `research/` e consomem os dados gerados pelos pipelines.
Execute localmente após instalar as dependências abaixo.

Exemplos disponíveis:
- [research/notebooks/01.01 selic.ipynb](research/notebooks/01.01%20selic.ipynb) - visão geral da série histórica da Selic.
- [research/notebooks/01.06 beta+segmentos_setoriais.ipynb](research/notebooks/01.06%20beta%2Bsegmentos_setoriais.ipynb) - cálculo de beta por ativo versus IBOVESPA e análise por segmento.
- [research/notebooks/02.01 mapa.ipynb](research/notebooks/02.01%20mapa.ipynb) - consolidação de indicadores (drawdown, beta, regressão e retorno mensal) em um mapa único.

### Readers

As classes de leitura para consumo dos dados gerados pelos pipelines ficam em `pipelines/readers/`.
Há readers para acesso via CSV e via SQLite, dependendo do pipeline.

→ [pipelines/readers/README.md](pipelines/readers/README.md)

### Operacao

Existe um checklist operacional separado para validacao do servidor, Docker, timers e logs apos reboot ou manutencao.

→ [README.operations.md](README.operations.md)

### Backup

Existe um guia separado para backup do projeto em outro computador da mesma rede com `rsync`, `ssh` e `systemd timer`.

→ [README.backup.md](README.backup.md)

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

### Configurar fuso horário do servidor

```bash
# Verificar data/hora atual
date

# Definir fuso horário
sudo timedatectl set-timezone America/Sao_Paulo

# Confirmar configuração aplicada
timedatectl status
```

### Pipelines (ETL)

Os pipelines coletam e processam dados financeiros públicos e são executados via Docker. Veja também: [README.Docker.md](README.Docker.md)

#### BCB — Histórico de Taxas de Juros

Extrai o histórico de reuniões do COPOM e as taxas Selic (meta e over) diretamente da página do Banco Central do Brasil via Selenium, salvando em CSV e carregando os dados em um banco SQLite para consumo por readers CSV e SQL.

→ [pipelines/scripts/bcb_historico_taxas_juros/README.md](pipelines/scripts/bcb_historico_taxas_juros/README.md)

#### B3 — Índices e Segmentos Setoriais

Baixa as carteiras diárias dos índices da B3, salva os CSVs brutos por índice e consolida os dados em um banco SQLite para consumo por readers CSV e SQL.

→ [pipelines/scripts/b3_indices_segmentos_setoriais/README.md](pipelines/scripts/b3_indices_segmentos_setoriais/README.md)

#### CVM — Formulário de Informações Trimestrais (ITR)

Baixa, consolida e carrega as informações trimestrais de companhias abertas publicadas pela CVM, organizando por empresa em um banco de dados SQLite para consumo por readers CSV e SQL.

→ [pipelines/scripts/cvm_formulario_informacoes_trimestrais/README.md](pipelines/scripts/cvm_formulario_informacoes_trimestrais/README.md)

#### CVM — Formulário de Demonstrações Financeiras Padronizadas (DFP)

Baixa, consolida e carrega as demonstrações financeiras anuais de companhias abertas publicadas pela CVM, organizando por empresa em um banco de dados SQLite para consumo por readers CSV e SQL.

→ [pipelines/scripts/cvm_formulario_demonstracoes_financeiras_padronizadas/README.md](pipelines/scripts/cvm_formulario_demonstracoes_financeiras_padronizadas/README.md)

# Topologia

| Componente | Detalhe |
|---|---|
| OS | Ubuntu Server LTS |
| Acesso remoto | OpenSSH + VS Code Remote-SSH |
| Execução | Docker e Compose |
| Armazenamento compartilhado | Samba — `/srv/data` |
| Agendamento | systemd timers → [README.systemd.md](README.systemd.md) |