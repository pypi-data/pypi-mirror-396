import pytest

from sdg_core_lib.data_generator.model_factory import dynamic_import, model_factory
from sdg_core_lib.data_generator.models.keras.implementation.TabularVAE import (
    TabularVAE,
)


@pytest.fixture()
def class_name():
    return (
        "sdg_core_lib.data_generator.models.keras.implementation.TabularVAE.TabularVAE"
    )


@pytest.fixture()
def shapeless_model():
    return {
        "algorithm_name": "sdg_core_lib.data_generator.models.keras.implementation.TabularVAE.TabularVAE",
        "model_name": "Test-T_VAE",
    }


@pytest.fixture()
def shape_model():
    return {
        "algorithm_name": "sdg_core_lib.data_generator.models.keras.implementation.TabularVAE.TabularVAE",
        "model_name": "Test-T_VAE",
        "input_shape": "(13,)",
    }


def test_dynamic_import(class_name):
    model_class = dynamic_import(class_name)
    assert model_class is not None
    assert model_class is TabularVAE


def test_model_factory_empty(shapeless_model):
    model = model_factory(shapeless_model, input_shape="(13,)")
    assert type(model) is TabularVAE
    assert model.input_shape == (13,)
    assert model._model is not None
    assert model.model_name is shapeless_model["model_name"]


def test_model_factory_full(shape_model):
    model = model_factory(shape_model)
    assert type(model) is TabularVAE
    assert model.input_shape == (13,)
    assert model._model is not None
    assert model.model_name is shape_model["model_name"]
