from sdg_core_lib.post_process.functions.UnspecializedFunction import (
    UnspecializedFunction,
)

import numpy as np


class IntervalThreshold(UnspecializedFunction):
    def __init__(self, parameters: list[dict]):
        super().__init__(parameters)
        self.upper_bound = None
        self.lower_bound = None
        self.upper_strict = None
        self.lower_strict = None
        self._check_parameters()

    def _check_parameters(self):
        param_mapping = {param.name: param for param in self.parameters}
        self.upper_bound = param_mapping["upper_bound"].value
        self.lower_bound = param_mapping["lower_bound"].value
        self.upper_strict = param_mapping["upper_strict"].value
        self.lower_strict = param_mapping["lower_strict"].value

    def _compute(self, data: np.array):
        pass

    def _evaluate(self, data: np.array):
        pass

    @classmethod
    def self_describe(cls):
        raise NotImplementedError
