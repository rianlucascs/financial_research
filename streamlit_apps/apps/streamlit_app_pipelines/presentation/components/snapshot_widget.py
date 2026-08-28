

import streamlit as st


def render_snapshot_widget(pipelines_data: list[dict]) -> None:
    """
    pipelines_data = [
        {
            "pipeline": "Pipeline 1",
            "processes": [
                {"name": "raw", "executed_at": "08:12", "has_error": False},
                {"name": "to_interim", "executed_at": "08:14", "has_error": False},
                {"name": "to_processed", "executed_at": "08:15", "has_error": True},
            ]
        }
    ]
    """

    st.markdown(
        """
        <style>
        .excel-table {
            width: 100%;
            border-collapse: collapse;
            font-family: Calibri, Arial, sans-serif;
            background-color: #1E1E1E;
        }
        .excel-table th.pipeline-header {
            font-size: 16px;
            padding: 8px 10px;
        }
        .excel-table th.column-header {
            border-bottom: 4px solid #3A3A3A;
        }
        .excel-table th, .excel-table td {
            border: 1px solid #3A3A3A;
            padding: 6px 10px;
            font-size: 13px;
            color: #E1E1E1;
        }
        .excel-table th {
            background-color: #2D2D2D;
            font-weight: 600;
            text-align: center;
            color: #FFFFFF;
        }
        .excel-table td:first-child {
            text-align: left;
        }
        .excel-table td:last-child {
            text-align: center;
        }
        .excel-table tr:nth-child(even) td {
            background-color: #262626;
        }
        .excel-error {
            background-color: #4C1D1D !important;
            color: #FF8080 !important;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3)

    for index, data in enumerate(pipelines_data):

        with cols[index % 3]:

            row_htmls = []
            for p in data["processes"]:
                name = p["name"]
                executed_at = p["executed_at"]
                has_error = p["has_error"]

                error_class = ' class="excel-error"' if has_error else ""

                row_htmls.append(
                    f'<tr>'
                    f'<td{error_class}>{name}</td>'
                    f'<td{error_class}>{executed_at}</td>'
                    f'</tr>'
                )

            rows = "".join(row_htmls)
            pipeline_name = data["pipeline"]

            table_html = (
                f'<table class="excel-table">'
                f'<thead>'
                f'<tr><th colspan="2" class="pipeline-header">{pipeline_name}</th></tr>'
                f'<tr><th class="column-header">Processo</th><th class="column-header">Execução</th></tr>'
                f'</thead>'
                f'<tbody>{rows}</tbody>'
                f'</table>'
            )

            st.markdown(table_html, unsafe_allow_html=True) 