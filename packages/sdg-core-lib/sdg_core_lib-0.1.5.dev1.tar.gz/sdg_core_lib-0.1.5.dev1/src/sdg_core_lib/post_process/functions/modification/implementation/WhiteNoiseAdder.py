from sdg_core_lib.post_process.functions.FunctionInfo import FunctionInfo
from sdg_core_lib.post_process.functions.Parameter import Parameter
from sdg_core_lib.post_process.functions.UnspecializedFunction import (
    UnspecializedFunction,
)
import numpy as np


class WhiteNoiseAdder(UnspecializedFunction):
    def __init__(self, parameters: list[dict]):
        super().__init__(parameters)
        self.mean = None
        self.std = None
        self._check_parameters()

    def _check_parameters(self):
        param_mapping = {param.name: param for param in self.parameters}
        self.mean = param_mapping["mean"].value
        self.std = param_mapping["standard_deviation"].value

    def _compute(self, data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        noise = np.random.normal(self.mean, self.std, data.shape)
        return data + noise, np.array(range(len(data)))

    def _evaluate(self, data: np.ndarray) -> bool:
        return True

    @classmethod
    def self_describe(cls):
        return FunctionInfo(
            name=f"{cls.__qualname__}",
            function_reference=f"{cls.__module__}.{cls.__qualname__}",
            parameters=[
                Parameter("mean", 0.0, "float"),
                Parameter("standard_deviation", 1.0, "float"),
            ],
            description="Adds white noise to the data",
        ).get_function_info()
