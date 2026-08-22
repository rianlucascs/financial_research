

from pipelines.shared.interfaces.readers.cvm.reader_sqlite_cvm import ReaderSnapshotSQLiteInterface


class ReaderSnapshotSQLiteDFP(ReaderSnapshotSQLiteInterface):
    
    
    def __init__(
        self,
    ) -> None:

        super().__init__(
            pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas",
            prefix="dfp",
        )
        
