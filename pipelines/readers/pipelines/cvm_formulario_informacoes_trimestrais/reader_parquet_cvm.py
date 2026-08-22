

from pipelines.shared.interfaces.readers.cvm.reader_parquet_cvm import ReaderSnapshotParquetInterface


class ReaderSnapshotParquetITR(ReaderSnapshotParquetInterface):
    
    
    def __init__(
        self,
    ) -> None:

        super().__init__(
            pipeline="cvm_formulario_informacoes_trimestrais",
            prefix="itr",
        )