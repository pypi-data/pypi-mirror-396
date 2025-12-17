import keras
from keras import layers

from sdg_core_lib.data_generator.models.ModelInfo import ModelInfo, AllowedData
from sdg_core_lib.data_generator.models.keras.KerasBaseVAE import KerasBaseVAE
from sdg_core_lib.data_generator.models.keras.VAE import Sampling, VAE


class TabularVAE(KerasBaseVAE):
    """
    TabularVAE is a class that implements a Variational Autoencoder (VAE) for tabular data generation.
    It inherits from the KerasBaseVAE class and provides functionality specific to handling tabular data.

    Attributes:
        _latent_dim (int): The dimensionality of the latent space.
        _beta (float): The beta parameter for the VAE loss function.
        _learning_rate (float): Learning rate for the optimizer.
        _batch_size (int): Number of samples per batch during training.
        _epochs (int): Number of training epochs.
        _scaler: Scaler used for standardizing input data.

    Methods:
        __init__: Initializes the TabularVAE with model parameters.
        _load_model: Loads the VAE model with specified encoder and decoder.
        _build: Builds the VAE model architecture.
        _pre_process: Pre-processes input data using standardization.
        self_describe: Provides metadata information about the model.
    """

    def __init__(
        self,
        metadata: dict,
        model_name: str,
        input_shape: str,
        load_path: str | None,
        latent_dim: int = 2,
        learning_rate: float = 1e-3,
        batch_size: int = 8,
        epochs: int = 200,
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
        encoder_inputs = keras.Input(shape=input_shape)
        x = layers.Dense(64, activation="relu")(encoder_inputs)
        x = layers.Dense(128, activation="relu")(x)
        x = layers.Dense(16, activation="relu")(x)
        z_mean = layers.Dense(self._latent_dim, name="z_mean")(x)
        z_log_var = layers.Dense(self._latent_dim, name="z_log_var")(x)
        z = Sampling()([z_mean, z_log_var])
        encoder = keras.Model(encoder_inputs, [z_mean, z_log_var, z], name="encoder")

        latent_inputs = keras.Input(shape=(self._latent_dim,))
        y = layers.Dense(16, activation="relu")(latent_inputs)
        y = layers.Dense(128, activation="relu")(y)
        y = layers.Dense(64, activation="relu")(y)
        decoder_outputs = layers.Dense(input_shape[0], activation="linear")(y)
        decoder = keras.Model(latent_inputs, decoder_outputs, name="decoder")

        vae = VAE(encoder, decoder, self._beta, name="TabularVAE")
        vae.summary()
        return vae

    @classmethod
    def self_describe(cls):
        return ModelInfo(
            name=f"{cls.__module__}.{cls.__qualname__}",
            default_loss_function="ELBO LOSS",
            description="A Variational Autoencoder for data generation",
            allowed_data=[
                AllowedData("float32", False),
                AllowedData("int32", False),
                AllowedData("int64", False),
                AllowedData("int32", True),
                AllowedData("str", True),
            ],
        ).get_model_info()
