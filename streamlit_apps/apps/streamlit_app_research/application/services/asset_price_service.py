

from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.asset_price_repository import AssetPriceRepository

from pandas import DataFrame


class AssetPriceService:
    
    
    def __init__(
        self
    ) -> None:
        
        self.asset_price_repository = AssetPriceRepository()


    def get_asset_price(self, **kwargs) -> DataFrame:
        
        return self.asset_price_repository.get_asset_price(**kwargs)