

from pipelines.readers.b3_indices_segmentos_setoriais import ReaderSQLB3IndicesSegmentosSetoriais

from functools import lru_cache


@lru_cache(maxsize=8)
def load_b3_indices_segmentos_setoriais(indice: str):
    
    reader_b3 = ReaderSQLB3IndicesSegmentosSetoriais()
    df_b3 = reader_b3.read(indice=indice)

    return df_b3
