from email.policy import default

from agent.sla.lang.metamodel import QoSMetricType, QoSMetric, QoSMetricUnit, Provider, SLA, WindowUnit, \
    AggregationFunction, DerivedQoSMetric, QoSDriftMetric, GuaranteeTerm, Scope, QualifyingCondition, SLO, And, Or, \
    Comparison, Operator
from agent.sla.lang.errors import ErrorMessage, NotInEnum, UndefinedLabel, OutOfBound, NoUnit


class SLAVisitor:

    def __init__(self):
        self.model_cards = dict()
        self.agents = dict()
        self.providers = dict()
        self.metrics = dict()
        self.errors: list[ErrorMessage] = list()



    def visit_SLA(self, struct):

        # cards = struct.get("ModelCard")
        # if cards is not None:
        #     for card in cards:
        #         mcard = ModelCard(card.get("name"), card.get("model_card"))
        #         self.model_cards[card.get("name")] = mcard
        #
        # agents = struct.get("Agent")
        # if agents is not None:
        #     for agent in agents:
        #         mc = None
        #         if agent.get("ModelCard") is not None and agent.get("ModelCard") not in self.model_cards:
        #             self.errors.append(UndefinedLabel(agent.get("ModelCard"), "ModelCard"))
        #         else:
        #             mc = self.model_cards[agent.get("ModelCard")]
        #         ag = Agent(agent.get("description"), agent.get("url"), agent.get("name"), mc)
        #         self.agents[agent.get("name")] = ag

        providers = struct.get("Provider")
        if providers is not None:
            for provider in providers:
                if provider.get("confidence") > 1 or provider.get("confidence") < 0:
                    self.errors.append(OutOfBound(str(provider.get("confidence"))))
                    self.providers[provider.get("name")] = None
                    continue
                prov = Provider(provider.get("name"), provider.get("confidence"), provider.get("reputation"))
                self.providers[provider.get("name")] = prov

        metrics = struct.get("QoSMetric")
        if metrics is not None:
            for metric in metrics:
                qos_metric = self.visit_QoSMetric(metric)
                self.metrics[metric.get("name")] = qos_metric

        metrics = struct.get("DerivedQoSMetric")
        if metrics is not None:
            for metric in metrics:
                qos_metric = self.visit_DerivedQoSMetric(metric)
                self.metrics[metric.get("name")] = qos_metric

        metrics = struct.get("QoSDriftMetric")
        if metrics is not None:
            for metric in metrics:
                qos_metric = self.visit_QoSDriftMetric(metric)
                self.metrics[metric.get("name")] = qos_metric

        terms = struct.get("GuaranteeTerm")
        guarantee_terms = []
        for term in terms:
            guarantee_terms.append(self.visit_GuaranteeTerm(term))

        return SLA(guarantee_terms)



    def visit_GuaranteeTerm(self, struct):
        gt = GuaranteeTerm([],[],[])
        scopes = struct.get("Scope")
        for scope in scopes:
            gt.scope.append(Scope(scope.get("name"), gt, scope.get("tasks", [])))
            # if scope.get("Agent") not in self.agents:
            #     self.errors.append(UndefinedLabel(scope.get("Agent"), "Agent"))
            # else:
            #     gt.scope.append(Scope(scope.get("name"), gt, self.agents[scope.get("Agent")]))

        conditions = struct.get("QualifyingCondition")
        if conditions is not None:
            for condition in conditions:
                gt.qualifying_condition.append(self.visit_QualifyingCondition(condition, gt))

        slos = struct.get("SLO")
        for slo in slos:
            gt.slo.append(self.visit_SLO(slo, gt))

        return gt



    def visit_QualifyingCondition(self, struct, term):
        expr = self.visit_BoolExpression(struct.get("BoolExpression"))
        return QualifyingCondition(struct.get("name"), term, expr)



    def visit_SLO(self, struct, term):
        expr = self.visit_BoolExpression(struct.get("BoolExpression"))
        return SLO(struct.get("name"), term, expr)



    def visit_BoolExpression(self, struct):
        if struct.get("type") == "And" or struct.get("type") == "Or":
            operands = struct.get("BoolExpression")
            exprs = []
            for operand in operands:
                exprs.append(self.visit_BoolExpression(operand))

            if struct.get("type") == "And":
                return And(exprs)
            else:
                return Or(exprs)

        error = False
        if struct.get("QoSMetric") not in self.metrics:
            self.errors.append(UndefinedLabel(struct.get("QoSMetric"), "QoSMetric"))
            error = True
        if struct.get("operator") not in Operator:
            self.errors.append(NotInEnum(struct.get("operator"), f"Operator"))
            error = True

        if error:
            return None

        return Comparison(Operator[struct.get("operator")], struct.get("value"), self.metrics[struct.get("QoSMetric")])



    def visit_QoSMetric(self, struct):
        provider = None
        if struct.get("Provider") is not None and struct.get("Provider") not in self.providers:
            self.errors.append(UndefinedLabel(struct.get("Provider"), "Provider"))
        else:
            provider = self.providers[struct.get("Provider")]

        error = False
        if struct.get("metric_type") not in QoSMetricType:
            self.errors.append(NotInEnum(struct.get("metric_type"), f"Metric Type ({struct.get("name")})"))
            error = True
        if struct.get("unit") is None:
            self.errors.append(NoUnit(f"Metric ({struct.get("name")})"))
            error = True
        elif struct.get("unit") not in QoSMetricUnit:
            self.errors.append(NotInEnum(struct.get("unit"), f"Metric Unit ({struct.get("name")})"))
            error = True

        if error:
            return None

        metric = QoSMetric(struct.get("name"), struct.get("description"),
                           QoSMetricType[struct.get("metric_type")], QoSMetricUnit[struct.get("unit")],
                           struct.get("uncertainty"), provider)
        self.metrics[struct.get("name")] = metric
        return metric



    def visit_DerivedQoSMetric(self, struct):
        provider = None
        if struct.get("Provider") is not None and struct.get("Provider") not in self.providers:
            self.errors.append(UndefinedLabel(struct.get("Provider"), "Provider"))
        else:
            provider = self.providers[struct.get("Provider")]

        error = False
        if struct.get("metric_type") not in QoSMetricType:
            self.errors.append(NotInEnum(struct.get("metric_type"), f"Metric Type ({struct.get("name")})"))
            error = True
        if struct.get("unit") is None:
            self.errors.append(NoUnit(f"Metric ({struct.get("name")})"))
            error = True
        elif struct.get("unit") not in QoSMetricUnit:
            self.errors.append(NotInEnum(struct.get("unit"), f"Metric Unit ({struct.get("name")})"))
            error = True
        if struct.get("window_unit") is None:
            self.errors.append(NoUnit(f"Window of Metric ({struct.get("name")})"))
            error = True
        elif struct.get("window_unit") not in WindowUnit:
            self.errors.append(NotInEnum(struct.get("window_unit"), f"Metric Window Unit ({struct.get("name")})"))
            error = True
        if struct.get("aggregation") not in AggregationFunction:
            self.errors.append(NotInEnum(struct.get("aggregation"), f"Aggregation Function ({struct.get("name")})"))
            error = True

        if error:
            return None

        metric = DerivedQoSMetric(struct.get("name"),
                                  struct.get("description"),
                                  QoSMetricType[struct.get("metric_type")],
                                  QoSMetricUnit[struct.get("unit")],
                                  struct.get("uncertainty"),
                                  struct.get("window"),
                                  AggregationFunction[struct.get("aggregation")],
                                  WindowUnit[struct.get("window_unit")],
                                  provider)
        self.metrics[struct.get("name")] = metric
        return metric



    def visit_QoSDriftMetric(self, struct):
        provider = None
        if struct.get("Provider") is not None and struct.get("Provider") not in self.providers:
            self.errors.append(UndefinedLabel(struct.get("Provider"), "Provider"))
        else:
            provider = self.providers[struct.get("Provider")]

        error = False
        if struct.get("metric_type") not in QoSMetricType:
            self.errors.append(NotInEnum(struct.get("metric_type"), f"Metric Type ({struct.get("name")})"))
            error = True
        if struct.get("unit") is None:
            self.errors.append(NoUnit(f"Metric ({struct.get("name")})"))
            error = True
        elif struct.get("unit") not in QoSMetricUnit:
            self.errors.append(NotInEnum(struct.get("unit"), f"Metric Unit ({struct.get("name")})"))
            error = True
        if struct.get("window_unit") is None:
            self.errors.append(NoUnit(f"Window of Metric ({struct.get("name")})"))
            error = True
        elif struct.get("window_unit") not in WindowUnit:
            self.errors.append(NotInEnum(struct.get("window_unit"), f"Metric Window Unit ({struct.get("name")})"))
            error = True
        if struct.get("aggregation") not in AggregationFunction:
            self.errors.append(NotInEnum(struct.get("aggregation"), f"Aggregation Function ({struct.get("name")})"))
            error = True

        if error:
            return None

        metric = QoSDriftMetric(struct.get("name"),
                                  struct.get("description"),
                                  QoSMetricType[struct.get("metric_type")],
                                  QoSMetricUnit[struct.get("unit")],
                                  struct.get("uncertainty"),
                                  struct.get("window"),
                                  AggregationFunction[struct.get("aggregation")],
                                  WindowUnit[struct.get("window_unit")],
                                  provider)
        self.metrics[struct.get("name")] = metric
        return metric



