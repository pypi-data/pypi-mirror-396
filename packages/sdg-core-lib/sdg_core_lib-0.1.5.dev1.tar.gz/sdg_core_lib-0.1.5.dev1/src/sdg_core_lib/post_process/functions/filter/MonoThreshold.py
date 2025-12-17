from sdg_core_lib.post_process.functions.UnspecializedFunction import (
    UnspecializedFunction,
)

import numpy as np


class MonoThreshold(UnspecializedFunction):
    def __init__(self, parameters: list[dict]):
        super().__init__(parameters)
        self.value = None
        self.strict = None
        self._check_parameters()

    def _check_parameters(self):
        param_mapping = {param.name: param for param in self.parameters}
        self.value = param_mapping["value"].value
        self.strict = param_mapping["strict"].value

    def _compute(self, data: np.array):
        pass

    def _evaluate(self, data: np.array):
        pass

    @classmethod
    def self_describe(cls):
        raise NotImplementedError
