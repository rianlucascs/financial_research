# Responsabilidade do AssetRepository: servir informação estática/cadastral sobre os ativos

class AssetRepository:
    """
    Fornece acesso somente-leitura aos metadados cadastrais dos ativos
    (nome, ticker, setor, CNPJ, tipo de ativo, etc.), agregando dados
    provenientes das pipelines CVM/BCB já processadas.
    """