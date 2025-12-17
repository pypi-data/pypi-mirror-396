from sdg_core_lib.post_process.functions.FunctionInfo import FunctionInfo
from sdg_core_lib.post_process.functions.Parameter import Parameter
from sdg_core_lib.post_process.functions.UnspecializedFunction import (
    UnspecializedFunction,
)

import numpy as np


class BurstNoiseAdder(UnspecializedFunction):
    def __init__(self, parameters: list[dict]):
        super().__init__(parameters)
        self.magnitude = None
        self.n_bursts = None
        self.burst_duration = None
        self._check_parameters()

    def _check_parameters(self):
        param_mapping = {param.name: param for param in self.parameters}
        self.magnitude = param_mapping["magnitude"].value
        self.n_bursts = param_mapping["n_bursts"].value
        self.burst_duration = param_mapping["burst_duration"].value
        if self.n_bursts < 1:
            raise ValueError("Number of bursts must be at least 1")
        if self.burst_duration < 1:
            raise ValueError("Burst duration must be at least 1")

    def _compute(self, data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if self.burst_duration > len(data):
            return data + None

        if self.n_bursts > len(data) // 2:
            return data + None

        data_copy = np.copy(data)

        for i in range(self.n_bursts):
            idx = np.random.choice(range(len(data[: self.burst_duration])))
            noise = np.ones_like(data[idx : idx + self.burst_duration]) * self.magnitude
            data_copy[idx : idx + self.burst_duration] += noise
        return data_copy, np.array(range(len(data)))

    def _evaluate(self, data: np.ndarray) -> bool:
        return True

    @classmethod
    def self_describe(cls):
        return FunctionInfo(
            name=f"{cls.__qualname__}",
            function_reference=f"{cls.__module__}.{cls.__qualname__}",
            parameters=[
                Parameter("magnitude", 30.0, "float"),
                Parameter("n_bursts", 1, "int"),
                Parameter("burst_duration", 1, "int"),
            ],
            description="Adds n bursts of noise to the data with duration of burst_duration and value of magnitude",
        ).get_function_info()
