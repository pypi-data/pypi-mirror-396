import numpy as np

from sdg_core_lib.post_process.functions.FunctionInfo import FunctionInfo
from sdg_core_lib.post_process.functions.Parameter import Parameter
from sdg_core_lib.post_process.functions.filter.MonoThreshold import MonoThreshold


class UpperThreshold(MonoThreshold):
    def __init__(self, parameters: list[dict]):
        super().__init__(parameters)

    def _compute(self, data: np.array):
        if self.strict:
            indexes = np.less_equal(data, self.value)
        else:
            indexes = np.less(data, self.value)
        return data[indexes], indexes

    def _evaluate(self, data: np.array):
        return True

    @classmethod
    def self_describe(cls):
        return FunctionInfo(
            name=f"{cls.__qualname__}",
            function_reference=f"{cls.__module__}.{cls.__qualname__}",
            parameters=[
                Parameter("value", 0.0, "float"),
                Parameter("strict", True, "bool"),
            ],
            description="Mono-threshold function: picks value less than an upper threshold",
        ).get_function_info()
