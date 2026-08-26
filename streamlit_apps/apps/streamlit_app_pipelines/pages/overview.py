

from streamlit_apps.apps.streamlit_app_pipelines.services.monitoring_service_logs import MonitoringServiceLogs
from streamlit_apps.apps.streamlit_app_pipelines.services.monitoring_service_memory import (
    MonitoringServiceMemory, 
    MonitoringServiceDisk
)
from streamlit_apps.apps.streamlit_app_pipelines.services.pipeline_service import AvailablePipelinesService
from streamlit_apps.apps.streamlit_app_pipelines.services.pipeline_service import PipelineProcessMappingService

from streamlit_apps.apps.streamlit_app_pipelines.components.memory_widget import render_memory_widget
from streamlit_apps.apps.streamlit_app_pipelines.components.disk_widget import render_disk_widget
from streamlit_apps.apps.streamlit_app_pipelines.components.snapshot_pipeline_status_widget import render_snapshot_pipeline_status_widget
from streamlit_apps.apps.streamlit_app_pipelines.components.logs_widget import render_logs_widget

import streamlit as st
from datetime import date

st.title("Visão geral do sistema")
st.subheader("Recursos do servidor")

monitoring_service_memory = MonitoringServiceMemory()
mem = monitoring_service_memory.run()
render_memory_widget(mem)

monitoring_service_disk = MonitoringServiceDisk()
disk = monitoring_service_disk.run()
render_disk_widget(disk)

st.write("---")
st.title("Pipelines")
st.caption("Visão operacional dos pipelines de dados financeiros.")
st.subheader(f"Pipelines que geraram snapshots em {date.today()}")

available_pipelines_service = AvailablePipelinesService()
pipelines = available_pipelines_service.run()
pipeline_process_mapping = PipelineProcessMappingService().run()
render_snapshot_pipeline_status_widget(pipelines=pipelines, pipeline_process_mapping=pipeline_process_mapping)

st.write("---")
st.subheader("Logs dos pipelines")

log_level = st.selectbox(
    label="Nível de log",
    options=["ERROR", "WARNING", "INFO"],
    index=0,
    key="log_level",
)

monitoring_service_logs = MonitoringServiceLogs()
monitoring_logs = monitoring_service_logs.run(log_level=st.session_state.log_level)
render_logs_widget(monitoring_logs)
