# **Financial Research**

### Visão geral

Plataforma de engenharia de dados para extração, processamento, validação e persistência de diferentes tipos de dados provenientes de diversas fontes. O projeto é estruturado para receber dados brutos, transformá-los em fluxos padronizados e disponibilizá-los para consumo em camadas posteriores de análise e exploração.

### Objetivo

Organizar uma arquitetura reutilizável para ingestão, processamento e persistência de dados, com separação clara entre produção e consumo dos dados. A solução foi concebida para evoluir com novos pipelines e fontes sem depender de uma estrutura específica de origem.
  
# **Pipelines**

A camada de pipelines é responsável pela aquisição, preparação e persistência dos dados.

### Processos ETL

| Processo | Descrição |
|---|---|
| `extract` | Aquisição dos dados de origem e armazenamento dos arquivos brutos. |
| `to_interim` | Padronização inicial dos dados e organização em uma camada intermediária. |
| `to_processed` | Transformação e consolidação dos dados para a camada processada. |
| `load` | Persistência dos dados no destino configurado do pipeline. |
| `compare` | Comparação entre snapshots para identificar alterações e diferenças. |
| `retention` | Aplicação da política de retenção de dados e logs do projeto. |

### Pipelines disponíveis

| Pipeline | Descrição |
|---|---|
| `cvm_formulario_informacoes_trimestrais` | Extração e processamento dos dados do formulário ITR. |
| `cvm_formulario_demonstracoes_financeiras_padronizadas` | Extração e processamento dos dados do formulário DFP. |

---

# **Research**

A camada de Research é responsável pelo consumo e utilização dos dados produzidos pelos pipelines.

| Componente | Descrição |
|---|---|
| `research/` | Exploração e análise dos dados gerados pelos pipelines. |
| `streamlit_apps/` | Consumo e visualização dos dados em interface analítica. |

# **Topologia**

| Componente | Detalhe |
|---|---|
| OS | Ubuntu Server LTS |
| Acesso remoto | OpenSSH + VS Code Remote-SSH |
| Execução | Docker e Docker Compose |
| Armazenamento compartilhado | Samba — `/srv/data` |
| Agendamento | systemd timers |


