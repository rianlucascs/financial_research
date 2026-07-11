

from pipelines.readers.cvm_balanco_patrimonial import ReaderCSVCVMBalancoPatrimonial

from functools import lru_cache


@lru_cache(maxsize=8)
def load_cvm_balanco_patrimonial(ticker: str, tipo_arquivo: str, cd_conta: str):
    
    reader_cvm = ReaderCSVCVMBalancoPatrimonial()
    df_cvm = reader_cvm.read(ticker=ticker, tipo_arquivo=tipo_arquivo, cd_conta=cd_conta)

    return df_cvm
