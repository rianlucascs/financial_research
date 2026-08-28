

from streamlit_apps.apps.streamlit_app_pipelines.application.services.pipeline_service import PipelineService
from streamlit_apps.apps.streamlit_app_pipelines.application.services.system_service import SystemService

from streamlit_apps.apps.streamlit_app_pipelines.presentation.components.snapshot_widget import render_snapshot_widget
from streamlit_apps.apps.streamlit_app_pipelines.presentation.components.system_widget import render_system_widget

import streamlit as st


pipeline_service = PipelineService()
system_service = SystemService()


st.markdown(
    """
    <h1 style="
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
        font-size: 30px;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin: 0 0 20px 0;
    ">Overview</h1>
    """,
    unsafe_allow_html=True,
)

st.caption("Monitoramento do Sistema")

render_system_widget(
    memory_info=system_service.get_memory_info(),
    disk_info=system_service.get_disk_info()
)


st.markdown(
    """
    <p style="color: #FFFFFF; font-size: 15px; margin-top: 30px;">
        Monitoramento dos Pipelines ETL
    </p>
    """,
    unsafe_allow_html=True,
)

render_snapshot_widget(
    pipeline_service.get_snapshot_overview()
)