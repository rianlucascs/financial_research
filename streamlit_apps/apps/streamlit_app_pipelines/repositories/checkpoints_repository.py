


from pipelines.readers.checkpoints.reader_checkpoints import ReaderCheckpoints


class CheckpointsRepository(ReaderCheckpoints):


    def __init__(
        self,
        pipeline
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
            )