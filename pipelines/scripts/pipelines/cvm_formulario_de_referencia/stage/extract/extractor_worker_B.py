

from pipelines.shared.interfaces.pipelines.stage.extract.cvm.extractor_worker_B import ExtractorWorkerInterfaceB


class ExtractorWorkerB(ExtractorWorkerInterfaceB):
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )
        
