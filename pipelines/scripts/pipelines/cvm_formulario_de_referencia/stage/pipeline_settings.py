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


file_prefix: str = "fre_cia_aberta"


start_year: int = 2010


# Lista de arquivos zip a serem baixados, um para cada ano de 2011 até o ano atual.
build_archives_zip = [f'{file_prefix}_{year_now}.zip' for year_now in range(start_year, date.today().year + 1)]


file_identifiers = [
    "",  # arquivo base: fre_cia_aberta_<ANO>.parquet
    "acao_entregue",
    "administrador_PCD",
    "administrador_declaracao_genero",
    "administrador_declaracao_raca",
    "administrador_membro_conselho_fiscal",
    "ativo_imobilizado",
    "ativo_intangivel",
    "auditor",
    "auditor_responsavel",
    "capital_social",
    "capital_social_aumento",
    "capital_social_aumento_classe_acao",
    "capital_social_classe_acao",
    "capital_social_desdobramento",
    "capital_social_desdobramento_classe_acao",
    "capital_social_reducao",
    "capital_social_reducao_classe_acao",
    "capital_social_titulo_conversivel",
    "direito_acao",
    "distribuicao_capital",
    "distribuicao_capital_classe_acao",
    "distribuicao_dividendos",
    "distribuicao_dividendos_classe_acao",
    "empregado_PCD",
    "empregado_local_declaracao_genero",
    "empregado_local_declaracao_raca",
    "empregado_local_faixa_etaria",
    "empregado_posicao_declaracao_genero",
    "empregado_posicao_declaracao_raca",
    "empregado_posicao_faixa_etaria",
    "empregado_posicao_local",
    "endividamento",
    "grupo_economico_reestruturacao",
    "historico_emissor",
    "informacao_financeira",
    "membro_comite",
    "mercado_estrangeiro",
    "obrigacao",
    "outro_valor_mobiliario",
    "participacao_sociedade",
    "participacao_sociedade_valorizacao_acao",
    "plano_recompra",
    "plano_recompra_classe_acao",
    "politica_negociacao",
    "politica_negociacao_cargo",
    "posicao_acionaria",
    "posicao_acionaria_classe_acao",
    "relacao_familiar",
    "relacao_subordinacao",
    "remuneracao_acao",
    "remuneracao_maxima_minima_media",
    "remuneracao_total_orgao",
    "remuneracao_variavel",
    "responsavel",
    "titular_valor_mobiliario",
    "titulo_exterior",
    "transacao_parte_relacionada",
    "valor_mobiliario_tesouraria_movimentacao",
    "valor_mobiliario_tesouraria_ultimo_exercicio",
    "volume_valor_mobiliario",
]