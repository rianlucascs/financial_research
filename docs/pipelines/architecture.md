# Tree

    financial_research/
    ├── docker/                                            # Containers dos pipelines
    │   ├── `docker-compose.yml`                           # Serviços dos pipelines
    │   └── Dockerfile.pipelines                           # Imagem de execução
    ├── docs/                                              # Documentação operacional
    │   ├── pipelines/                                     # Guias por pipeline
    │   │   ├── b3_enriquecimento_cadastral_ativos/        # Documentação B3 cadastral
    │   │   ├── cvm_cias_abertas_informacao_cadastral/     # Documentação cadastro CVM
    │   │   ├── cvm_formulario_de_referencia/              # Documentação FRE
    │   │   ├── cvm_formulario_demonstracoes_financeiras_padronizadas/ # Documentação DFP
    │   │   ├── cvm_formulario_informacoes_trimestrais/    # Documentação ITR
    │   │   ├── docker.md                                  # Operação Docker geral
    │   │   ├── `pipeline_execution_schedule.md`           # Agenda de execuções
    │   │   ├── systemd.md                                 # Operação systemd geral
    │   │   └── ubuntu-server.md                           # Configuração do servidor
    │   └── screenshots/                                   # Capturas dos aplicativos
    ├── pipelines/                                         # Camada ETL
    │   ├── readers/                                       # Leitura de dados produzidos
    │   │   ├── pipelines/                                 # Readers por pipeline
    │   │   │   └── ...                                    # Padrão repetido em 5 pipelines
    │   │   ├── data_preparation/                          # Leitores de preparação
    │   │   └── historical_data/                           # Leitores de histórico
    │   ├── scripts/                                       # Implementações executáveis
    │   │   └── pipelines/                                 # Stages por pipeline
    │   │       ├── b3_enriquecimento_cadastral_ativos/    # Enriquecimento cadastral B3
    │   │       ├── cvm_cias_abertas_informacao_cadastral/ # Cadastro de companhias
    │   │       ├── cvm_formulario_de_referencia/          # Formulário de referência
    │   │       ├── cvm_formulario_demonstracoes_financeiras_padronizadas/ # DFP
    │   │       ├── cvm_formulario_informacoes_trimestrais/ # ITR
    │   │       └── ...                                    # Padrão repetido em 5 pipelines
    │   └── shared/                                        # Infraestrutura ETL comum
    │       ├── interfaces/                                # Contratos e classes base
    │       ├── utils/                                     # Utilitários compartilhados
    │       ├── checkpoint_contract.py                     # Contrato de checkpoints
    │       ├── `checkpoint_values.py`                     # Enums de checkpoints
    │       ├── checkpoint_writer_mixin.py                 # Persistência de checkpoints
    │       └── context.py                                 # Contexto de execução
    ├── research/                                          # Estudos e análises
    │   ├── exploratory_analysis/                          # Exploração de dados
    │   └── research_studies/                              # Estudos especializados
    ├── streamlit_apps/                                    # Aplicativos analíticos
    │   └── apps/
    │       ├── streamlit_app_pipelines/                   # Monitoramento ETL
    │       └── streamlit_app_research/                    # Pesquisa financeira
    ├── `README.md`                                        # Visão geral do projeto
    ├── `pyproject.toml`                                   # Metadados e empacotamento
    ├── `requirements.pipelines.txt`                       # Dependências ETL
    └── `teste_logica.py`                                  # Testes experimentais
