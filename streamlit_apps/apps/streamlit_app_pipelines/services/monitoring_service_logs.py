


from streamlit_apps.apps.streamlit_app_pipelines.repositories.log_repository import LogRepository
from streamlit_apps.apps.streamlit_app_pipelines.repositories.pipeline_repository import PipelineRepository

from typing import Literal


class MonitoringServiceLogs:
    """
    Classe responsável por monitorar os logs dos pipelines de dados financeiros. 
    Ela utiliza o repositório de logs para ler os arquivos de log e filtrar os logs com base no nível de log especificado.
    O resultado é um dicionário contendo os logs filtrados para cada pipeline.
    """
    
    
    log_levels: list[str] = ["ERROR", "WARNING", "INFO"]
    
    
    def _worker(self, pipeline: str, log_level: Literal["ERROR", "WARNING", "INFO"] = "ERROR") -> list[list[str, str, str]]:
        """
        Args:
            ``pipeline`` (str): Nome do pipeline.
            ``log_level`` (Literal["ERROR", "WARNING", "INFO"]): Nível de log a ser filtrado. Default é "ERROR".
        Returns:
            list[list[str, str, str]]: Lista de logs filtrados. Cada log é representado como uma lista contendo o nome do 
            arquivo de log, o nível de log e a mensagem.
        """
        
        log_repository = LogRepository(pipeline=pipeline)
        
        list_error_logs = []
        
        for log_file_name in log_repository.log_file_name:
            
            try:
            
                file = log_repository._read_log_file(log_file_name)
            
            except FileNotFoundError:
            
                continue
                    
            for row in file.split("\n"):
                
                if log_level in row:
                    list_error_logs.append([log_file_name, log_level, row])
                    
        return list_error_logs
    
    
    def run(self, log_level: Literal["ERROR", "WARNING", "INFO"] = "ERROR") -> dict[str, list[list[str, str, str]]]:
        """
        Retorna os logs monitorados para todos os pipelines.

        Returns:
            dict[str, list[list[str, str, str]]]: Dicionário contendo os logs filtrados para cada pipeline.
        """
        
        monitoring_logs = {}
        
        for pipeline in PipelineRepository().list_pipelines():
            
            monitoring_logs[pipeline] = self._worker(pipeline=pipeline, log_level=log_level)

        return monitoring_logs