import numpy as np


class FunctionResult:
    def __init__(self, result: np.array, indexes: np.array, evaluation_result: bool):
        self.indexes = indexes
        self.result = result
        self.evaluation_result = evaluation_result

    def to_dict(self):
        return {
            "indexes": self.indexes,
            "results": self.result,
            "evaluation_results": self.evaluation_result,
        }
