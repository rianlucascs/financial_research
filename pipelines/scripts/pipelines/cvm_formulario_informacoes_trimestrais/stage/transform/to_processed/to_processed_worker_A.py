

from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.cvm.to_processed_worker_A import ToProcessedWorkerInterfaceA

from pandas import DataFrame


class ToProcessedWorkerA(ToProcessedWorkerInterfaceA):
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )

    
    def _add_derived_columns(self, df: DataFrame) -> DataFrame | None:
        """
        Adiciona colunas derivadas ao DataFrame.

        Retorna o DataFrame modificado ou None se nenhuma modificação for necessária.
        """
        
        df["ORIGEM_FORMULARIO"] = "ITR"
        
        
        if ("DT_INI_EXERC" in df.columns) and ("DT_FIM_EXERC" in df.columns):
            df["INTERVALO_EXERC"] = (df["DT_FIM_EXERC"] - df["DT_INI_EXERC"]).dt.days
            
        return df
