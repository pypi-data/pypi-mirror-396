from abc import ABC

import numpy as np
import os
import keras
from keras import saving

from sdg_core_lib.data_generator.models.UnspecializedModel import UnspecializedModel
from sdg_core_lib.data_generator.models.TrainingInfo import TrainingInfo

os.environ["KERAS_BACKEND"] = "tensorflow"


class KerasBaseVAE(UnspecializedModel, ABC):
    """
    Abstract base class for keras VAE models.

    This class provides a common interface for keras VAE models and handles the saving and loading of models.
    """

    def __init__(
        self,
        metadata: dict,
        model_name: str,
        input_shape: str,
        load_path: str | None,
        latent_dim: int,
    ):
        super().__init__(metadata, model_name, input_shape, load_path)
        self._latent_dim = latent_dim
        self._beta = None
        self._learning_rate = None
        self._batch_size = None
        self._epochs = None

    @staticmethod
    def _load_files(folder_path: str):
        """
        Loads the saved VAE model files from the given folder path.

        :param folder_path: path to the folder containing the saved model files
        :return: encoder and decoder models
        :raises FileNotFoundError: if the model files are not found in the given folder
        """
        encoder_filename = os.path.join(folder_path, "encoder.keras")
        decoder_filename = os.path.join(folder_path, "decoder.keras")
        encoder = saving.load_model(encoder_filename)
        decoder = saving.load_model(decoder_filename)
        return encoder, decoder

    def _load_model(self, encoder, decoder):
        raise NotImplementedError

    def _load(self, folder_path: str):
        encoder, decoder = self._load_files(folder_path)
        self._load_model(encoder, decoder)

    def _instantiate(self):
        """
        Instantiates the model and loads the saved model if the load_path is given.

        :return: None
        """
        if self._load_path is not None:
            self._load(self._load_path)
            return
        if not self._model and self.input_shape:
            self._model = self._build(self.input_shape)

    def save(self, folder_path: str):
        """
        Saves the model and scaler to the given folder path.

        :param folder_path: path to the folder to save the model
        :raises FileNotFoundError: if the folder does not exist
        :raises AttributeError: if the model does not exist
        :return: None
        """
        encoder_filename = os.path.join(folder_path, "encoder.keras")
        decoder_filename = os.path.join(folder_path, "decoder.keras")
        saving.save_model(self._model.encoder, encoder_filename)
        saving.save_model(self._model.decoder, decoder_filename)

    def fine_tune(self, data: np.ndarray, **kwargs):
        raise NotImplementedError

    def _build(self, input_shape: str):
        raise NotImplementedError

    def _set_hyperparams(self, learning_rate, batch_size, epochs):
        self._learning_rate = learning_rate
        self._batch_size = batch_size
        self._epochs = epochs

    def set_hyperparameters(self, **kwargs):
        learning_rate = kwargs.get("learning_rate", self._learning_rate)
        batch_size = kwargs.get("batch_size", self._batch_size)
        epochs = kwargs.get("epochs", self._epochs)
        self._set_hyperparams(learning_rate, batch_size, epochs)

    def train(
        self,
        data: np.ndarray,
        learning_rate: float = None,
        batch_size: int = None,
        epochs: int = None,
    ):
        """
        Trains the VAE model on the provided data.

        :param data: the dataset to train the model on, must be a NumericDataset
        :param learning_rate: optional, the learning rate to use for training
        :param batch_size: optional, the batch size to use for training
        :param epochs: optional, the number of epochs to train the model for
        :raises TypeError: if the data is not of type NumericDataset
        :raises ValueError: if the model shape does not match data shape
        :return: None
        """
        learning_rate = (
            learning_rate if learning_rate is not None else self._learning_rate
        )
        batch_size = batch_size if batch_size is not None else self._batch_size
        epochs = epochs if epochs is not None else self._epochs
        self._model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate)
        )
        history = self._model.fit(data, epochs=epochs, batch_size=batch_size, verbose=1)
        self.training_info = TrainingInfo(
            loss_fn="ELBO",
            train_loss=history.history["loss"][-1].numpy().item(),
            train_samples=data.shape[0],
            validation_loss=-1,
            validation_samples=0,
        )

    def infer(self, n_rows: int, **kwargs):
        """
        Performs inference using the trained VAE model.

        :param n_rows: Number of rows to generate.
        :param kwargs: Additional arguments for inference, not currently used.
        :raises AttributeError: If the model is not instantiated.
        :return: A numpy array containing the generated data after decoding and inverse scaling.
        """
        z_random = np.random.normal(size=(n_rows, self._latent_dim))
        results = self._model.decoder.predict(z_random)
        return results

    @classmethod
    def self_describe(cls):
        raise NotImplementedError
