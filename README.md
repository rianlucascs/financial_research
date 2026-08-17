# **Financial Research**

### Visão geral

Plataforma de engenharia de dados para extração, processamento, validação e persistência de diferentes tipos de dados provenientes de diversas fontes. O projeto é estruturado para receber dados brutos, transformá-los em fluxos padronizados e disponibilizá-los para consumo em camadas posteriores de análise e exploração.

### Objetivo

Organizar uma arquitetura reutilizável para ingestão, processamento e persistência de dados, mantendo uma separação clara entre a obtenção dos dados e a sua utilização em pesquisa e análise. Os dados produzidos pelos pipelines são utilizados por componentes de Research para exploração, consulta e consumo analítico.
 
# **Pipelines**
A camada de pipelines é responsável pela aquisição, preparação e persistência dos dados.

| Pipeline | Descrição |
|---|---|
| `cvm_formulario_informacoes_trimestrais` | Extração e processamento dos dados do formulário ITR. |
| `cvm_formulario_demonstracoes_financeiras_padronizadas` | Extração e processamento dos dados do formulário DFP. |

---

# **Research**

A camada de Research é responsável pelo consumo e utilização dos dados produzidos pelos pipelines.

| Componente | Descrição |
|---|---|
| `research/` | Diretório de exploração e análise dos dados gerados pelos pipelines. |
| `streamlit_apps/` | Aplicações para consumo e visualização dos dados em interface analítica. |

## **Topologia**

| Componente | Detalhe |
|---|---|
| OS | Ubuntu Server LTS |
| Acesso remoto | OpenSSH + VS Code Remote-SSH |
| Execução | Docker e Docker Compose |
| Armazenamento compartilhado | Samba — `/srv/data` |
| Agendamento | systemd timers |


