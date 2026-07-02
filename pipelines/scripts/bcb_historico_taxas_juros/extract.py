

from .settings import (
    CHECKPOINT_STAGE_EXTRACT,
    CHECKPOINT_STEP_DOWNLOAD,
    URL
)

from pipelines.shared.checkpoint_values import (
    STATUS_SUCCESSFUL,
    STATUS_FAILED,
    STATUS_NO_FILE_DETECTED,
    FAILURE_NETWORK_ERROR,
    FAILURE_DRIVER_CREATION,
    FAILURE_IO_ERROR
)

from pipelines.shared.checkpoint_contract import build_checkpoint_payload
from pipelines.shared.selenium_utils import SeleniumUtils

from time import sleep
from selenium.webdriver.common.by import By
import gc
from pandas import DataFrame


class ExtractBCBHistoricoTaxasJurosSettings:
    
    
    def __init__(self, pipeline):

        self.pipeline = pipeline
        self.process = "extract"
        self.logger = None
        self.driver = None
    

    def _gravar_checkpoint_extract(self, filename, raw_path, extension, status, failure_point, ctx):

        try:
            checkpoint = build_checkpoint_payload(
                pipeline=self.pipeline,
                stage=CHECKPOINT_STAGE_EXTRACT,
                step=CHECKPOINT_STEP_DOWNLOAD,
                status=status,
                run_id=ctx.run_id,
                environment=ctx.env,
                failure_point=failure_point,
                extra={
                    "downloaded_file": filename,
                    "download_path": str(raw_path),
                    "downloaded_extension": extension,
                },
            )

            ctx.write_checkpoint(
                self.pipeline, 
                CHECKPOINT_STAGE_EXTRACT, 
                CHECKPOINT_STEP_DOWNLOAD, 
                filename, 
                checkpoint)
        
        except Exception as e:
            
            self.logger.exception(f"Falha ao gravar checkpoint para {filename}: {e}")
        
        
    def _extract(self, ctx):
        
        self.logger.info("Iniciando a extração do histórico de taxas de juros do Banco Central do Brasil")
        
        selenium_utils = SeleniumUtils(ctx=ctx)
        
        # Configura o caminho para salvar o arquivo CSV
        raw_path = ctx.prepare_raw_path(self.pipeline)
        filename = 'bcb_historico_taxas_juros'
        raw_path_filename = raw_path / f"{filename}.csv"
        
        try:
            
            # Cria o driver do Selenium 
            self.driver = selenium_utils.driver(
                download_path=None, 
                incognito=False, 
                user_agent="agente_1",
                disable_gpu=True
            ) 
            
            self.logger.info("Acessando a URL do Banco Central do Brasil para extração de dados")
            self.driver.get(URL)
            
            # Aguardar o carregamento da página
            sleep(5)
            
        except Exception as e:
            
            self.logger.exception(f"Falha ao criar o driver do Selenium: {e}") 
            
            self._gravar_checkpoint_extract(
                filename=filename,
                raw_path=None,
                extension=None,
                status=STATUS_FAILED,
                failure_point=FAILURE_DRIVER_CREATION,
                ctx=ctx
            )
            
            raise RuntimeError("Driver Selenium não inicializado")

        # Localiza todas as linhas da tabela de dados
        rows = selenium_utils.find(self.driver, 'tr', find_all=True, by=By.TAG_NAME, visible=False, wait=20)

        if len(rows) <= 20:
            
            self.logger.error("Nenhuma linha de dados encontrada na tabela.")
            
            self._gravar_checkpoint_extract(
                filename=filename,
                raw_path=None,
                extension=None,
                status=STATUS_NO_FILE_DETECTED,
                failure_point=FAILURE_NETWORK_ERROR,
                ctx=ctx
            )
            
            raise ValueError("Nenhuma linha de dados encontrada na tabela.")

        data = []
        
        for i, row in enumerate(rows):
            if i > 1:
                data.append(
                    {
                        'Reunião': selenium_utils.find(row, 'td:nth-child(1)', by=By.CSS_SELECTOR).text,
                        'Data da Reunião': selenium_utils.find(row, 'td:nth-child(2)', by=By.CSS_SELECTOR).text,
                        'Data da Divulgação': selenium_utils.find(row, 'td:nth-child(3)', by=By.CSS_SELECTOR).text,
                        'Período de Vigência': selenium_utils.find(row, 'td:nth-child(4)', by=By.CSS_SELECTOR).text,
                        'Taxa Selic Meta (%)': selenium_utils.find(row, 'td:nth-child(5)', by=By.CSS_SELECTOR).text,
                        'Taxa Selic Over (%)': selenium_utils.find(row, 'td:nth-child(6)', by=By.CSS_SELECTOR).text,
                        'Taxa Selic Meta Anterior (%)': selenium_utils.find(row, 'td:nth-child(7)', by=By.CSS_SELECTOR).text,
                        'Taxa Selic Over Anterior (%)': selenium_utils.find(row, 'td:nth-child(8)', by=By.CSS_SELECTOR).text,  
                    }
                )

        try:
            
            df = DataFrame(data)      
        
            df.to_csv(raw_path / "bcb_historico_taxas_juros.csv", index=False, encoding='utf-8-sig')
            
            del data
            del df
            
            gc.collect()
            
            self.logger.info(f"CSV salvo com sucesso em: {raw_path / 'bcb_historico_taxas_juros.csv'}")
            
            self._gravar_checkpoint_extract(
                filename=filename,
                raw_path=raw_path_filename,
                extension='csv',
                status=STATUS_SUCCESSFUL,
                failure_point=None,
                ctx=ctx
            )
            
            self.logger.info("Extração concluída com sucesso.")
        
        except Exception as e:
            
            self._gravar_checkpoint_extract(
                filename=filename,
                raw_path=None,
                extension=None,
                status=STATUS_FAILED,
                failure_point=FAILURE_IO_ERROR,
                ctx=ctx
            )
            
            self.logger.exception(f"Falha ao salvar CSV: {e}")
            
            
    def main(self, ctx):
    
        # Configura o logger e o ambiente
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        if ctx.env == "dev":
            pass
        
        if ctx.env == "prod": 
            pass
        
        # Inicia o processo de extração
        self._extract(ctx=ctx)
        
        

