import pytest

from sdg_core_lib.dataset.datasets import Table
from sdg_core_lib.evaluate.tables import TabularComparisonEvaluator
from sdg_core_lib.evaluate.metrics import (
    Metric,
    StatisticalMetric,
    AdherenceMetric,
    NoveltyMetric,
    MetricReport,
)

# Test data
dummy_json = [
    {
        "column_name": "a",
        "column_type": "continuous",
        "column_data": [1, 2, 3, 1, 2, 3],
        "column_datatype": "int",
    },
    {
        "column_name": "b",
        "column_type": "categorical",
        "column_data": [1, 1, 1, 2, 2, 2],
        "column_datatype": "int",
    },
    {
        "column_name": "c",
        "column_type": "continuous",
        "column_data": [1, 2, 3, 4, 5, 6],
        "column_datatype": "float32",
    },
    {
        "column_name": "d",
        "column_type": "categorical",
        "column_data": ["a", "b", "c", "d", "e", "f"],
        "column_datatype": "str",
    },
]

# Edge case test data
empty_json = []
single_numeric_json = [
    {
        "column_name": "single",
        "column_type": "continuous",
        "column_data": [1],
        "column_datatype": "int",
    }
]
single_categorical_json = [
    {
        "column_name": "single",
        "column_type": "categorical",
        "column_data": ["a"],
        "column_datatype": "str",
    }
]
nan_data_json = [
    {
        "column_name": "with_nan",
        "column_type": "continuous",
        "column_data": [1.0, 2.0, float("nan"), 4.0],
        "column_datatype": "float32",
    }
]


# Fixtures
@pytest.fixture()
def real_data():
    return Table.from_json(dummy_json, None)


@pytest.fixture()
def synthetic_data():
    return Table.from_json(dummy_json, None)


@pytest.fixture()
def single_numeric_table():
    return Table.from_json(single_numeric_json, None)


@pytest.fixture()
def single_categorical_table():
    return Table.from_json(single_categorical_json, None)


@pytest.fixture()
def nan_data_table():
    return Table.from_json(nan_data_json, None)


@pytest.fixture()
def evaluator_correct(real_data, synthetic_data):
    return TabularComparisonEvaluator(real_data, synthetic_data)


@pytest.fixture()
def metric_report():
    return MetricReport()


def test_init(evaluator_correct, real_data, synthetic_data):
    # Test initialization with correct data
    assert evaluator_correct._real_data == real_data
    assert evaluator_correct._synth_data == synthetic_data
    assert isinstance(evaluator_correct.report, MetricReport)


def test_init_with_invalid_inputs():
    # Test initialization with invalid inputs
    with pytest.raises(TypeError, match="real_data must be a Table"):
        TabularComparisonEvaluator("not a table", Table.from_json(dummy_json, None))

    with pytest.raises(TypeError, match="synthetic_data must be a Table"):
        TabularComparisonEvaluator(Table.from_json(dummy_json, None), "not a table")


def test_evaluate(evaluator_correct):
    # Test the complete evaluation pipeline
    report = evaluator_correct.compute()
    print(report)

    # Basic structure checks
    assert isinstance(report, dict)
    assert "statistical_metrics" in report
    assert "adherence_metrics" in report
    assert "novelty_metrics" in report

    # Check statistical metrics
    statistical_metrics = report["statistical_metrics"]
    statistical_metrics_titles = [metric["title"] for metric in statistical_metrics]

    expected_metrics = [
        "Association Distance Index (Cramer's V, Real vs Synthetic)",
        "Continuous Features Statical Distance (Wasserstein Distance)",
        "Categorical Frequency Difference",
    ]

    for metric in expected_metrics:
        assert metric in statistical_metrics_titles

    # Check adherence metrics
    adherence_metrics = report["adherence_metrics"]
    assert len(adherence_metrics) >= 2  # At least two types of adherence metrics

    # Check novelty metrics
    novelty_metrics = report["novelty_metrics"]
    assert len(novelty_metrics) >= 2  # At least two types of novelty metrics

    for metric in novelty_metrics:
        assert 0 <= metric["value"] <= 100  # Should be percentages


def test_evaluate_edge_cases(
    single_numeric_table, single_categorical_table, nan_data_table
):
    # Test with single numeric column
    evaluator = TabularComparisonEvaluator(single_numeric_table, single_numeric_table)
    report = evaluator.compute()
    assert "statistical_metrics" in report

    # Test with single categorical column
    evaluator = TabularComparisonEvaluator(
        single_categorical_table, single_categorical_table
    )
    report = evaluator.compute()
    assert "adherence_metrics" in report

    # Test with NaN values
    evaluator = TabularComparisonEvaluator(nan_data_table, nan_data_table)
    report = evaluator.compute()
    assert report != {}


def test_metric_classes():
    # Test base Metric class
    metric = Metric("test", "unit", 42)
    assert metric.title == "test"
    assert metric.unit_measure == "unit"
    assert metric.value == 42
    assert metric.type is None

    # Test StatisticalMetric
    stat_metric = StatisticalMetric("stat", "unit", 0.8)
    assert stat_metric.type == "statistical_metrics"

    # Test AdherenceMetric
    adh_metric = AdherenceMetric("adh", "unit", 0.9)
    assert adh_metric.type == "adherence_metrics"

    # Test NoveltyMetric
    nov_metric = NoveltyMetric("nov", "unit", 0.7)
    assert nov_metric.type == "novelty_metrics"


def test_metric_report(metric_report):
    # Test adding metrics
    metric1 = StatisticalMetric("test1", "unit", 1)
    metric2 = StatisticalMetric("test2", "unit", 2)

    metric_report.add_metric(metric1)
    metric_report.add_metric(metric2)

    # Test report structure
    report = metric_report.to_json()
    assert "statistical_metrics" in report
    assert len(report["statistical_metrics"]) == 2

    # Test empty report
    empty_report = MetricReport().to_json()
    assert empty_report == {}
