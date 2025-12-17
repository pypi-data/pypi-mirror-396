from inspect import Parameter
from kedantic.plugin import KedanticHook
from unittest.mock import MagicMock
from pydantic import BaseModel
from kedro.pipeline.node import Node


class MockModel(BaseModel):
    test: str = "test"


def mock_func(
    test_data: dict,
    test_params: MockModel,
    test_params_2={},
    test_params_3: MockModel = MockModel(test="test"),
):
    pass


def test_get_new_input():
    hook = KedanticHook()

    # Check non "params:" input key has no side effects
    inputs = {}
    input_key = "test_key"
    param = MagicMock(Parameter)
    hook._get_new_input(inputs, input_key, param)
    assert inputs == {}

    # Check that non Base Model parameter has no side effects
    input_key = "params:test"
    param.annotation = dict
    hook._get_new_input(inputs, input_key, param)
    assert inputs == {}

    # Check that input that isn't a dict has no side effect
    inputs = {"params:test": "test"}
    param.annotation = MockModel
    hook._get_new_input(inputs, input_key, param)
    assert inputs == {"params:test": "test"}

    # Check inputs get changed to model when proper condition
    inputs = {"params:test": {"test": "check"}}
    hook._get_new_input(inputs, input_key, param)
    assert inputs == {"params:test": MockModel(test="check")}


def test_before_node_run():
    hook = KedanticHook()
    node = MagicMock(Node)
    node._inputs = None
    node.func = mock_func
    inputs = {}
    assert hook.before_node_run(node, None, inputs) is None

    node._inputs = ["data", "params:test"]
    inputs = {"data": {"test": "data"}, "params:test": {"test": "params"}}
    output = hook.before_node_run(node, None, inputs)
    assert isinstance(output, dict)
    assert output["params:test"] == MockModel(test="params")
    assert output["data"] == {"test": "data"}

    node._inputs = {
        "test_data": "data",
        "test_params": "params:test",
        "test_params_3": "params:other",
    }
    inputs = {
        "data": {"test": "data"},
        "params:test": {"test": "params"},
        "params:other": {"test": "other"},
    }
    output = hook.before_node_run(node, None, inputs)
    assert isinstance(output, dict)
    assert output["params:test"] == MockModel(test="params")
    assert output["data"] == {"test": "data"}
    assert output["params:other"] == MockModel(test="other")
