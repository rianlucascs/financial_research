

from streamlit_apps.apps.streamlit_app_pipelines.services.monitoring_service_logs import MonitoringServiceLogs

import streamlit as st


def render_logs_widget(monitoring_logs: MonitoringServiceLogs) -> None:
    
    for i, (pipeline, logs) in enumerate(monitoring_logs.items()):
        
        for log in logs:
            
            if not i:
                st.write("---")
            else:
                st.write("")
                st.write("")
            
            st.markdown(
                f"""
                {pipeline} - **{log[1]}**

                <span style="
                    background-color: rgba(59, 130, 246, 0.12);
                    border: 1px solid rgba(59, 130, 246, 0.30);
                    color: #3B82F6;
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
        
