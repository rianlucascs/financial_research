"""
Worker:
    loader_workers.py

Responsabilidades:
    Ler os dados de uma fonte (pipeline) e carregá-los no estágio de integração.

Notas:  
    ...
"""


from pipelines.shared.interfaces.integration.stage.loader_workers import LoaderWorkersInterface


class LoaderWorkers(LoaderWorkersInterface):


    process: str = "loader_workers"
    

    def __init__(
        self,
        *,
        integration: str,
        source_pipeline: str,
        data_dir: str | None = None,
        filename: str
    ) -> None:
        
        self.integration = integration
        self.source_pipeline = source_pipeline
        self.source_stage = data_dir if data_dir is not None else "to_processed"
        self.filename = filename
        self.logger = None
