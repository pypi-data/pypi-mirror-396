import importlib

from sdg_core_lib.post_process.functions.UnspecializedFunction import (
    UnspecializedFunction,
)


def dynamic_import(class_name: str):
    """
    Dynamically imports a class given its name.

    :param class_name: a string with the full name of the class to import
    :return: the class itself
    """
    module_name, class_name = class_name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def function_factory(function_dict: dict) -> UnspecializedFunction:
    """
    This function is a generic model factory. Takes a dictionary containing useful model information and plugs
    them in the model itself.
    Input shape may be passed as an argument (i.e) from the request data itself, or [alternatively] may be present in
    model dictionary. If not explicitly passed, it will use the model dictionary

    :return: An instance of a BaseModel class or any subclass
    """
    function_name, parameter_list = parse_function_info(function_dict)
    function_class = dynamic_import(function_name)
    function = function_class(parameters=parameter_list)
    return function


def parse_function_info(function_dict: dict):
    """ """

    function_name = function_dict["function_reference"]
    parameter_list = function_dict["parameters"]

    return function_name, parameter_list
