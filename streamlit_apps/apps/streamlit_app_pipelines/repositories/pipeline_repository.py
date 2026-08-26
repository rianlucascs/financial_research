

from pipelines.shared.context import PipelineContext

from pathlib import Path
from datetime import datetime


class PipelineRepository:
    
    
    def __init__(
        self,
        pipeline: str | None = None,
    ) -> None:
        
        self.pipeline = pipeline
        self.ctx = PipelineContext()


    def list_pipelines(self):
        """
        Lista todos os pipelines disponíveis no diretório de scripts.
        """
        
        return [
            path.name
            for path in (self.ctx.pipelines_dir / "scripts" / "pipelines").glob("*")
            if path.is_dir()
        ]
    
    
    def map_pipeline_processes(self) -> dict[str, dict[str, Path]]:
        """
        Retorna o Path do primeiro arquivo encontrado
        em cada etapa do pipeline, para cada extensão de arquivo relevante.
        """

        data_producing_paths = {
            "raw": ["csv", "zip"],
            "transform/to_interim": ["parquet"],
            "transform/to_processed": ["parquet"],
        }

        first_file_paths: dict[str, dict[str, Path]] = {}

        for pipeline in self.list_pipelines():

            pipeline_path = self.ctx.data_dir / self.ctx.current_snapshot_path(pipeline)

            for process, extensions in data_producing_paths.items():

                process_path = pipeline_path / process

                for extension in extensions:

                    first_file = next(process_path.glob(f"**/*.{extension}"), None)
                    
                    if first_file is not None:
                        
                        current = first_file_paths.setdefault(pipeline, {}).get(process)
                        if current is None or first_file.stat().st_mtime > current.stat().st_mtime:
                            first_file_paths[pipeline][process] = first_file

        return first_file_paths


    def pipelines_with_snapshot_today(self):
        
        return [
            (path, path.name)
            for path in (self.ctx.data_dir / self.ctx.current_snapshot_path(self.pipeline)).glob("*")
            if path.is_dir()
        ]

