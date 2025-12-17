import numpy as np
import keras

from sdg_core_lib.data_generator.models.ModelInfo import ModelInfo, AllowedData
from sdg_core_lib.data_generator.models.keras.KerasBaseVAE import KerasBaseVAE
from keras import layers

from sdg_core_lib.data_generator.models.keras.VAE import Sampling, VAE


class TimeSeriesVAE(KerasBaseVAE):
    """
    TimeSeriesVAE is a Variational Autoencoder designed for generating synthetic time series data.

    This model is particularly useful in scenarios where time series data needs to be generated for
    testing or simulation purposes. It leverages the power of variational inference to learn latent
    representations of time series data, enabling the generation of new, similar sequences.

    Attributes:
        _beta (float): Coefficient for the KL divergence term in the VAE loss.
        _learning_rate (float): Learning rate for the optimizer.
        _epochs (int): Number of training epochs.
        _batch_size (int): Number of samples per gradient update.

    Methods:
        _load_model(encoder, decoder): Loads the VAE model with the specified encoder and decoder.
        _build(input_shape): Constructs the VAE model architecture.
        _pre_process(data, **kwargs): Pre-processes the input data for training.
        self_describe(): Provides a description of the model, including its name, loss function, and allowed data types.
    """

    def __init__(
        self,
        metadata: dict,
        model_name: str,
        input_shape: str,
        load_path: str,
        latent_dim: int = 2,
        learning_rate: float = 1e-3,
        batch_size: int = 16,
        epochs: int = 100,
    ):
        super().__init__(metadata, model_name, input_shape, load_path, latent_dim)
        self._beta = 0.15
        self._learning_rate = learning_rate
        self._epochs = epochs
        self._batch_size = batch_size
        self._instantiate()

    def _load_model(self, encoder, decoder):
        self._model = VAE(encoder, decoder, self._beta)

    def _build(self, input_shape: tuple[int, ...]):
        print(input_shape)
        encoder_inputs = keras.Input(shape=input_shape)
        encoder_inputs_permute = layers.Permute((2, 1))(encoder_inputs)
        x = layers.Conv1D(
            32,
            9,
            activation="relu",
            padding="valid",
            strides=1,
            data_format="channels_last",
        )(encoder_inputs_permute)
        x = layers.Conv1D(
            64,
            5,
            activation="relu",
            padding="valid",
            strides=1,
            data_format="channels_last",
        )(x)
        shape_before_flatten = x.shape[1:]
        x = layers.Flatten()(x)
        x = layers.Dense(16, activation="relu")(x)
        z_mean = layers.Dense(self._latent_dim, name="z_mean")(x)
        z_log_var = layers.Dense(self._latent_dim, name="z_log_var")(x)
        z = Sampling()([z_mean, z_log_var])
        encoder = keras.Model(encoder_inputs, [z_mean, z_log_var, z], name="encoder")

        latent_inputs = keras.Input(shape=(self._latent_dim,))
        y = layers.Dense(np.prod(shape_before_flatten), activation="relu")(
            latent_inputs
        )
        y = layers.Reshape(shape_before_flatten)(y)
        y = layers.Conv1DTranspose(
            64,
            5,
            activation="relu",
            padding="valid",
            strides=1,
            data_format="channels_last",
        )(y)
        y = layers.Conv1DTranspose(
            32,
            9,
            activation="relu",
            padding="valid",
            strides=1,
            data_format="channels_last",
        )(y)
        decoder_outputs = layers.Conv1DTranspose(
            input_shape[0], 3, activation="relu", padding="same"
        )(y)
        decoder_outputs_permute = layers.Permute((2, 1))(decoder_outputs)
        decoder = keras.Model(latent_inputs, decoder_outputs_permute, name="decoder")

        vae = VAE(encoder, decoder, self._beta, name="TimeSeriesVAE")
        encoder.summary()
        decoder.summary()
        vae.summary()
        return vae

    @classmethod
    def self_describe(cls):
        return ModelInfo(
            name=f"{cls.__module__}.{cls.__qualname__}",
            default_loss_function="ELBO LOSS",
            description="A Beta-Variational Autoencoder for time series generation",
            allowed_data=[
                AllowedData("float32", False),
                AllowedData("int32", False),
                AllowedData("int64", False),
                AllowedData("int32", True),
                AllowedData("str", True),
            ],
        ).get_model_info()
