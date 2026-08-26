

import psutil
from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryInfo:
    
    
    total_bytes: int
    used_bytes: int
    available_bytes: int
    percent_used: float


    @property
    def total_gb(self) -> float:
        return self.total_bytes / (1024 ** 3)


    @property
    def used_gb(self) -> float:
        return self.used_bytes / (1024 ** 3)


    @property
    def available_gb(self) -> float:
        return self.available_bytes / (1024 ** 3)


@dataclass(frozen=True)
class DiskInfo:
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent_used: float

    @property
    def total_gb(self) -> float:
        return self.total_bytes / (1024 ** 3)

    @property
    def used_gb(self) -> float:
        return self.used_bytes / (1024 ** 3)

    @property
    def free_gb(self) -> float:
        return self.free_bytes / (1024 ** 3)
    
    
def get_memory_info() -> MemoryInfo:
    """
    Retorna o uso de memória RAM do sistema (Linux).

    ``used`` aqui reflete a memória de fato indisponível para novos processos,
    não a soma bruta de tudo alocado — o Linux usa RAM livre para cache de
    página/buffers, que é liberada sob demanda. Por isso ``available``
    (não ``used``) é a métrica mais confiável pra saber "quanto ainda posso usar".
    """
    
    vm = psutil.virtual_memory()

    return MemoryInfo(
        total_bytes=vm.total,
        used_bytes=vm.used,
        available_bytes=vm.available,
        percent_used=vm.percent,
    )
    

def get_disk_info(path: str = "/") -> DiskInfo:
    """
    Retorna o uso de disco do ponto de montagem em ``path``.

    Por padrão consulta a raiz ("/"). Se seus dados ficam num volume/partição
    separada (por exemplo, um disco dedicado montado em ``/data`` ou
    ``/mnt/financial_research``), passe esse path explicitamente para
    refletir o espaço real disponível para os Parquets/snapshots.
    """
    
    du = psutil.disk_usage(path)
    
    return DiskInfo(
        total_bytes=du.total,
        used_bytes=du.used,
        free_bytes=du.free,
        percent_used=du.percent,
    )