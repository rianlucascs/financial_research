"""
Worker:
    extractor_worker_a

Responsabilidades:
    Baixar o arquivo CSV público da CVM sem abrir navegador.

Notas:
    O alvo desta fonte é um CSV estático em HTTP, então não há necessidade de
    usar Selenium para navegar em páginas ou interagir com elementos do DOM.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_workers import ExtractorWorkersInterface
from pipelines.shared.utils.http_utils import url_is_accessible, download_file
from pipelines.shared.checkpoint_values import Stage, Step, Status, Severity
  
from os import listdir


class ExtractorWorkerA(ExtractorWorkersInterface):


    process: str = "extractor_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)
    
    
    def _worker(self, ctx: PipelineContext) -> None:
        
        url = getattr(self.settings, "url", "")
        filename = getattr(self.settings, "filename", "")
        
        if not url_is_accessible(url):
            
            self.logger.error(f"URL não encontrada (404 ou indisponível): {url}")
            
            return None

        raw_path_csv = ctx.prepare_raw_path(
            ctx.current_snapshot_path(pipeline=self.pipeline), 
            subdir_format="csv"
        )
        
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            
            downloaded_file_path = download_file(url=url, target_path=raw_path_csv, logger=self.logger)
                
            if downloaded_file_path:
                
                if not filename in listdir(raw_path_csv):
                    
                    self.logger.warning(f"Arquivo '{filename}' não encontrado no diretório {raw_path_csv} após o download.")
                    
                else:
                    
                    self._write_checkpoint(
                        ctx=ctx,
                        stage=Stage.EXTRACT,
                        step=Step.DOWNLOAD,
                        status=Status.SUCCESSFUL,
                        filename=f"extractor_worker_a.success.download.json",
                        severity=Severity.INFO,
                        source=getattr(self.settings, "url", self.pipeline),
                        extra={"downloaded_file_path": str(downloaded_file_path)},
                    )
                    
                    break
                
            attempt += 1
            
            if attempt < max_attempts:
                
                self.logger.warning(f"Tentativa {attempt + 1} de {max_attempts} falhou. Retentando...")
                
                continue
            
            if attempt >= max_attempts:
                
                self.logger.error(f"Falha ao baixar o arquivo CSV após {max_attempts} tentativas.")
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.EXTRACT,
                    step=Step.DOWNLOAD,
                    status=Status.FAILED,
                    filename=f"extractor_worker_a.failed.download.json",
                    severity=Severity.CRITICAL,
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={"download_result": None, "error": f"Falha ao baixar o arquivo CSV após {max_attempts} tentativas."},
                )

