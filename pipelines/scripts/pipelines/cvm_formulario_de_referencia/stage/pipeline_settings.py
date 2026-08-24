"""
Settings:
    pipeline_settings

Responsabilidades:
    - Definir as configurações do pipeline `cvm_formulario_de_referencia`, 
    incluindo a URL base para baixar os arquivos ZIP do site da CVM (Comissão de Valores Mobiliários) 
    e a lista de arquivos ZIP a serem baixados, um para cada ano de 2011 até o ano atual.
    
Notas:
    ...
"""


from datetime import date


# URL base para baixar os arquivos ZIP do site da CVM (Comissão de Valores Mobiliários).
url: str = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/"


# Lista de arquivos zip a serem baixados, um para cada ano de 2011 até o ano atual.
build_archives_zip = [f'fre_cia_aberta_{year_now}.zip' for year_now in range(2010, date.today().year + 1)]


