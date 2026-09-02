

from dataclasses import dataclass


@dataclass(frozen=True)
class AssetTradingCodeDTO:
    trading_code: str
    cvm_code: str | None
    company_name: list[str]
    
