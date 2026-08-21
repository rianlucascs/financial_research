"""
Settings:
    pipeline_settings

Responsabilidades:
    Variáveis de `configuração` do pipeline `cvm_cias_abertas_informacao_cadastral`.
    
    - Url de download do arquivo CSV.
    - Nome do arquivo CSV.
    
Notas:
    ...
"""

url: str = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"

filename: str = "cad_cia_aberta.csv"