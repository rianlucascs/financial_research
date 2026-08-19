

from streamlit_apps.apps.streamlit_app_pipelines.repositories.pipeline_repository import PipelineRepository
from streamlit_apps.apps.streamlit_app_pipelines.repositories.log_repository import LogRepository

import streamlit as st


st.title("Logs")

pipeline_repository = PipelineRepository()
pipelines = pipeline_repository.list_pipelines()

st.selectbox(
    "Selecione o pipeline para visualizar os logs",
    pipelines,
    key="selected_pipeline",
    on_change=lambda: st.session_state.update({"selected_pipeline": st.session_state.selected_pipeline})
)

log_repository = LogRepository(pipeline=st.session_state.selected_pipeline)

st.write(f"Log mais recente do pipeline: ``{log_repository._get_latest_log_folder().name}``")

st.selectbox(
    "Selecione o ``stage`` do pipeline para visualizar os logs",
    log_repository.log_file_name,
    key="selected_log_file",
    on_change=lambda: st.session_state.update({"selected_log_file": st.session_state.selected_log_file})
)

try:
    
    st.text_area(
        "Conteúdo do log",
        value=log_repository._read_log_file(log_file_name=st.session_state.selected_log_file),
        height=400,
        key="log_content",
        on_change=lambda: st.session_state.update({"log_content": log_repository._read_log_file(log_file_name=st.session_state.selected_log_file)})
    )
    
except FileNotFoundError:
    
    st.error(f"Arquivo de log ``{st.session_state.selected_log_file}`` não encontrado.")
    