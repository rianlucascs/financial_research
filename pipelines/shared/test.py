

from context import PipelineContext


def test_pipeline_context():
    ctx = PipelineContext()
    assert ctx.project_root.name == "financial_research"
    assert ctx.pipelines_dir.name == "pipelines"
    assert ctx.data_dir.name == "data"
    assert ctx.logs_dir.name == "logs"
    assert ctx.state_dir.name == "state"


