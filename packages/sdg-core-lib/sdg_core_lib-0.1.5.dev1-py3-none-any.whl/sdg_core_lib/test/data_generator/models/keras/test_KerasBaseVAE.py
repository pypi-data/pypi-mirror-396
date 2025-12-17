import pytest

from sdg_core_lib.dataset.datasets import Table
from sdg_core_lib.data_generator.models.keras.KerasBaseVAE import KerasBaseVAE


@pytest.fixture()
def model():
    return KerasBaseVAE(
        metadata={},
        model_name="Test-T_VAE",
        input_shape="(13,)",
        load_path=None,
        latent_dim=2,
    )


@pytest.fixture()
def correct_dataset():
    data = [
        {
            "column_name": "A",
            "column_type": "continuous",
            "column_datatype": "float64",
            "column_data": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
    ]
    return Table.from_json(data, "./")


def test_instantiate(model):
    assert model._model is None
    with pytest.raises(NotImplementedError) as exception_info:
        model._instantiate()
    assert exception_info.type is NotImplementedError


def test_load_files(model):
    wrong_filepath = ""
    with pytest.raises(ValueError) as exception_info:
        model._load_files(wrong_filepath)
    assert exception_info.type is ValueError


def test_set_hyperparameters(model):
    hyperparams_wrong = {"wrong": 0.01, "test": 32, "foobar": 10}
    model.set_hyperparameters(**hyperparams_wrong)
    assert model._learning_rate is None
    assert model._batch_size is None
    assert model._epochs is None

    hyperparams = {"learning_rate": 0.01, "batch_size": 32, "epochs": 10}
    model.set_hyperparameters(**hyperparams)
    assert model._learning_rate == 0.01
    assert model._batch_size == 32
    assert model._epochs == 10


def test_train_not_initialized(model, correct_dataset):
    with pytest.raises(AttributeError) as exception_info:
        model.train(correct_dataset.get_computing_data())
    assert exception_info.type is AttributeError


def test_train_wrong_data(model):
    with pytest.raises(AttributeError) as exception_info:
        model.train([1, 2, 3])
    assert exception_info.type is AttributeError


def test_infer(model):
    with pytest.raises(AttributeError) as exception_info:
        model.infer(2)
    assert exception_info.type is AttributeError
