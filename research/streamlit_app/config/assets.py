

from dataclasses import dataclass
from functools import lru_cache

from pandas import isna

from data.b3_indices_segmentos_setoriais import load_b3_indices_segmentos_setoriais


@dataclass(frozen=True)
class AssetOption:
    label: str
    acao: str
    ticker: str


DEFAULT_ASSETS = [
    AssetOption("TAEE11 - Taesa", "TAEE11", "TAEE11.SA"),
    AssetOption("KLBN11 - Klabin", "KLBN11", "KLBN11.SA"),
    AssetOption("PETR4 - Petrobras", "PETR4", "PETR4.SA"),
    AssetOption("VALE3 - Vale", "VALE3", "VALE3.SA"),
]


@lru_cache(maxsize=8)
def get_assets(indice: str = "IBEP") -> tuple[AssetOption, ...]:
     
    df_b3 = load_b3_indices_segmentos_setoriais(indice=indice)

    if "Data Referencia" in df_b3.columns:
        
        latest_date = df_b3["Data Referencia"].max()
        df_b3 = df_b3[df_b3["Data Referencia"] == latest_date].copy()

    df_b3 = df_b3.drop_duplicates(subset=["Código"]).copy()

    assets: list[AssetOption] = []
    
    for _, row in df_b3.iterrows():
        
        codigo = str(row.get("Código", "")).strip()
        
        if not codigo:
            continue

        acao = row.get("Ação", codigo)
        acao = codigo if isna(acao) else str(acao).strip()

        assets.append(AssetOption(label=f"{codigo} - {acao}", acao=acao, ticker=f"{codigo}.SA"))

    assets = [*assets, AssetOption("IBOV - Ibovespa", acao="Ibovespa", ticker="^BVSP")]

    return tuple(assets)
