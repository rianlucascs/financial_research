

from streamlit_apps.apps.streamlit_app_pipelines.repositories.pipeline_repository import PipelineRepository

from datetime import datetime
from pathlib import Path


class AvailablePipelinesService:
    """Servico de listagem de pipelines disponíveis."""
    
    
    def run(self) -> list[str]:
        
        return PipelineRepository().list_pipelines()


class PipelineProcessMappingService:
    """Servico de mapeamento de processos das pipelines."""
    

    def run(self) -> dict[str, dict[str, dict[str, str]]]:
        
        return {
            pipeline: {
                process: {
                    "date": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
                    "time": datetime.fromtimestamp(path.stat().st_mtime).strftime("%H:%M:%S"),
                }
                for process, path in processes.items()
            }
            for pipeline, processes in PipelineRepository().map_pipeline_processes().items()
        }
