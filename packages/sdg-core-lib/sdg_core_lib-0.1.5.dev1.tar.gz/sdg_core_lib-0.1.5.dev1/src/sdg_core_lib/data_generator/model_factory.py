import importlib

from sdg_core_lib.data_generator.models.UnspecializedModel import UnspecializedModel


def dynamic_import(class_name: str):
    """
    Dynamically imports a class given its name.

    :param class_name: a string with the full name of the class to import
    :return: the class itself
    """
    module_name, class_name = class_name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def model_factory(model_dict: dict, input_shape: str = None) -> UnspecializedModel:
    """
    This function is a generic model factory. Takes a dictionary containing useful model information and plugs
    them in the model itself.
    Input shape may be passed as an argument (i.e) from the request data itself, or [alternatively] may be present in
    model dictionary. If not explicitly passed, it will use the model dictionary

    :param model_dict: A dictionary containing model information, structured as follows:
    {
        "image" -> contains the possible path where to find the model image. If not none, model will be loaded from there
        "metadata" -> a dictionary itself, containing miscellaneous information
        "algorithm_name" -> includes the model class module to _load
        "model_name" -> the model name, used to identify the model itself
        "input_shape" [optional] -> contains a stringed tuple that identifies the input layer shape
    }
    :param input_shape:
    :return: An instance of a BaseModel class or any subclass
    """
    model_file, metadata, model_type, model_name, input_shape_model = parse_model_info(
        model_dict
    )
    if input_shape is None:
        input_shape = input_shape_model

    ModelClass = dynamic_import(model_type)
    model = ModelClass(
        metadata=metadata,
        model_name=model_name,
        input_shape=input_shape,
        load_path=model_file,
    )
    return model


def parse_model_info(model_dict: dict):
    """
    Extracts the necessary information from the model dictionary and returns them as separate arguments.

    :param model_dict: A dictionary containing model information, structured as follows:
    {
        "image" -> contains the possible path where to find the model image. If not none, model will be loaded from there
        "metadata" -> a dictionary itself, containing miscellaneous information
        "algorithm_name" -> includes the model class module to _load
        "model_name" -> the model name, used to identify the model itself
        "input_shape" [optional] -> contains a stringed tuple that identifies the input layer shape
    }
    :return: model_file, metadata, model_type, model_name, input_shape
    """
    model_file = model_dict.get("image", None)
    metadata = model_dict.get("metadata", {})
    model_type = model_dict.get("algorithm_name")
    model_name = model_dict.get("model_name")
    input_shape = model_dict.get("input_shape", "")

    return model_file, metadata, model_type, model_name, input_shape
