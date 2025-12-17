import numpy as np
from abc import ABC, abstractmethod


class UnspecializedModel(ABC):
    """
    Abstract class for all models. Implements common functionalities and defines abstract methods that must be implemented
    by all subclasses.

    Attributes:
        _metadata (dict): A dictionary containing miscellaneous information about the model.
        model_name (str): The model name, used to identify the model itself.
        input_shape (tuple): A tuple containing the input shape of the model.
        _load_path (str): A string containing the path where to load the model from.
        _model (keras.Model): The model instance.
        _scaler (Scaler): The scaler instance.
        training_info (TrainingInfo): The training info instance.
    """

    def __init__(
        self,
        metadata: dict,
        model_name: str,
        input_shape: str = None,
        load_path: str = None,
    ):
        self._metadata = metadata
        self.model_name = model_name
        self.input_shape = self._parse_stringed_input_shape(input_shape)
        self._load_path = load_path
        self._model = None  # Placeholder for the model instance
        self.training_info = None  # Placeholder for training info
        self._model_misc = None  # Placeholder for model miscellaneous info

    @abstractmethod
    def _build(self, input_shape: str):
        raise NotImplementedError

    @abstractmethod
    def _load(self, model_filepath: str):
        """Load trained_models weights."""
        raise NotImplementedError

    @abstractmethod
    def _instantiate(self):
        raise NotImplementedError

    @abstractmethod
    def train(self, data: np.ndarray):
        """Train the model."""
        raise NotImplementedError

    @abstractmethod
    def fine_tune(self, data: np.ndarray, **kwargs):
        """Fine-tune the model."""
        raise NotImplementedError

    @abstractmethod
    def infer(self, n_rows: int, **kwargs):
        """Run inference."""
        raise NotImplementedError

    @abstractmethod
    def save(self, folder_path):
        """Save Model."""
        raise NotImplementedError

    @abstractmethod
    def set_hyperparameters(self, **kwargs):
        """Set Hyperparameters"""
        raise NotImplementedError

    @classmethod
    def self_describe(cls):
        raise NotImplementedError

    @staticmethod
    def _parse_stringed_input_shape(stringed_shape: str) -> tuple[int, ...]:
        """
        Parses a stringed list of numbers into a tuple

        :param stringed_shape: a stringed list of number in format "[x,y,z]"
        :return: a tuple of numbers, in format (x, y, z)
        """
        brackets = ["(", ")", "[", "]", "{", "}"]
        for b in brackets:
            stringed_shape = stringed_shape.replace(b, "")
        return tuple([int(n) for n in stringed_shape.split(",") if n != ""])
