

from streamlit_apps.apps.streamlit_app_pipelines.shared.dto.system_dto import MemoryInfo, DiskInfo


import streamlit as st


def _status_color(percent_used: float) -> str:
    if percent_used >= 90:
        return "#FF8080"  # mesma cor do .excel-error
    if percent_used >= 70:
        return "#F0C36D"
    return "#7FD98A"


def render_system_widget(memory_info: MemoryInfo, disk_info: DiskInfo) -> None:
    st.markdown(
        """
        <style>
        .system-card {
            background-color: #1E1E1E;
            border: 1px solid #3A3A3A;
            border-radius: 0px;
            padding: 12px 16px;
            font-family: Calibri, Arial, sans-serif;
        }
        .system-card-title {
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .system-card-value {
            color: #E1E1E1;
            font-size: 13px;
            margin-bottom: 6px;
        }
        .system-bar-track {
            width: 100%;
            height: 8px;
            background-color: #2D2D2D;
            border-radius: 4px;
            overflow: hidden;
        }
        .system-bar-fill {
            height: 100%;
            border-radius: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_memory, col_disk = st.columns(2)

    with col_memory:
        color = _status_color(memory_info.percent_used)
        st.markdown(
            f"""
            <div class="system-card">
                <div class="system-card-title">Memória</div>
                <div class="system-card-value">
                    {memory_info.used_gb:.1f} GB / {memory_info.total_gb:.1f} GB
                    ({memory_info.percent_used:.0f}%)
                </div>
                <div class="system-bar-track">
                    <div class="system-bar-fill" style="width: {memory_info.percent_used:.0f}%; background-color: {color};"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_disk:
        color = _status_color(disk_info.percent_used)
        st.markdown(
            f"""
            <div class="system-card">
                <div class="system-card-title">Disco</div>
                <div class="system-card-value">
                    {disk_info.used_gb:.1f} GB / {disk_info.total_gb:.1f} GB
                    ({disk_info.percent_used:.0f}%)
                </div>
                <div class="system-bar-track">
                    <div class="system-bar-fill" style="width: {disk_info.percent_used:.0f}%; background-color: {color};"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )