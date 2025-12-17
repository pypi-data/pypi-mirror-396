from sdg_core_lib.dataset.datasets import Table, TimeSeries
from sdg_core_lib.evaluate.tables import TabularComparisonEvaluator
from sdg_core_lib.evaluate.time_series import TimeSeriesComparisonEvaluator
from sdg_core_lib.data_generator.model_factory import model_factory
from sdg_core_lib.data_generator.models.UnspecializedModel import UnspecializedModel

dataset_mapping = {
    "table": {"dataset": Table, "evaluator": TabularComparisonEvaluator},
    "time_series": {"dataset": TimeSeries, "evaluator": TimeSeriesComparisonEvaluator},
}


def train(
    model_info: dict, dataset: dict, n_rows: int, save_filepath: str
) -> tuple[list[dict], dict, UnspecializedModel, list[dict]]:
    """
    Main function to run the job.

    This function will run the Synthetic Data Generation job. It will create an instance of the specified model or
    load the specified dataset, pre-process the data, train the model (if specified to do so), generate synthetic
    data, evaluate the generated data and save the results to the specified location.

    :param model_info: a dictionary containing the model's information
    :param dataset: a list of dataframes
    :param n_rows: the number of rows to generate
    :param save_filepath: the path to save the results
    :return: a tuple containing a list of metrics, a dictionary with the model's info, the trained model, and the generated dataset
    """

    data_payload = dataset.get("data", [])
    dataset_type = dataset.get("dataset_type", "")
    dataset_class = dataset_mapping[dataset_type]["dataset"]
    dataset_evaluator_class = dataset_mapping[dataset_type]["evaluator"]

    data = dataset_class.from_json(data_payload, save_filepath)

    preprocessed_data = data.preprocess()
    preprocess_schema = preprocessed_data.to_skeleton()
    model = model_factory(model_info, preprocessed_data.get_shape_for_model())
    model.train(data=preprocessed_data.get_computing_data())
    model.save(save_filepath)

    predicted_data = model.infer(n_rows)
    synthetic_data = preprocessed_data.clone(predicted_data)
    synthetic_data = synthetic_data.postprocess()

    evaluator = dataset_evaluator_class(
        real_data=data,
        synthetic_data=synthetic_data,
    )
    report = evaluator.compute()
    results = synthetic_data.to_json()

    return results, report, model, preprocess_schema


def infer(
    model_info: dict, dataset: dict, n_rows: int, save_filepath: str
) -> tuple[list[dict], dict]:
    dataset_type = dataset.get("dataset_type", "")
    dataset_class = dataset_mapping[dataset_type]["dataset"]
    dataset_evaluator_class = dataset_mapping[dataset_type]["evaluator"]

    data_payload = dataset.get("data", [])
    data = None
    if len(data_payload) == 0:
        data_skeleton = model_info.get("training_data_info")
        preprocessed_data = dataset_class.from_skeleton(data_skeleton, save_filepath)
    else:
        data = dataset_class.from_json(data_payload, save_filepath)
        preprocessed_data = data.preprocess()

    model = model_factory(model_info)
    predicted_data = model.infer(n_rows)
    synthetic_data = preprocessed_data.clone(predicted_data)
    synthetic_data = synthetic_data.postprocess()

    report = {"available": "false"}
    if data is not None:
        evaluator = dataset_evaluator_class(
            real_data=data,
            synthetic_data=synthetic_data,
        )
        report = evaluator.compute()

    results = synthetic_data.to_json()

    return results, report
