

from streamlit_apps.apps.streamlit_app_pipelines.infrastructure.repositories import system_repository 
from streamlit_apps.apps.streamlit_app_pipelines.shared.dto.system_dto import MemoryInfo, DiskInfo


class SystemService:
    
    
    def __init__(self):
        
        self.system_repository = system_repository


    def get_memory_info(self) -> MemoryInfo:
        return self.system_repository.get_memory_info()


    def get_disk_info(self) -> DiskInfo:
        return self.system_repository.get_disk_info()