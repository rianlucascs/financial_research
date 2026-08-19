

from pipelines.readers.logs.reader_logs import ReaderLogs


class LogRepository(ReaderLogs):
    
    
    def __init__(
        self, 
        pipeline
    ) -> None:    
        
        super().__init__(
            pipeline=pipeline
        )