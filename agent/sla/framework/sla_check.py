import math
import statistics
import time
from typing import Iterable

from agent.sla.framework.agent import Measurement
from agent.sla.lang.metamodel import SLA, BoolExpression, QoSMetric, DerivedQoSMetric, QoSDriftMetric, Comparison, And, \
    Or, Operator, QoSMetricType, WindowUnit, AggregationFunction


def check_sla(sla:SLA, measurements:dict[QoSMetricType,list[Measurement]]) -> bool:
    for term in sla.guarantee_term:
        pass_conditions = True
        for cond in term.qualifying_condition:
            valid = check_expression(cond.boolexpression, measurements)
            if not valid:
                pass_conditions = False
                break
        if not pass_conditions:
            continue

        for slo in term.slo:
            valid = check_expression(slo.boolexpression, measurements)
            if not valid:
                return False
    return True

def check_expression(expr:BoolExpression, measurements:dict[QoSMetricType,list[Measurement]]) -> bool:
    if isinstance(expr, Comparison):
        metric_value:float = 0.0
        if isinstance(expr.qosmetric, DerivedQoSMetric):
            metric_value = compute_derived_metric(expr.qosmetric, measurements)
        elif isinstance(expr.qosmetric, QoSDriftMetric):
            metric_value = compute_drift_metric(expr.qosmetric, measurements)
        elif isinstance(expr.qosmetric, QoSMetric):
            metric_value = compute_metric(expr.qosmetric, measurements)
        match expr.operator:
            case Operator.LESS:
                return metric_value < expr.value
            case Operator.LESSEQ:
                return metric_value <= expr.value
            case Operator.GREATER:
                return metric_value > expr.value
            case Operator.GREATEREQ:
                return metric_value >= expr.value
            case Operator.EQUAL:
                return math.isclose(metric_value, expr.value)
    elif isinstance(expr, And):
        for subexpr in expr.expressions:
            if not check_expression(subexpr, measurements):
                return False
        return True
    elif isinstance(expr, Or):
        for subexpr in expr.expressions:
            if check_expression(subexpr, measurements):
                return True
        return False

def compute_metric(metric:QoSMetric, measurements:dict[QoSMetricType,list[Measurement]]) -> float:
    metric_measurements = reversed(measurements[metric.metric_type])
    return next(iter(metric_measurements))._value


def compute_derived_metric(metric:DerivedQoSMetric, measurements:dict[QoSMetricType,list[Measurement]]) -> float:
    metric_measurements = reversed(measurements[metric.metric_type])
    if metric.window_unit == WindowUnit.MESSAGE:
        window = measures_in_message_window(metric, metric_measurements, 0)
    else: # time based grouping
        now = time.time()
        window = measures_in_time_window(metric, metric_measurements, now)

    return aggregate(metric, window)

def compute_drift_metric(metric:QoSDriftMetric, measurements:dict[QoSMetricType,list[Measurement]]) -> float:
    metric_measurements = reversed(measurements[metric.metric_type])
    if metric.window_unit == WindowUnit.MESSAGE:
        sooner = measures_in_message_window(metric, metric_measurements, 0)
        later = measures_in_message_window(metric, metric_measurements, metric.window)
    else:  # time based grouping
        now = time.time()
        before = get_time_bound(metric, now)
        sooner = measures_in_time_window(metric, metric_measurements, now)
        later = measures_in_time_window(metric, metric_measurements, before)

    sooner_val = aggregate(metric, sooner)
    later_val = aggregate(metric, later)

    return sooner_val - later_val


def measures_in_message_window(metric, measurements:Iterable[Measurement], start):
    return measurements[start:(start+metric.window)]


def measures_in_time_window(metric, measurements:Iterable[Measurement], start):
    window = []
    bound = get_time_bound(metric, start)

    for measure in measurements:
        if measure._timestamp < bound:
            break
        window.append(measure._value)
    return window

def get_time_bound(metric, start):
    sec_per_unit = 1
    match metric.window_unit:
        case WindowUnit.MIN:
            sec_per_unit = 60
        case WindowUnit.HOUR:
            sec_per_unit = 60 * 60
        case WindowUnit.DAY:
            sec_per_unit = 60 * 60 * 24
    return start - (sec_per_unit * metric.window)

def aggregate(metric, window:list[float]):
    match metric.aggregation:
        case AggregationFunction.MIN:
            return min(window)
        case AggregationFunction.MAX:
            return max(window)
        case AggregationFunction.AVG:
            return statistics.mean(window)
        case AggregationFunction.MED:
            return statistics.median(window)