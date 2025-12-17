class AllowedData:
    def __init__(self, dtype: str, is_categorical: bool):
        self.dtype = dtype
        self.is_categorical = is_categorical

    def to_json(self):
        return {"type": self.dtype, "is_categorical": self.is_categorical}


class ModelInfo:
    def __init__(
        self,
        name: str,
        default_loss_function: str,
        description: str,
        allowed_data: list[AllowedData],
    ):
        self.name = name
        self.default_loss_function = default_loss_function
        self.description = description
        self.allowed_data = allowed_data

    def get_model_info(self):
        """
        Returns a dictionary containing the model information.

        The dictionary includes the model's name, default loss function, description,
        and a list of allowed data types with their categorical status.

        :return: dict containing the model's information
        """
        allowed_data = [ad.to_json() for ad in self.allowed_data]
        system_model_info = {
            "algorithm": {
                "name": self.name,
                "default_loss_function": self.default_loss_function,
                "description": self.description,
            },
            "datatypes": allowed_data,
        }

        return system_model_info
