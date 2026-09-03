


from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.asset_repository import AssetRepository
from streamlit_apps.apps.streamlit_app_research.shared.dto.asset_dto import AssetTradingCodeDTO


MANUAL_TRADING_CODES: list[AssetTradingCodeDTO] = [
    AssetTradingCodeDTO(
        trading_code="^BVSP",
        cvm_code=None,
        company_name="Ibovespa",
    ),
]


class AssetService:


    def __init__(
        self
    ) -> None:
        
        self.asset_repository = AssetRepository()


    def list_trading_codes(self) -> list[AssetTradingCodeDTO]:
        
        assets: list[AssetTradingCodeDTO] = self.asset_repository.list_trading_codes()

        b3_assets = [
            AssetTradingCodeDTO(
                trading_code=f"{asset.trading_code}.SA",
                cvm_code=asset.cvm_code,
                company_name=asset.company_name,
            )
            for asset in assets
        ]

        return MANUAL_TRADING_CODES + b3_assets