

from data_providers.providers.yfinance_price_provider import YFinancePriceProvider

from pandas import DataFrame


class AssetPriceRepository:
    
    
    def __init__(self):
        
        self.yfinance_price_provider = YFinancePriceProvider()
        
        
    def get_asset_price(self, **kwargs) -> DataFrame:
        
        return self.yfinance_price_provider.get_asset_price(**kwargs)