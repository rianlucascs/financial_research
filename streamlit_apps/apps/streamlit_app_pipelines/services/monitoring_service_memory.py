

from streamlit_apps.apps.streamlit_app_pipelines.repositories.io_repository import (
    get_memory_info, MemoryInfo,
    get_disk_info, DiskInfo
)


class MonitoringServiceMemory:
    """Servico de monitoramento de memória do sistema."""


    def run(self) -> MemoryInfo:
        
        return get_memory_info()
    

class MonitoringServiceDisk:
    """Servico de monitoramento de disco do sistema."""


    def run(self) -> DiskInfo:
        
        return get_disk_info()