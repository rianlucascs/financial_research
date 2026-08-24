"""
Worker:
    extractor_worker_a

Responsabilidades:
    Baixar os arquivos `ZIP` do site da CVM (Comissão de Valores Mobiliários) contendo
    as `demonstrações financeiras padronizadas` das empresas abertas no Brasil.
    
Notas:
    Caso o pipelines seja executado no mesmo dia em que os arquivos `ZIP` foram baixados, o worker irá sobrescrever os arquivos baixados.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_workers import ExtractorWorkersInterface
from pipelines.shared.checkpoint_values import Stage, Step, Status, FailurePoint, Severity
from pipelines.shared.utils.formatting_utils import format_size
from pipelines.shared.utils.io_utils import remove_file
from pipelines.shared.utils.http_utils import url_is_accessible

from pathlib import Path
import wget
from datetime import date


class ExtractorWorkerA(ExtractorWorkersInterface):
    
    
    process: str = "extractor_worker_a"
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )
        
    
    def _download_zip_file(self, filename: str, raw_path_zip: Path) -> tuple[Path | None, str | None]:
        
        _url = f"{getattr(self.settings, 'url', '')}{filename}"
        
        if not url_is_accessible(_url):
            return None, f"URL não encontrada (404 ou indisponível): {_url}"
        
        remove_file(zip_path=raw_path_zip / filename, logger=self.logger)
    
        try:
            
            return Path(wget.download(_url, out=str(raw_path_zip), bar=None)), None
        
        except Exception as e:
            
            self.logger.warning(f"Falha ao baixar {filename}: {e}")
            
            return None, str(e)
        

    def _worker(self, ctx: PipelineContext) -> None:

        for filename in getattr(self.settings, "build_archives_zip", []):
            
            build_raw_path_zip = ctx.prepare_raw_path(pipeline=Path(self.pipeline) / date.today().strftime("%Y-%m-%d"), subdir_format="zip")
            
            download_result = self._download_zip_file(filename=filename, raw_path_zip=build_raw_path_zip)
            
            if download_result[0] is None:
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.EXTRACT,
                    step=Step.DOWNLOAD,
                    filename=f"extractor_worker_a.failed_{filename}.json",
                    status=Status.FAILED,
                    failure_point=FailurePoint.EXCEPTION,
                    severity=Severity.ERROR,
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={"download_result": None, "error": download_result[1]},
                )
                
                self.logger.error(f"Falha no download do arquivo {filename}: {download_result[1]}")
                
            else:
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.EXTRACT,
                    step=Step.DOWNLOAD,
                    filename=f"extractor_worker_a.success_{filename}.json",
                    status=Status.SUCCESSFUL,
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={"download_result": {
                        "name": download_result[0].name,
                        "parent": str(download_result[0].parent),
                        "suffix": download_result[0].suffix,
                        "size_format": format_size(download_result[0].stat().st_size),
                        "size_bytes": download_result[0].stat().st_size,
                    }},
                )
            