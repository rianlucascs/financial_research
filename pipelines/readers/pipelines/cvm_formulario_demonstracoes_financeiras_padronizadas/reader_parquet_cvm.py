

from pipelines.shared.interfaces.readers.cvm.reader_parquet_cvm import ReaderParquetCVMInterface


class ReaderParquetCVM(ReaderParquetCVMInterface):
    
    
    def __init__(
        self,
    ) -> None:

        super().__init__(
            pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas",
            prefix="dfp",
        )