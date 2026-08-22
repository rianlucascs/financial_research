![alt text](banner.png)

# **Financial Research**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=flat&logo=duckdb&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat&logo=selenium&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=flat&logo=ubuntu&logoColor=white)


### Visão geral

O Financial Research é uma estrutura arquitetural reutilizável para organização e desenvolvimento de pipelines de dados. O projeto reúne interfaces, componentes compartilhados e convenções que orientam a extração, transformação, validação, persistência e operação dos dados. Os pipelines seguem uma estrutura comum, mas permanecem independentes para atender diferentes fontes, formatos e regras de negócio.

O projeto tem foco no mercado financeiro brasileiro, abrangendo dados financeiros nacionais, incluindo informações reguladas pela CVM e outras fontes relevantes do mercado.

### Objetivo

O objetivo é estabelecer uma base comum para desenvolver e manter pipelines de dados de forma consistente, reduzindo duplicação estrutural sem acoplar os pipelines às mesmas fontes ou regras de negócio. A arquitetura separa os componentes compartilhados das implementações específicas, permitindo a evolução dos pipelines existentes e a incorporação gradual de novos pipelines.

---

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

| Pipeline | Fonte dos dados | Descrição |
|---|---|---|
| `cvm_formulario_informacoes_trimestrais` | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/) | Extração e processamento dos dados do formulário ITR. |
| `cvm_formulario_demonstracoes_financeiras_padronizadas` | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/) | Extração e processamento dos dados do formulário DFP. |
| `cvm_cias_abertas_informacao_cadastral` | [CVM](https://dados.cvm.gov.br/dataset/cia_aberta-cad) | Extração e processamento dos dados de empresas abertas. |

---

# **Research**

A camada de Research é responsável pelo consumo e utilização dos dados produzidos pelos pipelines.

| Componente | Descrição |
|---|---|
| `research/` | Exploração e análise dos dados gerados pelos pipelines. |
| `streamlit_apps/` | Consumo e visualização dos dados em interface analítica. |

---

# **Topologia**

| Componente | Detalhe |
|---|---|
| OS | Ubuntu Server LTS |
| Acesso remoto | OpenSSH + VS Code Remote-SSH |
| Execução | Docker e Docker Compose |
| Armazenamento compartilhado | Samba — `/srv/data` |
| Agendamento | systemd timers |




