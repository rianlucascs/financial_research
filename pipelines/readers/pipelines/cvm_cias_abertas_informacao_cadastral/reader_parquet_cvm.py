

from pipelines.shared.interfaces.readers.reader_snapshot_parquet import ReaderSnapshotParquetInterface


class ReaderSnapshotParquet(ReaderSnapshotParquetInterface):
    
    
    def __init__(
        self,
    ) -> None:

        super().__init__(
            pipeline="cvm_cias_abertas_informacao_cadastral",
            filename="cad_cia_aberta.parquet"
        )