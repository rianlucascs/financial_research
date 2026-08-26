

import streamlit as st
from textwrap import dedent


def render_snapshot_pipeline_status_widget(pipelines: list[str], pipeline_process_mapping: dict[str, dict[str, str]]) -> None:
    
    cols = st.columns(3)

    for index, pipeline in enumerate(pipelines):
        
        raw = pipeline_process_mapping.get(pipeline, {}).get("raw")
        to_interim = pipeline_process_mapping.get(pipeline, {}).get("transform/to_interim")
        to_processed = pipeline_process_mapping.get(pipeline, {}).get("transform/to_processed")

        def format_process_status(process: dict[str, str] | None) -> str:
            
            if process is None:
            
                return "- indisponível"
            
            return f"● {process['date']} {process['time']}"
        
        with cols[index % 3]:
            
            st.markdown(
                dedent(f"""
                <div style="
                    border: 1px solid rgba(59, 130, 246, 0.30);
                    border-left: 3px solid #3B82F6;
                    border-radius: 8px;
                    padding: 14px 16px;
                    margin-bottom: 10px;
                    background-color: rgba(59, 130, 246, 0.05);
                ">
                    <div style="font-weight: 600; font-size: 16px; margin-bottom: 14px; color: #f0c844;">
                        {pipeline}
                    </div>
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 8px;
                        padding-bottom: 6px;
                        border-bottom: 1px solid rgba(148, 163, 184, 0.25);
                        font-size: 11px;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 0.03em;
                        color: rgba(148, 163, 184, 0.9);
                    ">
                        <span>Processo</span>
                        <span>Última atualização</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 13px;">
                        <span>raw</span>
                        <span style="color: #22C55E; font-weight: 600;">{format_process_status(raw)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 13px;">
                        <span>to interim</span>
                        <span style="color: #22C55E; font-weight: 600;">{format_process_status(to_interim)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 13px;">
                        <span>to processed</span>
                        <span style="color: #22C55E; font-weight: 600;">{format_process_status(to_processed)}</span>
                    </div>
                </div>
                """),
                unsafe_allow_html=True,
            )