

from pipelines.shared.context import PipelineContext

from pathlib import Path
from datetime import datetime


class PipelineRepository:
    
    
    def __init__(
        self,
    ) -> None:
        
        self.ctx = PipelineContext()


    def _glob_scripts_dirs(self) -> list[Path]:
        
        return (self.ctx.pipelines_dir / "scripts" / "pipelines").glob("*")

    
    def _glob_snapshot_dirs(self, pipeline: str) -> list[Path]:
        
        return (self.ctx.data_dir / self.ctx.current_snapshot_path(pipeline)).glob("*")    
    
    
    def list_pipeline_names(self) -> list[str]:
        """
        Lista todos os pipelines disponíveis no diretório de scripts.
        """
        
        return [
            path.name
            for path in self._glob_scripts_dirs()
            if path.is_dir()
        ]
    
    
    def find_first_file_by_extension(self, pipeline: str, process: str, extension: str) -> Path | None:
        """
        Retorna o primeiro arquivo encontrado em um diretório de processo específico do snapshot atual do pipeline, com a extensão fornecida.
        """
        
        process_path = self.ctx.data_dir / self.ctx.current_snapshot_path(pipeline) / process 
        
        return next(process_path.glob(f"**/*.{extension}"), None)
    
    
    def find_first_file_creation_time(self, pipeline: str, process: str, extension: str) -> datetime | None:
        
        if process in ["to_interim", "to_processed"]:
            process = f"transform/{process}"
            
        first_file = self.find_first_file_by_extension(pipeline, process, extension)
        
        if first_file is None:
            
            return None
        
        return datetime.fromtimestamp(first_file.stat().st_ctime)
