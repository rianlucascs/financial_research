

from pipelines.shared.interfaces.pipelines.stage.extract.cvm.extractor_worker_A import ExtractorWorkerInterfaceA 


class ExtractorWorkerA(ExtractorWorkerInterfaceA):
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )
