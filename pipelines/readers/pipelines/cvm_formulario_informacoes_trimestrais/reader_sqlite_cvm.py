

from pipelines.shared.interfaces.readers.cvm.reader_sqlite_cvm import ReaderSnapshotSQLiteInterface


class ReaderSnapshotSQLiteITR(ReaderSnapshotSQLiteInterface):
    
    
    def __init__(
        self,
    ) -> None:

        super().__init__(
            pipeline="cvm_formulario_informacoes_trimestrais",
            prefix="itr",
        )
        
