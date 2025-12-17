from sdg_core_lib.evaluate.metrics import (
    Metric,
    StatisticalMetric,
    AdherenceMetric,
    NoveltyMetric,
    MetricReport,
)


def test_metric_init():
    metric = Metric("title", "unit measure", 1.0)
    assert metric.title == "title"
    assert metric.unit_measure == "unit measure"
    assert metric.value == 1.0


def test_statistical_metric_init():
    metric = StatisticalMetric("title", "unit measure", 1.0)
    assert metric.title == "title"
    assert metric.unit_measure == "unit measure"
    assert metric.value == 1.0
    assert metric.type == "statistical_metrics"


def test_adherence_metric_init():
    metric = AdherenceMetric("title", "unit measure", 1.0)
    assert metric.title == "title"
    assert metric.unit_measure == "unit measure"
    assert metric.value == 1.0
    assert metric.type == "adherence_metrics"


def test_novelty_metric_init():
    metric = NoveltyMetric("title", "unit measure", 1.0)
    assert metric.title == "title"
    assert metric.unit_measure == "unit measure"
    assert metric.value == 1.0
    assert metric.type == "novelty_metrics"


def test_metric_report_init():
    report = MetricReport()
    assert report.report == {}


def test_metric_report_add_metric():
    report = MetricReport()
    metric = StatisticalMetric("title", "unit measure", 1.0)
    report.add_metric(metric)
    assert len(report.report["statistical_metrics"]) == 1


def test_metric_report_to_json():
    report = MetricReport()
    metric = StatisticalMetric("title", "unit measure", 1.0)
    report.add_metric(metric)
    json_report = report.to_json()
    assert json_report["statistical_metrics"][0] == {
        "title": "title",
        "unit_measure": "unit measure",
        "value": 1.0,
    }
