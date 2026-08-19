

from streamlit_apps.apps.streamlit_app_pipelines.repositories.checkpoints_repository import CheckpointsRepository
from streamlit_apps.apps.streamlit_app_pipelines.repositories.pipeline_repository import PipelineRepository

import streamlit as st


st.title("Checkpoints")

pipeline_repository = PipelineRepository()
pipelines = pipeline_repository.list_pipelines()

st.selectbox(
    "Selecione o pipeline para visualizar os logs",
    pipelines,
    key="selected_pipeline",
    on_change=lambda: st.session_state.update({"selected_pipeline": st.session_state.selected_pipeline})
)


checkpoints_repository = CheckpointsRepository(
    pipeline=st.session_state.selected_pipeline
)


selected_folder_checkpoint_0 = st.selectbox(
    "Selecione o Stage",
    checkpoints_repository._list_checkpoints(),
    format_func=lambda item: item[1],
    key="selected_folder_checkpoint_0"
)


selected_folder_checkpoint_1 = st.selectbox(
    "Selecione o Step",
    checkpoints_repository._list_checkpoints(selected_folder_checkpoint_0[0]),
    format_func=lambda item: item[1],
    key="selected_folder_checkpoint_1"
)


selected_folder_checkpoint_2 = st.selectbox(
    "Selecione o arquivo",
    checkpoints_repository._list_checkpoints(
        selected_folder_checkpoint_1[0]
    ),
    format_func=lambda item: item[1],
    key="selected_folder_checkpoint_2"
)


if selected_folder_checkpoint_2[0].is_dir():

    selected_folder_checkpoint_3 = st.selectbox(
        "Selecione o arquivo",
        checkpoints_repository._list_checkpoints(
            selected_folder_checkpoint_2[0]
        ),
        format_func=lambda item: item[1],
        key="selected_folder_checkpoint_3"
    )


st.text_area(
    "Conteúdo do arquivo",
    value=checkpoints_repository.read(
        selected_folder_checkpoint_3[0] if selected_folder_checkpoint_2[0].is_dir() else selected_folder_checkpoint_2[0]
    ),
    height=400,
) 