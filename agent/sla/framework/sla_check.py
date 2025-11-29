import math
import statistics
import time
from aenum import Enum
from typing import Iterable, Type

from agent.sla.lang.metamodel import SLA, BoolExpression, QoSMetric, DerivedQoSMetric, QoSDriftMetric, Comparison, And, \
    Or, Operator, QoSMetricType, WindowUnit, AggregationFunction, QoSMetricUnit


class UncertaintyMode(Enum):
    DEFAULT = "DEFAULT"
    STRICT = "STRICT"
    RELAXED = "RELAXED"

def check_sla(sla:SLA, measurements:dict[Type[QoSMetricType],list], uncertainty_mode:UncertaintyMode) -> bool:
    for term in sla.guarantee_term:
        pass_conditions = True
        for cond in term.qualifying_condition:
            valid = check_expression(cond.boolexpression, measurements, uncertainty_mode)
            if not valid:
                pass_conditions = False
                break
        if not pass_conditions:
            continue

        for slo in term.slo:
            valid = check_expression(slo.boolexpression, measurements, uncertainty_mode)
            if not valid:
                return False
    return True

def check_expression(expr:BoolExpression, measurements:dict[Type[QoSMetricType],list], uncertainty_mode:UncertaintyMode) -> bool:
    if isinstance(expr, Comparison):
        metric_measure:float = 0.0
        if isinstance(expr.qosmetric, DerivedQoSMetric):
            metric_measure = compute_derived_metric(expr.qosmetric, measurements)
        elif isinstance(expr.qosmetric, QoSDriftMetric):
            metric_measure = compute_drift_metric(expr.qosmetric, measurements)
        elif isinstance(expr.qosmetric, QoSMetric):
            metric_measure = compute_metric(expr.qosmetric, measurements)

        low_bound = metric_measure - expr.qosmetric.uncertainty
        high_bound = metric_measure + expr.qosmetric.uncertainty
        match expr.operator:
            case Operator.LESS:
                match uncertainty_mode:
                    case UncertaintyMode.DEFAULT:
                        return metric_measure < (expr.value * get_seconds_factor(expr.qosmetric.unit))
                    case UncertaintyMode.STRICT:
                        return high_bound < (expr.value * get_seconds_factor(expr.qosmetric.unit))
                    case UncertaintyMode.RELAXED:
                        return low_bound < (expr.value * get_seconds_factor(expr.qosmetric.unit))
            case Operator.LESSEQ:
                match uncertainty_mode:
                    case UncertaintyMode.DEFAULT:
                        return metric_measure <= (expr.value * get_seconds_factor(expr.qosmetric.unit))
                    case UncertaintyMode.STRICT:
                        return high_bound <= (expr.value * get_seconds_factor(expr.qosmetric.unit))
                    case UncertaintyMode.RELAXED:
                        return low_bound <= (expr.value * get_seconds_factor(expr.qosmetric.unit))
            case Operator.GREATER:
                match uncertainty_mode:
                    case UncertaintyMode.DEFAULT:
                        return metric_measure > (expr.value * get_seconds_factor(expr.qosmetric.unit))
                    case UncertaintyMode.STRICT:
                        return low_bound > (expr.value * get_seconds_factor(expr.qosmetric.unit))
                    case UncertaintyMode.RELAXED:
                        return high_bound > (expr.value * get_seconds_factor(expr.qosmetric.unit))
            case Operator.GREATEREQ:
                match uncertainty_mode:
                    case UncertaintyMode.DEFAULT:
                        return metric_measure >= (expr.value * get_seconds_factor(expr.qosmetric.unit))
                    case UncertaintyMode.STRICT:
                        return low_bound >= (expr.value * get_seconds_factor(expr.qosmetric.unit))
                    case UncertaintyMode.RELAXED:
                        return high_bound >= (expr.value * get_seconds_factor(expr.qosmetric.unit))
            case Operator.EQUAL:
                match uncertainty_mode:
                    case UncertaintyMode.DEFAULT:
                        return math.isclose(metric_measure, (expr.value * get_seconds_factor(expr.qosmetric.unit)))
                    case UncertaintyMode.STRICT:
                        return (math.isclose(low_bound, (expr.value * get_seconds_factor(expr.qosmetric.unit))) and
                                math.isclose(high_bound, (expr.value * get_seconds_factor(expr.qosmetric.unit))))
                    case UncertaintyMode.RELAXED:
                        return (high_bound >= (expr.value * get_seconds_factor(expr.qosmetric.unit)) and
                                low_bound <= (expr.value * get_seconds_factor(expr.qosmetric.unit)))

    elif isinstance(expr, And):
        for subexpr in expr.expressions:
            if not check_expression(subexpr, measurements, uncertainty_mode):
                return False
        return True
    elif isinstance(expr, Or):
        for subexpr in expr.expressions:
            if check_expression(subexpr, measurements, uncertainty_mode):
                return True
        return False

def compute_metric(metric:QoSMetric, measurements:dict[Type[QoSMetricType],list]) -> float:
    metric_measurements = reversed(measurements[metric.metric_type])
    return next(iter(metric_measurements))._value


def compute_derived_metric(metric:DerivedQoSMetric, measurements:dict[Type[QoSMetricType],list]) -> float:
    metric_measurements = reversed(measurements[metric.metric_type])
    if metric.window_unit == WindowUnit.MESSAGE:
        window = measures_in_message_window(metric, metric_measurements, 0)
    else: # time based grouping
        now = time.time()
        window = measures_in_time_window(metric, metric_measurements, now)

    return aggregate(metric, window)

def compute_drift_metric(metric:QoSDriftMetric, measurements:dict[Type[QoSMetricType],list]) -> float:
    metric_measurements = reversed(measurements[metric.metric_type])
    if metric.window_unit == WindowUnit.MESSAGE:
        sooner = measures_in_message_window(metric, metric_measurements, 0)
        later = measures_in_message_window(metric, metric_measurements, metric.window)
    else:  # time based grouping
        now = time.time()
        before = get_time_bound(metric, now)
        sooner = measures_in_time_window(metric, metric_measurements, now)
        later = measures_in_time_window(metric, metric_measurements, before)

    sooner_measure = aggregate(metric, sooner)
    later_measure = aggregate(metric, later)
    return sooner_measure - later_measure


def measures_in_message_window(metric, measurements:Iterable, start):
    return measurements[start:(start+metric.window)]


def measures_in_time_window(metric, measurements:Iterable, start):
    window = []
    bound = get_time_bound(metric, start)

    for measure in measurements:
        if measure._timestamp < bound:
            break
        window.append(measure)
    return window

def get_seconds_factor(unit):
    match unit:
        case QoSMetricUnit.MILLISECONDS:
            sec_per_unit = 0.1
        case WindowUnit.MIN | QoSMetricUnit.MINUTES:
            sec_per_unit = 60
        case WindowUnit.HOUR | QoSMetricUnit.HOURS:
            sec_per_unit = 60 * 60
        case WindowUnit.DAY:
            sec_per_unit = 60 * 60 * 24
        case _:
            sec_per_unit = 1
    return sec_per_unit


def get_time_bound(metric, start):
    sec_per_unit = get_seconds_factor(metric.window_unit)
    return start - (sec_per_unit * metric.window)

def aggregate(metric, window:list) -> float:
    values = [measure._value for measure in window]
    match metric.aggregation:
        case AggregationFunction.MIN:
            return min(values)
        case AggregationFunction.MAX:
            return max(values)
        case AggregationFunction.AVG:
            return statistics.mean(values)
        case AggregationFunction.MED:
            return statistics.median(values)