

from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.cvm.to_interim_worker_A import ToInterimWorkerInterfaceA


class ToInterimWorkerA(ToInterimWorkerInterfaceA):


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )


    def _columns_to_cast(self) -> dict[str, str]:
        
        return {
            "CNPJ_CIA": "string",
            "VERSAO": "Int64",
            "DENOM_CIA": "string",
            "CD_CVM": "string",
            "GRUPO_DFP": "string",
            "MOEDA": "string",
            "ESCALA_MOEDA": "string",
            "ORDEM_EXERC": "string",
            "CD_CONTA": "string",
            "DS_CONTA": "string",
            "ST_CONTA_FIXA": "string",
        }


    def _columns_to_parse_dates(self) -> list[str]:
        
        return [
            "DT_REFER",
            "DT_INI_EXERC",
            "DT_FIM_EXERC",
        ]


    def _columns_to_cast_to_numeric(self) -> list[str] | None: 

        return [
            "VL_CONTA",
        ]
        
