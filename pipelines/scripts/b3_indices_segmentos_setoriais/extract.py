

from .settings import (
    B3_INDICES,
    CHECKPOINT_STAGE_EXTRACT,
    CHECKPOINT_STEP_DOWNLOAD,
    DOWNLOAD_MAX_ATTEMPTS,
)

from pipelines.shared.checkpoint_values import (
    STATUS_SUCCESSFUL,
    STATUS_FAILED,
    STATUS_NO_FILE_DETECTED,
    STATUS_DRIVER_ERROR,
    FAILURE_DRIVER_CREATION,
    FAILURE_FILE_DETECTION,
    FAILURE_VALIDATION,
    FAILURE_EXCEPTION,
    FAILURE_DOWNLOAD_BUTTON_NOT_FOUND,
) 

from pipelines.shared.selenium_utils import SeleniumUtils
from pipelines.shared.checkpoint_contract import build_checkpoint_payload

from time import sleep


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
         
        raw_path = ctx.prepare_raw_path(self.pipeline)
        
        # Inicializa o contador para percorrer os índices da B3
        contador = 0
        
        while (contador < len(B3_INDICES)):
            
            indice = B3_INDICES[contador]
            
            filename = None
            extension = None
            tentativas = 0
            extraido_com_sucesso = False

            while tentativas < DOWNLOAD_MAX_ATTEMPTS:

                try:
                    # Incrementa o contador de tentativas antes de tentar criar o driver e acessar a página.
                    tentativas += 1

                    self.driver = selenium_utils.driver(
                        download_path=str(raw_path),
                        disable_gpu=True,
                        incognito=True,
                        disable_sandbox=True,
                        user_agent="agent_1",
                    )

                    self.logger.info(
                        f"Iniciando a extração do índice {indice} da B3 "
                        f"(tentativa {tentativas}/{DOWNLOAD_MAX_ATTEMPTS})"
                    )

                    url = f"https://sistemaswebb3-listados.b3.com.br/indexPage/day/{indice}?language=pt-br"
                    self.driver.get(url)

                    # Aguarda o carregamento da página e a presença do botão de download.
                    sleep(selenium_utils.random_delay)

                    self._gravar_checkpoint_extract(
                        indice=indice,
                        filename=filename,
                        extension=extension,
                        status=STATUS_SUCCESSFUL,
                        failure_point=None,
                        attempts=tentativas,
                        ctx=ctx,
                    )

                    extraido_com_sucesso = True
                    break

                except Exception as e:

                    self.logger.exception(f"Falha na extração do índice {indice} (tentativa {tentativas}/{DOWNLOAD_MAX_ATTEMPTS}): {e}")

                    if tentativas < DOWNLOAD_MAX_ATTEMPTS:
                        sleep(selenium_utils.random_delay)

                finally:

                    # Garante encerramento do navegador em sucesso e falha.
                    if self.driver is not None:
                        selenium_utils.quit(self.driver)
                        self.driver = None

            if extraido_com_sucesso:
                
                # Incrementa o contador para passar para o próximo índice após sucesso.
                contador += 1
                continue
            
            else:
                
                self._gravar_checkpoint_extract(
                    indice=indice,
                    filename=filename,
                    extension=extension,
                    status=STATUS_DRIVER_ERROR,
                    failure_point=FAILURE_DRIVER_CREATION,
                    attempts=tentativas,
                    ctx=ctx,
                )

                self.logger.error(f"Falha definitiva para índice {indice} após {tentativas} tentativa(s). Seguindo para o próximo índice.")
                
                # Incrementa o contador para passar para o próximo índice, mesmo após falha.
                contador += 1
            
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