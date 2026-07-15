from dataclasses import dataclass

@dataclass(frozen=True)
class StrategyOption:
    ticker: str
    acao: str
    name_file_strategy: str
    

def get_strategy_options() -> tuple[StrategyOption, ...]:
    
    return (
        StrategyOption(ticker="TAEE11.SA", acao="TAEE11", name_file_strategy="01_01_neutro_predicao_retorno"),
        StrategyOption(ticker="TAEE11.SA", acao="TAEE11", name_file_strategy="01_02_neutro_predicao_retorno"),
    )
    
def get_strategy_options_by_ticker(ticker: str) -> tuple[StrategyOption, ...]:
    return tuple(
        strategy
        for strategy in get_strategy_options()
        if strategy.ticker == ticker
    )