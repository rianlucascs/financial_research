

from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface
from pipelines.shared.checkpoint_values import Stage, Step, Status
from pipelines.shared.utils.io_utils import clear_directory

import json
import pandas as pd
import gc


class ToInterimWorkerA(ToInterimWorkersInterface):


    process: str = "to_interim_worker_a"


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
            # df_empresas
            "codeCVM": "string",
            "issuingCompany": "string",
            "companyName": "string",
            "tradingName": "string",
            "cnpj": "string",
            "industryClassification": "string",
            "industryClassificationEng": "string",
            "activity": "string",
            "website": "string",
            "hasQuotation": "string",
            "status": "string",
            "marketIndicator": "string",
            "market": "string",
            "institutionCommon": "string",
            "institutionPreferred": "string",
            "code": "string",
            "hasEmissions": "boolean",
            "hasBDR": "boolean",
            "typeBDR": "string",
            "describleCategoryBVMF": "string",
            # df_codigos
            "isin": "string",
        }


    def _columns_to_parse_dates(self) -> list[str]:
        return [
            "dateQuotation",
            "lastDate",
        ]
        
        
    def _columns_to_cast_to_numeric(self) -> list[str]:
        return []
    
    
    def _worker(self, ctx):
        
        raw_json_path = ctx.build_raw_path(
            ctx.current_snapshot_path(self.pipeline), 
            subdir_format="json"
        )

        interim_parquet_path = ctx.prepare_transformed_path(
            ctx.current_snapshot_path(self.pipeline), 
            subdir_stage="to_interim", 
            subdir_format="parquet"
        )

        clear_directory(interim_parquet_path, logger=self.logger, remove_root=False)

        records = [json.loads(p.read_text(encoding="utf-8")) for p in raw_json_path.glob("*.json")]

        # Tabela principal: um registro por empresa, sem a lista aninhada
        df_empresas = pd.json_normalize(
            records,
            max_level=0,
        ).drop(columns=["otherCodes"])

        # Tabela de detalhe: um registro por (codeCVM, code, isin) — não perde nenhum otherCode
        df_codigos = pd.json_normalize(
            records,
            record_path="otherCodes",
            meta=["codeCVM"],
        )

        # Datas da B3 vêm em DD/MM/YYYY; parse com dayfirst antes do _parse_dates genérico (que não define dayfirst).
        for col in self._columns_to_parse_dates():
            
            if col in df_empresas.columns:
                
                df_empresas[col] = pd.to_datetime(df_empresas[col], format="%d/%m/%Y %H:%M:%S", errors="coerce").fillna(
                    pd.to_datetime(df_empresas[col], format="%d/%m/%Y", errors="coerce")
                )

        df_empresas, cast_failed_empresas = self._cast_columns(df_empresas)
        df_empresas, invalid_dates_empresas = self._parse_dates(df_empresas)
        df_empresas, cast_failed_numeric_empresas = self._cast_columns_numeric(df_empresas)

        df_codigos, cast_failed_codigos = self._cast_columns(df_codigos)

        df_empresas.to_parquet(interim_parquet_path / "empresas.parquet", index=False, engine="pyarrow")
        df_codigos.to_parquet(interim_parquet_path / "codigos.parquet", index=False, engine="pyarrow")

        del df_empresas, df_codigos
        gc.collect()

        self._write_checkpoint(
            ctx=ctx,
            stage=Stage.TO_INTERIM,
            step=Step.PARSE,
            filename="to_interim_worker_a.success.json",
            status=Status.SUCCESSFUL,
            source=getattr(self.settings, "url", self.pipeline),
            extra={
                "parse_invalid_dates": invalid_dates_empresas,
                "cast_failed_columns_empresas": cast_failed_empresas,
                "cast_failed_columns_codigos": cast_failed_codigos,
                "cast_failed_numeric_empresas": cast_failed_numeric_empresas,
            },
        )