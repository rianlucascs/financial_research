"""
Settings:
    pipeline_settings

Responsabilidades:
    Variáveis e funções de `configuração` do pipeline `cvm_formulario_demonstracoes_financeiras_padronizadas`.
    
    - Listar os arquivos zip a serem baixados, um para cada ano de 2011 até o ano atual.
    - Listar os códigos de demonstrações financeiras padronizadas (CVM) a serem processadas.
    - Acessar o caminho do snapshot atual.
    
Notas:
    ...
"""


from datetime import date
from pathlib import Path


# Lista de arquivos zip a serem baixados, um para cada ano de 2011 até o ano atual.
build_archives_zip = [f'itr_cia_aberta_{year_now}.zip' for year_now in range(2011, date.today().year + 1)]


# Lista de códigos de demonstrações financeiras padronizadas (CVM) a serem processadas.
demonstration_codes: list[str] = [
    'BPA_con', 'BPA_ind', 
    'BPP_con', 'BPP_ind', 
    'DFC_MD_con', 'DFC_MD_ind', 
    'DFC_MI_con', 'DFC_MI_ind', 
    'DMPL_con', 'DMPL_ind', 
    'DRA_con', 'DRA_ind', 
    'DRE_con', 'DRE_ind', 
    'DVA_con', 'DVA_ind'
    ]


def current_snapshot_path(pipeline, current_date: str | None = None) -> Path:
    """Retorna o caminho do snapshot atual.
    
    Returns:
        Path(pipeline) / date.today().strftime("%Y-%m-%d"): Caminho do snapshot atual.
    """
    
    if current_date is None:
        current_date = date.today().strftime("%Y-%m-%d")
        
    return Path(pipeline) / current_date

