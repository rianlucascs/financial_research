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