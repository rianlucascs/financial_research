

from pipelines.shared.context import PipelineContext


class ReaderHistoricalData:
    
    
    def __init__(
        self,
        pipeline: str
    ) -> None:
        
        self.pipeline = pipeline
        self.ctx = PipelineContext()
        
    
    