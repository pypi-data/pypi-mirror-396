class Metric:
    def __init__(self, title: str, unit_measure: str, value: float | int | dict):
        self.title = title
        self.unit_measure = unit_measure
        self.value = value
        self.type = None

    def to_json(self):
        return {
            "title": self.title,
            "unit_measure": self.unit_measure,
            "value": self.value,
        }


class StatisticalMetric(Metric):
    def __init__(self, title: str, unit_measure: str, value: float | int | dict):
        super().__init__(title, unit_measure, value)
        self.type = "statistical_metrics"


class AdherenceMetric(Metric):
    def __init__(self, title: str, unit_measure: str, value: float | int | dict):
        super().__init__(title, unit_measure, value)
        self.type = "adherence_metrics"


class NoveltyMetric(Metric):
    def __init__(self, title: str, unit_measure: str, value: float | int | dict):
        super().__init__(title, unit_measure, value)
        self.type = "novelty_metrics"


class TimeSeriesSpecificMetric(Metric):
    def __init__(self, title: str, unit_measure: str, value: float | int | dict):
        super().__init__(title, unit_measure, value)
        self.type = "time_series_metrics"


class MetricReport:
    def __init__(self):
        self.report = {}

    def add_metric(self, metric: Metric):
        if metric.type not in self.report:
            self.report[metric.type] = [metric.to_json()]
        else:
            self.report[metric.type].append(metric.to_json())

    def to_json(self):
        if len(self.report) == 0:
            return {}

        return self.report
