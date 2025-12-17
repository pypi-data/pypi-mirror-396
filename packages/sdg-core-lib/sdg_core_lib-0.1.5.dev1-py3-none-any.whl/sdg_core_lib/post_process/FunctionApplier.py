import numpy as np

from sdg_core_lib.post_process.functions.UnspecializedFunction import (
    UnspecializedFunction,
)


class FunctionApplier:
    def __init__(self, functions: list[UnspecializedFunction], data: list[np.ndarray]):
        self.functions = functions
        self.data = data

    def apply(self):
        pass
