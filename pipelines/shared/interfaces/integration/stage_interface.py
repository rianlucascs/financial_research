"""
Define os tipos de dado que trafegam entre estágios de integração entre
pipelines independentes e o contrato genérico que toda Stage deve respeitar.

Fluxo típico de integração:
    LoadSourcesData -> AlignedData -> JoinedData -> ValidatedData -> PersistedData
"""


from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar
from pandas import DataFrame


@dataclass(frozen=True)
class SourceDataset:
    """Um dataset carregado de uma fonte/pipeline de origem."""

    source: str
    dataset: str
    snapshot: str
    df: DataFrame


@dataclass(frozen=True)
class LoadSourcesData:
    """
    Datasets brutos carregados de múltiplas fontes de origem.

    Exemplo de fontes: CVM, BCB, B3, outputs de outros pipelines internos.
    """

    datasets: list[SourceDataset]


@dataclass(frozen=True)
class AlignedData:
    """
    Datasets após reconciliação semântica entre fontes.

    Contém dados com chaves, granularidade, moeda e unidades alinhadas.
    """

    datasets: list[SourceDataset]
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class JoinedData:
    """Resultado da combinação (join/merge) entre os datasets alinhados."""

    df: DataFrame
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ValidationIssue:
    """Issue detectado na validação pós-join."""

    code: str
    message: str
    severity: str
    details: dict[str, Any] | None = None


@dataclass(frozen=True)
class ValidatedData:
    """Resultado validado, com report de qualidade e consistência."""

    df: DataFrame
    issues: list[ValidationIssue]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class PersistedData:
    """Artefato final persistido (arquivo, tabela, view etc.)."""

    uri: str
    rows: int
    metadata: dict[str, Any]


TIn = TypeVar("TIn")
TOut = TypeVar("TOut")


class StageTypes(Generic[TIn, TOut]):
    """Apenas marca TIn/TOut para leitura humana e type checker.
    
    TIn  = tipo de dado que esta Stage espera receber.
    TOut = tipo de dado que esta Stage produz.

    A primeira Stage da lista (extract) tem TIn = None, pois não
    recebe dado de nenhuma etapa anterior.
    """