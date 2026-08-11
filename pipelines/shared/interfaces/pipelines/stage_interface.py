"""
Define os tipos de dado que trafegam entre estágios do pipeline e o
contrato genérico que toda Stage deve respeitar.

Tipos de dado entre estágios (a ordem real depende do Pipeline):
    RawData       -> dado exatamente como veio da fonte, sem transformação.
    InterimData   -> dado estruturalmente correto (tipado, nomeado, sem nulos técnicos),
                     sem regra de negócio.
    ProcessedData -> dado com regra de negócio aplicada, pronto para carga.
    LoadData      -> dado final preparado para escrita no destino.
    SnapshotDrift -> delta entre snapshots (added, removed, changed).  
"""


from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar
from pandas import DataFrame


@dataclass(frozen=True)
class RawData:
    """Dado bruto, exatamente como recebido da fonte (CVM, BCB, B3, ...).

    Não deve ser modificado após criado (frozen). Serve como registro
    para auditoria e reprocessamento sem precisar re-extrair da fonte.
    """
    
    df: DataFrame
    
    
@dataclass(frozen=True)
class InterimData:
    """Dado estruturalmente validado e tipado corretamente.

    Contém: tipos corretos (Decimal, date, etc.), colunas renomeadas
    para o padrão interno, nulos técnicos tratados.

    NÃO contém: agregações, joins, cálculo de indicadores, ou qualquer
    regra que dependa de conhecimento de negócio.
    """
    
    df: DataFrame
    

@dataclass(frozen=True)
class ProcessedData:
    """Dado final, com regras de negócio já aplicadas.

    Contém: agregações, joins entre fontes, indicadores calculados,
    enriquecimento com metadados. Pronto para load no destino final.
    """
    
    df: DataFrame
    
    
@dataclass(frozen=True)
class LoadData:
    """Dado pronto para load no destino final.

    Contém: DataFrame com dados finais, pronto para ser carregado
    no banco de dados ou outro destino.
    """
    
    df: DataFrame


@dataclass(frozen=True)
class SnapshotDrift:
    """Resultado da comparação entre dois DataFrames.

    Contém três DataFrames: added, removed e changed.
    
    Args
        `added` (DataFrame): Linhas que estão no DataFrame novo, mas não no antigo.
        `removed` (DataFrame): Linhas que estão no DataFrame antigo, mas não no novo.
        `changed` (DataFrame): Linhas que estão em ambos os DataFrames, mas com valores diferentes.
    """
    
    added: DataFrame
    removed: DataFrame
    changed: DataFrame
    

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")
        
        
class StageTypes(Generic[TIn, TOut]):
    """Apenas marca TIn/TOut para leitura humana e type checker. Sem contrato de execução.

    TIn  = tipo de dado que esta Stage espera receber.
    TOut = tipo de dado que esta Stage produz.

    A primeira Stage da lista (extract) tem TIn = None, pois não
    recebe dado de nenhuma etapa anterior.
    """

