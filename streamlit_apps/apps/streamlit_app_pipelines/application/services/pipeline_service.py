

from streamlit_apps.apps.streamlit_app_pipelines.infrastructure.repositories.pipeline_repository import PipelineRepository

from datetime import datetime


class PipelineService:
    
    
    def __init__(
        self
        ) -> None:
        
        self.pipeline_repository = PipelineRepository()
        
    
    def list_pipeline_names(self) -> list[str]:
        
        return self.pipeline_repository.list_pipeline_names()
    
    
    def find_first_file_creation_time(self, pipeline: str, process: str, extension: str) -> str | None:
        """
        Retorna o timestamp de criação do primeiro arquivo encontrado em um diretório de processo específico do snapshot atual do pipeline, com a extensão fornecida.
        """
        
        creation_time = self.pipeline_repository.find_first_file_creation_time(pipeline, process, extension)
        
        if creation_time is None:
        
            return None
        
        return creation_time.strftime("%H:%M")


    def get_snapshot_overview(self) -> list[dict]:
        
        return [
            {
                "pipeline": pipeline_name,
                "processes": [
                    {
                        "name": "raw",
                        "executed_at": self.find_first_file_creation_time(
                            pipeline_name, "raw", "csv"
                        ),
                        "has_error": False,
                    },
                    {
                        "name": "to_interim",
                        "executed_at": self.find_first_file_creation_time(
                            pipeline_name, "to_interim", "parquet"
                        ),
                        "has_error": False,
                    },
                    {
                        "name": "to_processed",
                        "executed_at": self.find_first_file_creation_time(
                            pipeline_name, "to_processed", "parquet"
                        ),
                        "has_error": False,
                    },
                ],
            }
            for pipeline_name in self.list_pipeline_names()
        ]