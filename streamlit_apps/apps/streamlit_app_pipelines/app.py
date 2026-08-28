

import streamlit as st


st.set_page_config(
    page_title="Financial Research - Pipelines",
    page_icon="⚙️",
    layout="wide",
)

pg = st.navigation(
    [
        st.Page("presentation/pages/overview.py", title="Overview"),
    ]
)

pg.run()

with st.sidebar:
    
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 style="font-size: 24px; font-weight: bold;">Financial Research</h1>
            <p style="font-size: 14px;">Monitoramento e acompanhamento da execução dos pipelines ETL.</p>
            <p style="font-size: 12px; color: gray;">
                Built by <a href="https://github.com/rianlucascs" target="_blank">@rianlucascs</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )