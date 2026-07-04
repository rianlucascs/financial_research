

from .settings import (
    B3_INDICES,
    CHECKPOINT_STAGE_EXTRACT,
    CHECKPOINT_STEP_DOWNLOAD,
)

from pipelines.shared.checkpoint_values import (
    STATUS_SUCCESSFUL,
    STATUS_FAILED,
    STATUS_NO_FILE_DETECTED,
    STATUS_DRIVER_ERROR,
    FAILURE_DRIVER_CREATION,
    FAILURE_FILE_DETECTION,
    FAILURE_DOWNLOAD_BUTTON_NOT_FOUND,
) 

from pipelines.shared.selenium_utils import SeleniumUtils
from pipelines.shared.checkpoint_contract import build_checkpoint_payload

from time import sleep
from selenium.webdriver.common.by import By
from shutil import rmtree


class ExtractB3IndicesSegmentosSetoriais:
    
    
    def __init__(self, pipeline):
        
        self.pipeline = pipeline
        self.process = "extract"
        self.logger = None
        self.driver = None

    
    def _gravar_checkpoint_extract(self, indice, filename, extension, status, failure_point, attempts, ctx):
        
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
                    "indice": indice,
                    "downloaded_file": filename,
                    "downloaded_extension": extension,
                    "attempts": attempts,
                },
            )

            ctx.write_checkpoint(
                self.pipeline, 
                CHECKPOINT_STAGE_EXTRACT, 
                CHECKPOINT_STEP_DOWNLOAD, 
                indice, 
                checkpoint)
            
            self.logger.info(f"Checkpoint gravado para {indice}")

        except Exception as e:

            self.logger.exception(f"Falha ao gravar checkpoint para {indice}: {e}")


    def _extract(self, ctx):
        
        selenium_utils = SeleniumUtils(ctx)
        
        # Inicializa o contador para percorrer os índices da B3
        contador = 0
        
        while (contador < len(B3_INDICES)):
            
            indice = B3_INDICES[contador]
            
            self.logger = ctx.logger.getChild(indice)
            
            filename = None
            extension = None
            tentativas_driver = 0
            driver_criado = False
            self.driver = None
            
            raw_path = ctx.prepare_raw_path(pipeline=self.pipeline, type_file=indice)
            
            if raw_path.exists() and any(raw_path.iterdir()):
            
                self.logger.info(f"Arquivos antigos detectados em {raw_path}. Limpando o diretório antes de iniciar a extração.")
            
                # Limpa somente o conteúdo de raw_path, preservando o diretório base.
                for item in raw_path.iterdir():
                    if item.is_dir():
                        rmtree(item)
                    else:
                        item.unlink(missing_ok=True)
            
            max_tentativas_para_criar_driver = 3
            
            while tentativas_driver < max_tentativas_para_criar_driver:

                try:
                    # Incrementa o contador de tentativas antes de tentar criar o driver e acessar a página.
                    tentativas_driver += 1

                    self.driver = selenium_utils.driver(
                        download_path=str(raw_path),
                        disable_gpu=True,
                        incognito=False,
                        disable_sandbox=True,
                        user_agent="agente_1",
                    )

                    self.logger.info(
                        f"Iniciando a extração do índice {indice} da B3 "
                        f"(tentativa {tentativas_driver}/{max_tentativas_para_criar_driver})"
                    )

                    url = f"https://sistemaswebb3-listados.b3.com.br/indexPage/day/{indice}?language=pt-br"
                    self.driver.get(url)

                    # Aguarda o carregamento da página e a presença do botão de download.
                    sleep(selenium_utils.random_delay)

                    driver_criado = True
                    break

                except Exception as e:

                    self.logger.exception(f"Falha na extração do índice {indice} (tentativa {tentativas_driver}/{max_tentativas_para_criar_driver}): {e}")

                    if tentativas_driver < max_tentativas_para_criar_driver:
                        sleep(selenium_utils.random_delay)
                    
                    else:
                        
                        self._gravar_checkpoint_extract(
                            indice=indice,
                            filename=filename,
                            extension=extension,
                            status=STATUS_DRIVER_ERROR,
                            failure_point=FAILURE_DRIVER_CREATION,
                            attempts=tentativas_driver,
                            ctx=ctx,
                        )

                        self.logger.error(f"Falha definitiva para índice {indice} após {tentativas_driver} tentativa(s). Seguindo para o próximo índice.")

                        # Garante encerramento do navegador em sucesso e falha.
                        if self.driver is not None:
                            selenium_utils.quit(self.driver)
                        
                        sleep(selenium_utils.random_delay)
                        
                        # Incrementa o contador para passar para o próximo índice, mesmo após falha.
                        contador += 1
                        continue

            if driver_criado:
                
                tentativas_download = 0
                max_tentativas_download = 10
                
                while tentativas_download < max_tentativas_download:
                    
                    try:
                    
                        # Incrementa o contador de tentativas antes de tentar clicar no botão de download.
                        tentativas_download += 1
                        
                        self.logger.info(f"Tentativa de download {tentativas_download}/{max_tentativas_download} para {indice}...")
                        
                        # Clica no botão de download usando o SeleniumUtils.
                        selenium_utils.safe_click(self.driver, 'Download', wait=15, by=By.LINK_TEXT)

                        sleep(selenium_utils.random_delay)
                        
                        # Aguarda o arquivo aparecer no diretório de download.
                        latest = None
                        tentativas_arquivo = 0
                        max_tentativas_arquivo = 5
                        
                        while tentativas_arquivo < max_tentativas_arquivo:
                            arquivos = [f for f in raw_path.iterdir() if f.is_file()]
                            if arquivos:
                                latest = max(arquivos, key=lambda f: f.stat().st_mtime)
                                break
                            tentativas_arquivo += 1
                            
                            sleep(selenium_utils.random_delay)
                            
                            self.logger.info(f"Aguardando arquivo de download para {indice} (tentativa {tentativas_arquivo}/{max_tentativas_arquivo})...")

                        if latest is None:
                            raise FileNotFoundError(f"Nenhum arquivo baixado detectado em {raw_path}")
                        
                        filename = latest.stem
                        extension = latest.suffix

                        self._gravar_checkpoint_extract(
                            indice=indice,
                            filename=filename,
                            extension=extension,
                            status=STATUS_SUCCESSFUL,
                            failure_point=None,
                            attempts=tentativas_download,
                            ctx=ctx,
                        )
                        
                        self.logger.info(f"Download bem-sucedido para {indice}: {filename}{extension}")
                        
                        break  # Sai do loop de tentativas de download após sucesso
                    
                    except Exception as e:
                        
                        self.logger.exception(f"Falha ao clicar no botão de download para {indice} (tentativa {tentativas_download}/{max_tentativas_download}): {e}")
                        
                        # Se atingiu o número máximo de tentativas, registra o checkpoint e segue para o próximo índice.
                        if tentativas_download >= max_tentativas_download:
                            
                            status = STATUS_FAILED
                            failure_point = FAILURE_DOWNLOAD_BUTTON_NOT_FOUND
                            
                            if isinstance(e, FileNotFoundError):
                                status = STATUS_NO_FILE_DETECTED
                                failure_point = FAILURE_FILE_DETECTION

                            self._gravar_checkpoint_extract(
                                indice=indice,
                                filename=filename,
                                extension=extension,
                                status=status,
                                failure_point=failure_point,
                                attempts=tentativas_download,
                                ctx=ctx,
                            )
                            
                            self.logger.error(f"Falha definitiva ao tentar baixar o índice {indice} após {tentativas_download} tentativa(s). Seguindo para o próximo índice.")
                            
                            # Garante encerramento do navegador em sucesso e falha.
                            if self.driver is not None:
                                selenium_utils.quit(self.driver)
                            
                            sleep(selenium_utils.random_delay)
                            
                            break  # Sai do loop de tentativas de download após falha definitiva

                self.logger.info(f"Finalizando a extração do índice {indice}. ")

                # Garante encerramento do navegador em sucesso e falha.
                if self.driver is not None:
                    selenium_utils.quit(self.driver)
                            
                sleep(selenium_utils.random_delay)
                            
                # Incrementa o contador para passar para o próximo índice após sucesso ou falha definitiva.
                contador += 1
                continue
            
            else:
                
                pass
            
            
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