from sdg_core_lib.post_process.functions.Parameter import Parameter


class FunctionInfo:
    def __init__(
        self,
        name: str,
        description: str,
        function_reference: str,
        parameters: list[Parameter],
    ):
        self.name = name
        self.description = description
        self.function_reference = function_reference
        self.Parameters = parameters

    def get_function_info(self):
        return {
            "function": {
                "name": self.name,
                "description": self.description,
                "function_reference": self.function_reference,
            },
            "parameters": [param.to_json() for param in self.Parameters],
        }
