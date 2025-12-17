import pytest

from sdg_core_lib.data_generator.models.ModelInfo import ModelInfo, AllowedData


@pytest.fixture()
def model_info():
    return ModelInfo(
        default_loss_function="Test Loss Function",
        description="This is a test model",
        allowed_data=[AllowedData("int64", False), AllowedData("float32", False)],
        name="Test",
    )


def test_get_data(model_info):
    info = model_info.get_model_info()
    assert info is not None
    assert info["algorithm"] is not None
    assert info["algorithm"]["default_loss_function"] == "Test Loss Function"
    assert info["algorithm"]["description"] == "This is a test model"
    assert info["algorithm"]["name"] == "Test"
    assert len(info["datatypes"]) == 2
    assert info["datatypes"][0]["type"] == "int64"
    assert not info["datatypes"][0]["is_categorical"]
    assert info["datatypes"][1]["type"] == "float32"
    assert not info["datatypes"][1]["is_categorical"]
