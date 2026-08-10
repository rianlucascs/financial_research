"""
Worker:
    extractor_worker_b

Responsabilidades:
    Extrair os arquivos `ZIP` baixados do site da CVM (Comissão de Valores Mobiliários) contendo
    as `formulários de informações trimestrais` das empresas abertas no Brasil.
    
Notas:
    Caso o pipelines seja executado no mesmo dia em que os arquivos `ZIP` foram baixados, o worker irá sobrescrever os arquivos extraídos.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_workers import ExtractorWorkersInterface
from pipelines.shared.checkpoint_values import Stage, Step, Status, FailurePoint, Severity
from pipelines.shared.utils.io_utils import clear_directory

from pipelines.scripts.pipelines.cvm_formulario_informacoes_trimestrais.stage.pipeline_settings import build_archives_zip, current_snapshot_path

from pathlib import Path
from zipfile import ZipFile


class ExtractorWorkerB(ExtractorWorkersInterface):
    

    process: str = "extractor_worker_b"
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)
    
    
    def _extract_zip_files(self, filename: str, raw_zip_path: Path, raw_csv_path: Path) -> list[str]:

        _raw_zip_file_path = raw_zip_path / filename
        
        with ZipFile(_raw_zip_file_path, "r") as zip_ref:

            members = zip_ref.infolist() 

            for member in members:
                
                member_path = (raw_csv_path / member.filename).resolve()

                if not member_path.is_relative_to(raw_csv_path.resolve()):
                    
                    self.logger.error(f"Caminho inválido detectado no ZIP: {member.filename}")
                    
                    raise ValueError(f"Caminho inválido detectado no ZIP: {member.filename}")

            zip_ref.extractall(raw_csv_path)


        return [m.filename for m in members]
    

    def _step_dynamic_folder(self, step: Step, zipname: str) -> str:
        """Cada zipname contem um chekpoint diferente, então o nome do arquivo de checkpoint é dinâmico"""
        return str(step) + "/" + zipname
    
    
    def _worker(self, ctx: PipelineContext) -> None:
        
        raw_zip_path = ctx.build_raw_path(current_snapshot_path(self.pipeline), subdir_format="zip")
        raw_csv_path = ctx.build_raw_path(current_snapshot_path(self.pipeline), subdir_format="csv")
        
        clear_directory(path=raw_csv_path, logger=self.logger, remove_root=False)
            
        for filename in build_archives_zip:
            
            if (raw_zip_path / filename).exists():
                
                try:
                    
                    extracted_files = self._extract_zip_files(filename=filename, raw_zip_path=raw_zip_path, raw_csv_path=raw_csv_path)
                    
                    self._write_checkpoint(
                        ctx=ctx,
                        stage=Stage.EXTRACT,
                        step=self._step_dynamic_folder(step=Step.UNZIP, zipname=filename),
                        filename=f"extractor_worker_b.success.json",
                        status=Status.SUCCESSFUL,
                        source="cvm_formulario_informacoes_trimestrais",
                        extra={
                            "zipname": filename,
                            "raw_zip_path": str(raw_zip_path),
                            "raw_csv_path": str(raw_csv_path),
                            "extracted_files": extracted_files,
                        },
                    )
                    
                except Exception as e:
                     
                    self._write_checkpoint(
                        ctx=ctx,
                        stage=Stage.EXTRACT,
                        step=self._step_dynamic_folder(step=Step.UNZIP, zipname=filename),
                        filename=f"extractor_worker_b.failed.json",
                        status=Status.FAILED,
                        failure_point=FailurePoint.UNZIP,
                        reason=str(e),
                        severity=Severity.ERROR,
                        source="cvm_formulario_informacoes_trimestrais",
                        extra={
                            "zipname": filename,
                            "raw_zip_path": str(raw_zip_path),
                            "raw_csv_path": str(raw_csv_path),
                            "extracted_files": extracted_files if 'extracted_files' in locals() else [],
                            "exception": str(e),
                        },
                        
                    ) 
                    
                    self.logger.error(f"Falha ao descompactar o arquivo '{filename}': {e}")       
                    
            else:
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.EXTRACT,
                    step=self._step_dynamic_folder(step=Step.UNZIP, zipname=filename),
                    filename=f"extractor_worker_b.missing.json",
                    status=Status.FAILED,
                    failure_point=FailurePoint.UNZIP,
                    reason="Arquivo ZIP não encontrado",
                    severity=Severity.ERROR,
                    source="cvm_formulario_informacoes_trimestrais",
                    extra={
                        "zipname": filename,
                        "raw_zip_path": str(raw_zip_path),
                        "raw_csv_path": str(raw_csv_path),
                    },
                )
                
                self.logger.error(f"Arquivo ZIP '{filename}' não encontrado no caminho '{raw_zip_path}'")
                

if __name__ == "__main__":
    worker = ExtractorWorkerB(pipeline="cvm_formulario_informacoes_trimestrais")
    worker.main(ctx=PipelineContext())