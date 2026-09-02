


from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.asset_repository import AssetRepository
from streamlit_apps.apps.streamlit_app_research.shared.dto.asset_dto import AssetTradingCodeDTO


class AssetService:


    def __init__(
        self
    ) -> None:
        
        self.asset_repository = AssetRepository()


    def list_trading_codes(self) -> list[AssetTradingCodeDTO]:
        
        assets: list[AssetTradingCodeDTO] = self.asset_repository.list_trading_codes()

        return [
            AssetTradingCodeDTO(
                trading_code=f"{asset.trading_code}.SA",
                cvm_code=asset.cvm_code,
                company_name=asset.company_name
            )
            for asset in assets
        ]