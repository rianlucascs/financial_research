

import streamlit as st
import base64
from pathlib import Path


def render_background_widget(
    container_key: str,
    image_path: Path,
    height: str = "300px",
    overlay_opacity: float = 0.45,
) -> None:
    encoded = base64.b64encode(image_path.read_bytes()).decode()

    st.markdown(
        f"""
        <style>
        .st-key-{container_key} {{
            position: relative;
            background-image:
                linear-gradient(
                    180deg,
                    rgba(0,0,0,{overlay_opacity}) 0%,
                    rgba(0,0,0,{overlay_opacity * 0.6}) 100%
                ),
                url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            border-radius: 10px;
            min-height: {height};
            padding: 28px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
            transition: box-shadow 0.3s ease;
        }}
        .st-key-{container_key}:hover {{
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )