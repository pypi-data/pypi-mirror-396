import numpy as np

from sdg_core_lib.post_process.functions.FunctionInfo import FunctionInfo
from sdg_core_lib.post_process.functions.Parameter import Parameter
from sdg_core_lib.post_process.functions.filter.IntervalThreshold import (
    IntervalThreshold,
)


class OuterThreshold(IntervalThreshold):
    def __init__(self, parameters: list[dict]):
        super().__init__(parameters)

    def _compute(self, data: np.array):
        if self.lower_strict:
            upper_indexes = np.greater_equal(data, self.upper_bound)
        else:
            upper_indexes = np.greater(data, self.upper_bound)

        if self.upper_strict:
            lower_indexes = np.less_equal(data, self.lower_bound)
        else:
            lower_indexes = np.less(data, self.lower_bound)
        final_indexes = lower_indexes | upper_indexes
        return data[final_indexes], final_indexes

    def _evaluate(self, data: np.array):
        return True

    @classmethod
    def self_describe(cls):
        return FunctionInfo(
            name=f"{cls.__qualname__}",
            function_reference=f"{cls.__module__}.{cls.__qualname__}",
            parameters=[
                Parameter("lower_bound", 0.0, "float"),
                Parameter("upper_bound", 1.0, "float"),
                Parameter("lower_strict", True, "bool"),
                Parameter("upper_strict", True, "bool"),
            ],
            description="Filters data outside a given interval",
        ).get_function_info()
