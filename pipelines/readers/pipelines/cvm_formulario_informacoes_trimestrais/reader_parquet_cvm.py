

from pipelines.shared.interfaces.readers.cvm.reader_parquet_cvm import ReaderParquetCVMInterface


class ReaderParquetCVMITR(ReaderParquetCVMInterface):
    
    
    def __init__(
        self,
    ) -> None:

        super().__init__(
            pipeline="cvm_formulario_informacoes_trimestrais",
            prefix="itr",
        )