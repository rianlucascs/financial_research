

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketOverviewAssetOption:
    label: str
    acao: str
    ticker: str


def get_market_overview_assets() -> tuple[MarketOverviewAssetOption, ...]:

    return (
        MarketOverviewAssetOption("IBEP - Brasil Empresas Públicas", acao="Empresas Públicas", ticker="IBEP"),
        MarketOverviewAssetOption("IDIV - Dividendos", acao="Dividendos", ticker="IDIV"),
        MarketOverviewAssetOption("MLCX - MidLarge Cap", acao="MidLarge Cap", ticker="MLCX"),
        MarketOverviewAssetOption("SMLL - Small Cap", acao="Small Cap", ticker="SMLL"),
        MarketOverviewAssetOption("IVBX - IVBX-2", acao="IVBX-2", ticker="IVBX"),
        MarketOverviewAssetOption("AGFS - Agronegócio Free Float Setorial", acao="Agronegócio", ticker="AGFS"),
        MarketOverviewAssetOption("IFNC - Financeiro", acao="Financeiro", ticker="IFNC"),
        MarketOverviewAssetOption("IBEE - Energia Elétrica", acao="Energia Elétrica", ticker="IBEE"),
        MarketOverviewAssetOption("IBHB - B3 High Beta", acao="High Beta", ticker="IBHB"),
        MarketOverviewAssetOption("IFIX - Fundos Imobiliários", acao="Fundos Imobiliários", ticker="IFIX"),
        MarketOverviewAssetOption("IBLV - B3 Low Volatility", acao="Low Volatility", ticker="IBLV"),
        MarketOverviewAssetOption("IMOB - Imobiliário", acao="Imobiliário", ticker="IMOB"),
        MarketOverviewAssetOption("UTIL - Utilidade Pública", acao="Utilidade Pública", ticker="UTIL"),
        MarketOverviewAssetOption("ICON - Consumo", acao="Consumo", ticker="ICON"),
        MarketOverviewAssetOption("IEEX - Energia Elétrica", acao="Energia Elétrica", ticker="IEEX"),
        MarketOverviewAssetOption("IFIL - Fundos de Investimento Listados", acao="Fundos Listados", ticker="IFIL"),
        MarketOverviewAssetOption("IMAT - Materiais Básicos", acao="Materiais Básicos", ticker="IMAT"),
        MarketOverviewAssetOption("INDX - Industrial", acao="Industrial", ticker="INDX"),
        MarketOverviewAssetOption("IBSD - Smart Dividendos", acao="Smart Dividendos", ticker="IBSD"),
        MarketOverviewAssetOption("BDRX - BDRX", acao="BDRs", ticker="BDRX"),
    )