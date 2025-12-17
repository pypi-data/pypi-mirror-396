import pytest

from sdg_core_lib.data_generator.models.UnspecializedModel import UnspecializedModel


@pytest.fixture(autouse=False)
def unspecialized_model():
    return UnspecializedModel(
        metadata={}, model_name="Test-T_VAE", input_shape="(13,)", load_path=None
    )


def test_initialize():
    with pytest.raises(TypeError) as exception_info:
        _ = UnspecializedModel(
            metadata={}, model_name="Test-T_VAE", input_shape="(13,)", load_path=None
        )
    assert exception_info.type is TypeError


def test_parse_stringed_input_shape():
    stringed_shape_1 = "(10,)"
    stringed_shape_2 = "(10)"
    stringed_shape_3 = "[10,]"
    stringed_shape_4 = "{10,}"
    stringed_shape_5 = "(13,10,)"

    assert UnspecializedModel._parse_stringed_input_shape(stringed_shape_1) == (10,)
    assert UnspecializedModel._parse_stringed_input_shape(stringed_shape_2) == (10,)
    assert UnspecializedModel._parse_stringed_input_shape(stringed_shape_3) == (10,)
    assert UnspecializedModel._parse_stringed_input_shape(stringed_shape_4) == (10,)
    assert UnspecializedModel._parse_stringed_input_shape(stringed_shape_5) == (13, 10)
