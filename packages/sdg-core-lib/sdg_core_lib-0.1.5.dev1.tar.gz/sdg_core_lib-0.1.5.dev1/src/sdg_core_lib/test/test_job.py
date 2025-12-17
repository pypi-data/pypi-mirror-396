import shutil
import pytest
from sdg_core_lib.job import train, infer
import json
import os
from loguru import logger

current_folder = os.path.dirname(os.path.abspath(__file__))
train_request = json.load(open(os.path.join(current_folder, "train_test.json")))
train_request_2 = json.load(open(os.path.join(current_folder, "train_test_2.json")))

infer_request = json.load(open(os.path.join(current_folder, "infer_test.json")))
infer_nodata_request = json.load(
    open(os.path.join(current_folder, "infer_test_nodata.json"))
)
infer_nodata_request_wrong = json.load(
    open(os.path.join(current_folder, "infer_test_nodata_wrong.json"))
)
output_folder = os.path.join(current_folder, "outputs")


@pytest.fixture()
def setup():
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)


@pytest.fixture()
def teardown():
    yield
    if os.path.isdir(output_folder):
        shutil.rmtree(output_folder)


def test_train_timeseries(setup):
    model_info = train_request_2["model"]
    dataset = train_request_2["dataset"]
    n_rows = train_request_2["n_rows"]
    save_filepath = output_folder

    results, metrics, model, data = train(
        model_info=model_info,
        dataset=dataset,
        n_rows=n_rows,
        save_filepath=save_filepath,
    )
    assert isinstance(results, list)
    assert results is not None
    assert model is not None
    assert data is not None


def test_train(setup):
    model_info = train_request["model"]
    dataset = train_request["dataset"]
    n_rows = train_request["n_rows"]
    save_filepath = output_folder

    results, metrics, model, data = train(
        model_info=model_info,
        dataset=dataset,
        n_rows=n_rows,
        save_filepath=save_filepath,
    )

    logger.add(
        os.path.join(current_folder, "out.log"),
    )
    assert isinstance(results, list)
    assert results is not None
    logger.info(results)
    assert metrics is not None
    logger.info(metrics)
    assert model is not None
    logger.info(model.training_info.to_json())
    assert data is not None
    logger.info(data)


def test_infer(setup):
    model_info = infer_request["model"]
    model_info["image"] = output_folder
    dataset = infer_request["dataset"]
    n_rows = infer_request["n_rows"]
    save_filepath = output_folder

    (
        results,
        metrics,
    ) = infer(
        model_info=model_info,
        dataset=dataset,
        n_rows=n_rows,
        save_filepath=save_filepath,
    )
    assert isinstance(results, list)
    assert results is not None
    assert metrics is not None


def test_infer_nodata_wrong(setup):
    model_info = infer_nodata_request_wrong["model"]
    model_info["image"] = output_folder
    n_rows = infer_nodata_request_wrong["n_rows"]
    save_filepath = output_folder

    with pytest.raises(ValueError) as exception_info:
        (
            _,
            _,
        ) = infer(
            model_info=model_info,
            dataset={"dataset_type": "table", "data": []},
            n_rows=n_rows,
            save_filepath=save_filepath,
        )
    assert exception_info.type is ValueError


def test_infer_nodata(setup, teardown):
    model_info = infer_nodata_request["model"]
    model_info["image"] = output_folder
    n_rows = infer_nodata_request["n_rows"]
    save_filepath = output_folder

    results, metrics = infer(
        model_info=model_info,
        dataset={"dataset_type": "table", "data": []},
        n_rows=n_rows,
        save_filepath=save_filepath,
    )
    assert isinstance(results, list)
    assert results is not None
    print(results)
    assert metrics is not None
    print(metrics)
