

from streamlit_apps.apps.streamlit_app_pipelines.repositories.pipeline_repository import PipelineRepository
from streamlit_apps.apps.streamlit_app_pipelines.services.monitoring_service_logs import MonitoringServiceLogs

import streamlit as st


st.title("Pipelines")
st.caption("Visão operacional dos pipelines de dados financeiros.")

st.subheader("Pipelines disponíveis")


cols = st.columns(3)

pipeline_repository = PipelineRepository()
pipelines = pipeline_repository.list_pipelines()


cols = st.columns(3)

for index, pipeline in enumerate(pipelines):
    with cols[index % 3]:
        st.container(
            border=True
        ).markdown(f"**{pipeline}**")

st.subheader("Logs dos pipelines")

st.session_state.log_level_slider = st.session_state.get("log_level_slider", "ERROR")

st.select_slider(
    label="Nível de log",
    options=["ERROR", "WARNING", "INFO"],
    value="ERROR",
    key="log_level_slider"
)


monitoring_service_logs = MonitoringServiceLogs()
monitoring_logs = monitoring_service_logs.run(log_level=st.session_state.log_level_slider)

for pipeline, logs in monitoring_logs.items():
    
    for log in logs:
        
        st.write("---")
        
        st.markdown(
            f"""
            **{log[1]}**

            <span style="
                background-color: #ff4b4b;
                color: white;
                padding: 3px 8px;
                border-radius: 5px;
                font-size: 0.8rem;
                font-weight: bold;
            ">
                {log[0]}
            </span>
            """,
            unsafe_allow_html=True,
        )

        st.text_area(
            label="Mensagem",
            value=log[2],
            height=200,
        )
    
