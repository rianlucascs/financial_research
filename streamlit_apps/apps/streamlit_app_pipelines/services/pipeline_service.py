

from pipelines.shared.context import PipelineContext


class PipelineService:
    
    
    def __init__(
        self
    ) -> None:
        
        self.PipelineContext = PipelineContext()


    def run_pipeline(self):
        self.PipelineContext.run()