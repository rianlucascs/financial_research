

from datetime import date


URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/"


# Lista de arquivos zip a serem baixados, um para cada ano de 2011 até o ano atual.
ARCHIVES_ZIP = [f'itr_cia_aberta_{year_now}.zip' for year_now in range(2011, date.today().year + 1)]


# Lista de demonstracoes financeiras padronizadas (DFPs) a serem processadas.
DEMONSTRACOES = ['BPA_con', 'BPA_ind', 'BPP_con', 'BPP_ind', 
                'DFC_MD_con', 'DFC_MD_ind', 'DFC_MI_con', 
                'DFC_MI_ind', 'DMPL_con', 'DMPL_ind', 'DRA_con', 
                'DRA_ind', 'DRE_con', 'DRE_ind', 'DVA_con', 'DVA_ind']


# Constantes de checkpoint para o pipeline CVM demonstracoes financeiras padronizadas.
CHECKPOINT_STAGE_EXTRACT = "extract"
CHECKPOINT_STEP_DOWNLOAD_ZIP = "download_zip"
CHECKPOINT_STEP_EXTRACT_ZIP = "extract_zip"


# Constantes de checkpoint para o pipeline CVM demonstracoes financeiras padronizadas.
CHECKPOINT_STAGE_PROCESSED = "processed"
CHECKPOINT_STEP_PROCESSED_1 = "transform_1"
CHECKPOINT_STEP_PROCESSED_2 = "transform_2"


# Constantes de checkpoint para o estágio de load do pipeline CVM informações trimestrais.
CHECKPOINT_STAGE_LOAD = "load"
CHECKPOINT_STEP_LOAD = "load"


# Constantes de checkpoint para o pipeline CVM demonstracoes financeiras padronizadas.
DOWNLOAD_MAX_ATTEMPTS = 3
