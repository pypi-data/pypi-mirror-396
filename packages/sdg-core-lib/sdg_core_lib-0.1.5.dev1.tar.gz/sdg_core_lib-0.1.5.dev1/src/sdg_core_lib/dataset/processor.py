from abc import ABC, abstractmethod

from sdg_core_lib.dataset.steps import NoneStep
from sdg_core_lib.dataset.steps import OneHotEncoderWrapper
from sdg_core_lib.dataset.columns import Column, Numeric, Categorical
from sdg_core_lib.dataset.steps import Step, ScalerWrapper
import numpy as np


class Processor(ABC):
    def __init__(self, dir_path: str):
        self.dir_path = dir_path
        self.steps: dict[int, list[Step]] = {}
        self.idx_to_data: dict[int, int] = {}

    @abstractmethod
    def _init_steps(self, data: list):
        raise NotImplementedError

    def add_steps(
        self, steps: list[Step], col_position: int, data_position: int
    ) -> "Processor":
        self.steps[col_position] = steps
        self.idx_to_data[col_position] = data_position
        return self

    def _save_all(self):
        [
            step.save(self.dir_path)
            for step_list in self.steps.values()
            for step in step_list
        ]

    def _load_all(self) -> "Processor":
        [
            step.load(self.dir_path)
            for step_list in self.steps.values()
            for step in step_list
        ]
        return self

    def process(self, data: list) -> dict[int, np.ndarray]:
        results = {
            idx: step.fit_transform(data[self.idx_to_data[idx]])
            for idx, step_list in self.steps.items()
            for step in step_list
        }
        self._save_all()
        return results

    def inverse_process(self, data: list) -> dict[int, np.ndarray]:
        self._load_all()
        return {
            idx: step.inverse_transform(data[self.idx_to_data[idx]])
            for idx, step_list in self.steps.items()
            for step in reversed(step_list)
        }


class TableProcessor(Processor):
    def __init__(self, dir_path: str):
        super().__init__(dir_path)

    # TODO: External config?
    def _init_steps(self, columns: list[Column]):
        if len(self.steps.keys()) == len(columns):
            pass

        if len(columns) == 0:
            raise ValueError("No columns provided for processing")
        for idx, col in enumerate(columns):
            step_list = []
            if isinstance(col, Numeric):
                step_list.append(ScalerWrapper(col.position, col.name, "standard"))
            elif isinstance(col, Categorical):
                step_list.append(OneHotEncoderWrapper(col.position, col.name))
            elif type(col) is Column:
                step_list.append(NoneStep(col.position))
            else:
                raise NotImplementedError()

            self.add_steps(step_list, col_position=col.position, data_position=idx)

    def process(self, columns: list[Column]) -> list[Column]:
        self._init_steps(columns)
        col_data = [col.get_data() for col in columns]
        results = super().process(col_data)
        preprocessed_columns = []
        for col in columns:
            preprocessed_columns.append(
                type(col)(
                    col.name,
                    col.value_type,
                    col.position,
                    results.get(col.position),
                    col.column_type,
                )
            )
        return preprocessed_columns

    def inverse_process(self, preprocessed_columns: list[Column]) -> list[Column]:
        self._init_steps(preprocessed_columns)
        col_data = [col.get_data() for col in preprocessed_columns]
        results = super().inverse_process(col_data)
        post_processed_columns = []
        for col in preprocessed_columns:
            post_processed_columns.append(
                type(col)(
                    col.name,
                    col.value_type,
                    col.position,
                    results.get(col.position),
                    col.column_type,
                )
            )
        return post_processed_columns
