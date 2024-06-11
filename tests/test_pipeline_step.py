# tests/test_pipeline_step.py

import pytest
from src.pipeline_step import PipelineStep

class DummyStep(PipelineStep):
    def run(self, input_data):
        return input_data

def test_pipeline_step():
    step = DummyStep()
    result = step.run("test_input")
    assert result == "test_input"
