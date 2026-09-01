# **kairos-trap**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=flat&logo=duckdb&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat&logo=selenium&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=flat&logo=ubuntu&logoColor=white)


### Visão geral

O kairos-trap coleta e processa dados públicos do mercado financeiro brasileiro — CVM, B3 e outras fontes — através de pipelines de ETL. O projeto reúne interfaces, componentes compartilhados e convenções que orientam extração, transformação, validação e persistência dos dados, mantendo os pipelines independentes entre si para atender diferentes fontes, formatos e regras de negócio.

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
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `cvm_formulario_informacoes_trimestrais`                | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/)                                   | Extração e processamento dos dados do formulário ITR.                                            |
| `cvm_formulario_demonstracoes_financeiras_padronizadas` | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/)                                   | Extração e processamento dos dados do formulário DFP.                                            |
| `cvm_cias_abertas_informacao_cadastral`                 | [CVM](https://dados.cvm.gov.br/dataset/cia_aberta-cad)                                            | Extração e processamento das informações cadastrais de companhias abertas.                       |
| `cvm_formulario_de_referencia`                          | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/)                                   | Extração e processamento dos dados do formulário FRE.                                            |
| `cvm_informacoes_periodicas_e_eventuais` — *dev*        | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/DADOS/)                                   | Extração e processamento das informações periódicas e eventuais divulgadas pelas companhias.     |
| `cvm_formulario_cadastral` — *dev*                      | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/)                                   | Extração e processamento dos dados do formulário FCA.                                            |
| `cvm_valores_mobiliarios_ofertados` — *dev*             | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/VLMO/DADOS/)                                  | Extração e processamento dos dados de valores mobiliários ofertados.                             |
| `google_noticias_mercado` — *dev*                       | [Google](https://news.google.com/)                                                           | Extração e processamento de notícias relacionadas ao mercado financeiro.                         |
| `b3_enriquecimento_cadastral_ativos` — *dev* | [B3](https://www.b3.com.br/)                                                           | Extração e processamento de informações complementares para enriquecimento cadastral e identificação de ativos financeiros. |
| `b3_indices_segmentos_setoriais` — *dev*                | [B3](https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-de-segmentos-e-setoriais/) | Extração e processamento da composição dos índices de segmentos e setoriais.                     |
| `social_monitoramento_agentes_de_mercado` — dev | [Redes sociais]() | Monitoramento e processamento de publicações de agentes de mercado em redes sociais.

---

# **Research**

A camada de Research é responsável pelo consumo e utilização dos dados produzidos pelos pipelines.

| Componente | Descrição |
|---|---|
| `research/` | Exploração e análise dos dados gerados pelos pipelines. |
| `streamlit_apps/` | Consumo e visualização dos dados em interface analítica. |

### Apps disponíveis

| App | Descrição | Preview |
|---|---|---|
| `streamlit_app_pipelines` | Monitoramento operacional dos pipelines ETL, incluindo:<br>• Consulta de pipelines disponíveis<br>• Logs de execução<br>• Checkpoints organizados por pipeline, stage e step | [preview](docs/screenshots/streamlit_apps/streamlit_app_pipelines/page_overview.png) |
| `streamlit_app_research` | Aplicação analítica para pesquisa de mercado, incluindo:<br>• Monitoramento geral e setorial<br>• Acompanhamento de preços e retornos<br>• Avaliação de estratégias de investimento<br>• Análise de conjuntos de ativos<br>• Consulta de notícias por ativo<br>• Configuração de alertas | ![preview](caminho/para/imagem.png) |

---

# **Topologia**

| Componente | Detalhe |
|---|---|
| OS | Ubuntu Server LTS |
| Acesso remoto | OpenSSH + VS Code Remote-SSH |
| Execução | Docker e Docker Compose |
| Armazenamento compartilhado | Samba — `/srv/data` |
| Agendamento | systemd timers |




