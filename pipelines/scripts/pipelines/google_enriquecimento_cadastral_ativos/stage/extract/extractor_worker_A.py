"""
Worker:
    extractor_worker_a

Responsabilidades:
    ...

Notas:
    ...
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_workers import ExtractorWorkersInterface
from pipelines.shared.utils.selenium_utils.driver_factory import ChromeDriverFactory
from pipelines.shared.utils.selenium_utils.config import ChromeDriverConfig
from pipelines.shared.utils.selenium_utils.browser_session import BrowserSession
from pipelines.shared.utils.selenium_utils.delays import jittered_delay



class ExtractorWorkerA(ExtractorWorkersInterface):
    
    
    process: str = "extractor_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)
    
    
    def _worker(self, ctx: PipelineContext) -> None:
        
        factory = ChromeDriverFactory(self.logger)
        browser_session = BrowserSession(factory, self.logger)

        config = ChromeDriverConfig(
            headless=False,
        )
        
        with browser_session.open(config) as driver:
            
            driver.get("https://www.google.com")
            
            jittered_delay(50, 60)
            
            pass
        
        
ExtractorWorkerA(pipeline="google_enriquecimento_cadastral_ativos").main(PipelineContext())