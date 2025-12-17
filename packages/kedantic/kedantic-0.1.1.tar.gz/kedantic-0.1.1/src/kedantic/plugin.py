from kedro.framework.hooks import hook_impl
from kedro.pipeline.node import Node
from pydantic import BaseModel
from inspect import Parameter, signature
from typing import Any


class KedanticHook:
    def _get_new_input(self, inputs: dict[str, Any], input_key: str, param: Parameter):
        if len(input_key.split("params:")) < 2:
            return
        if not issubclass(param.annotation, BaseModel):
            return
        if not isinstance(inputs[input_key], dict):
            return
        inputs[input_key] = param.annotation(**inputs[input_key])

    @hook_impl
    def before_node_run(
        self, node: Node, catalog, inputs: dict[str, Any]
    ) -> dict[str, Any] | None:
        sig = signature(node.func)
        node_inputs = node._inputs
        if node_inputs is None:
            return None
        if isinstance(node_inputs, str):
            node_inputs = [node_inputs]
        if isinstance(node_inputs, list):
            for input, param in zip(node_inputs, sig.parameters.values()):
                self._get_new_input(inputs, input, param)
        else:
            for input in node_inputs:
                self._get_new_input(inputs, node_inputs[input], sig.parameters[input])
        return inputs


hooks = KedanticHook()
