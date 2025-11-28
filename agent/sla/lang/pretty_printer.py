import json

from agent.sla.lang.metamodel import SLA, GuaranteeTerm, QualifyingCondition, SLO, BoolExpression, QoSMetric, \
    DerivedQoSMetric, QoSDriftMetric, Comparison, Provider, Scope


class SLAPrettyPrinter:
    def __init__(self, sla:SLA):
        self._sla:SLA = sla
        self._metrics = []
        self._derived_metrics = []
        self._drift_metrics = []
        self._providers = []

    def json(self):
        return json.dumps(self.__visit_SLA(self._sla), indent=4)

    def __visit_SLA(self, node:SLA):
        json_terms = [self.__visit_GuaranteeTerm(term) for term in node.guarantee_term]
        return {
            "GuaranteeTerm":json_terms,
            "QoSMetric": self._metrics,
            "DerivedQoSMetric": self._derived_metrics,
            "QoSDriftMetric": self._drift_metrics,
            "Provider": self._providers
        }

    def __visit_GuaranteeTerm(self, node:GuaranteeTerm):
        json_scopes = []
        json_conds = []
        json_slos = []
        for scope in node.scope:
            json_scopes.append(self.__visit_Scope(scope))
        for cond in node.qualifying_condition:
            json_conds.append(self.__visit_QualifyingCondition(cond))
        for slo in node.slo:
            json_slos.append(self.__visit_SLO(slo))
        return {
            "Scope": json_scopes,
            "QualifyingCondition": json_conds,
            "SLO": json_slos
        }

    def __visit_Scope(self, node:Scope):
        return {
            "name": node.name,
            "tasks": node.tasks
        }

    def __visit_QualifyingCondition(self, node:QualifyingCondition):
        expression = self.__visit_BoolExpression(node.boolexpression)
        return {
            "name": node.name,
            "BoolExpression": expression
        }

    def __visit_SLO(self, node:SLO):
        expression = self.__visit_BoolExpression(node.boolexpression)
        return {
            "name": node.name,
            "BoolExpression": expression
        }

    def __visit_BoolExpression(self, node:BoolExpression):
        if isinstance(node, Comparison):
            return self.__visit_Comparison(node)
        else:
            expressions = []
            for expr in node.expressions:
                expressions.append(self.__visit_BoolExpression(expr))

            return {
                "type": node.__class__.__name__,
                "BoolExpression": expressions
            }

    def __visit_Comparison(self, node:Comparison):
        if isinstance(node.qosmetric, QoSMetric):
            self._metrics.append(self.__visit_QoSMetric(node.qosmetric))
        elif isinstance(node.qosmetric, DerivedQoSMetric):
            self._derived_metrics.append(self.__visit_DerivedQoSMetric(node.qosmetric))
        elif isinstance(node.qosmetric, QoSDriftMetric):
            self._drift_metrics.append(self.__visit_QoSDriftMetric(node.qosmetric))

        return {
            "type": "Comparison",
            "QoSMetric": node.qosmetric.name,
            "operator": node.operator.value,
            "value": node.value
        }

    def __visit_QoSMetric(self, node:QoSMetric):
        self._providers.append(self.__visit_Provider(node.provider))
        return {
            "name": node.name,
            "description": node.description,
            "metric_type": node.metric_type.value,
            "unit": node.unit.value,
            "uncertainty": node.uncertainty,
            "Provider": node.provider.name
        }

    def __visit_DerivedQoSMetric(self, node:DerivedQoSMetric):
        self._providers.append(self.__visit_Provider(node.provider))
        return {
            "name": node.name,
            "description": node.description,
            "metric_type": node.metric_type.value,
            "unit": node.unit.value,
            "uncertainty": node.uncertainty,
            "window": node.window,
            "window_unit": node.window_unit.value,
            "aggregation": node.aggregation.value,
            "Provider": node.provider.name
        }

    def __visit_QoSDriftMetric(self, node:QoSDriftMetric):
        self._providers.append(self.__visit_Provider(node.provider))
        return {
            "name": node.name,
            "description": node.description,
            "metric_type": node.metric_type.value,
            "unit": node.unit.value,
            "uncertainty": node.uncertainty,
            "window": node.window,
            "window_unit": node.window_unit.value,
            "aggregation": node.aggregation.value,
            "Provider": node.provider.name
        }

    def __visit_Provider(self, node:Provider):
        return {
            "name": node.name,
            "confidence": node.confidence,
            "reputation": node.reputation
        }