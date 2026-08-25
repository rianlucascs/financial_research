

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
            
            'CNPJ_CIA': "string",
            'DENOM_SOCIAL': "string",
            'DENOM_COMERC': "string",
            'MOTIVO_CANCEL': "string",
            'SIT': "string",
            'CD_CVM': "string",
            'SETOR_ATIV': "string",
            'TP_MERC': "string",
            'CATEG_REG': "string",
            'SIT_EMISSOR': "string",
            'CONTROLE_ACIONARIO': "string",
            'TP_ENDER': "string",
            'LOGRADOURO': "string",
            'COMPL': "string",
            'BAIRRO': "string",
            'MUN': "string",
            'UF': "string",
            'PAIS': "string",
            'CEP': "string",
            'DDD_TEL': "string",
            'TEL': "string",
            'DDD_FAX': "string",
            'FAX': "string",
            'EMAIL': "string",
            'TP_RESP': "string",
            'RESP': "string",
            'LOGRADOURO_RESP': "string",
            'COMPL_RESP': "string",
            'BAIRRO_RESP': "string",
            'MUN_RESP': "string",
            'UF_RESP': "string",
            'PAIS_RESP': "string",
            'CEP_RESP': "string",
            'DDD_TEL_RESP': "string",
            'TEL_RESP': "string",
            'DDD_FAX_RESP': "string",
            'FAX_RESP': "string",
            'EMAIL_RESP': "string",
            'CNPJ_AUDITOR': "string",
            'AUDITOR': "string",
        }


    def _columns_to_parse_dates(self) -> list[str]:
        
        return [
            "DT_REG",
            "DT_CONST",
            "DT_CANCEL",
            "DT_INI_SIT",
            "DT_INI_CATEG",
            "DT_INI_SIT_EMISSOR",
            "DT_INI_RESP",
        ]
