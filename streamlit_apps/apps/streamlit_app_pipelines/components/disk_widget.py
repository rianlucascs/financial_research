

from streamlit_apps.apps.streamlit_app_pipelines.repositories.io_repository import DiskInfo

import streamlit as st


def _status_color(percent_used: float) -> str:
    
    if percent_used < 70:
        
        return "#22C55E"   # verde
    
    elif percent_used < 90:
        
        return "#F59E0B"   # amarelo
    
    else:
        return "#EF4444"   # vermelho
    

def render_disk_widget(disk: DiskInfo, label: str = "Disco") -> None:
    
    color = _status_color(disk.percent_used)

    st.markdown(
        f"""
        <div style="border: 1px solid rgba(59, 130, 246, 0.30); border-left: 3px solid #3B82F6; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; background-color: rgba(59, 130, 246, 0.05);">
            <div style="font-weight: 600; font-size: 16px; margin-bottom: 12px;">{label}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px;">
                <span>Total</span><span>{disk.total_gb:.2f} GB</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px;">
                <span>Usado</span><span>{disk.used_gb:.2f} GB</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 13px;">
                <span>Livre</span><span style="color: {color}; font-weight: 600;">{disk.free_gb:.2f} GB</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(min(disk.percent_used / 100, 1.0), text=f"{disk.percent_used:.1f}% utilizado")