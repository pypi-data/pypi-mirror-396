import json


class TrainingInfo:
    def __init__(
        self,
        loss_fn: str,
        train_samples: int,
        train_loss: float,
        validation_samples: int = None,
        validation_loss: float = None,
    ):
        self._loss_fn = loss_fn
        self._train_samples = train_samples
        self._train_loss = train_loss
        self._validation_samples = validation_samples
        self._validation_loss = validation_loss

    def to_dict(self) -> dict:
        """
        Convert the TrainingInfo to a dictionary

        :return: dict: A dictionary with the training info
        """
        return {
            "loss_function": self._loss_fn,
            "train_samples": self._train_samples,
            "train_loss": self._train_loss,
            "val_samples": self._validation_samples,
            "val_loss": self._validation_loss,
        }

    def to_json(self) -> str:
        """
        Convert the TrainingInfo to a JSON string

        :return: str: A JSON string with the training info
        """

        return json.dumps(self.to_dict())
