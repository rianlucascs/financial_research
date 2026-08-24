"""
Settings:
    pipeline_settings

Responsabilidades:
    - Definir as configurações do pipeline `cvm_cias_abertas_informacao_cadastral`, 
    incluindo a URL base para baixar o arquivo CSV do site da CVM (Comissão de Valores Mobiliários) e o nome do arquivo CSV a ser baixado.
    
Notas:
    ...
"""

url: str = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"

filename: str = "cad_cia_aberta.csv"