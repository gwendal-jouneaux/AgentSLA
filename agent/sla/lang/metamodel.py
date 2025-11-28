from enum import Enum

############################################
# Definition of Enumerations
############################################

class Operator(Enum):
    LESS = "LESS"
    LESSEQ = "LESSEQ"
    GREATER = "GREATER"
    GREATEREQ = "GREATEREQ"
    EQUAL = "EQUAL"

class AggregationFunction(Enum):
    MIN = "MIN"
    MAX = "MAX"
    AVG = "AVG"
    MED = "MED"

class QoSMetricType(Enum):
    Precision = "Precision"
    Recall = "Recall"
    Accuracy = "Accuracy"
    AUC = "AUC"
    F1Score = "F1Score"
    XAccuDiff = "XAccuDiff"
    PMV = "PMV"
    TrainingTime = "TrainingTime"
    PointwiseRobustness = "PointwiseRobustness"
    AdversarialFrequency = "AdversarialFrequency"
    AdversarialSeverity = "AdversarialSeverity"
    AdversarialDistance = "AdversarialDistance"
    TTFT = "TTFT"
    E2E = "E2E"
    Bias = "Bias"
    Racism = "Racism"
    Sexism = "Sexism"
    Ageism = "Ageism"
    Religious = "Religious"
    Political = "Political"
    Xenophobia = "Xenophobia"
    SHAP = "SHAP"
    LIME = "LIME"
    EnergyConsumption = "EnergyConsumption"
    WaterConsumption = "WaterConsumption"
    CarbonEmit = "CarbonEmit"
    CarbonOffset = "CarbonOffset"
    OutputSize = "OutputSize"
    MCP = "MCP"
    A2A = "A2A"
    OversightLevel = "OversightLevel"

class QoSMetricUnit(Enum):
    MILLISECONDS = "MILLISECONDS"
    SECONDS = "SECONDS"
    MINUTES = "MINUTES"
    HOURS = "HOURS"
    LITER = "LITER"
    M3 = "M3"
    Wh = "Wh"
    kWh = "kWh"
    gCO2eq = "gCO2eq"
    KgCO2eq = "KgCO2eq"
    NONE = "NONE"

class WindowUnit(Enum):
    SEC = "SEC"
    MIN = "MIN"
    HOUR = "HOUR"
    DAY = "DAY"
    MESSAGE = "MESSAGE"


############################################
# Definition of Classes
############################################

class Provider:

    def __init__(self, name:str, confidence: float, reputation: int):
        self.__confidence = confidence
        self.__name = name
        self.__reputation = reputation

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def reputation(self) -> int:
        return self.__reputation

    @reputation.setter
    def reputation(self, reputation: int):
        self.__reputation = reputation

    @property
    def confidence(self) -> float:
        return self.__confidence

    @confidence.setter
    def confidence(self, confidence: float):
        self.__confidence = confidence

# class ModelCard:
#
#     def __init__(self, name: str, model_card: str):
#         self.__name = name
#         self.__model_card = model_card
#
#     @property
#     def model_card(self) -> str:
#         return self.__model_card
#
#     @model_card.setter
#     def model_card(self, model_card: str):
#         self.__model_card = model_card
#
#     @property
#     def name(self) -> str:
#         return self.__name
#
#     @name.setter
#     def name(self, name: str):
#         self.__name = name

class QoSMetric:

    def __init__(self, name: str, description: str, metric_type: QoSMetricType, unit: QoSMetricUnit, uncertainty: float, provider: "Provider" = None):
        self.__name = name
        self.__description = description
        self.__metric_type = metric_type
        self.__unit = unit
        self.__uncertainty = uncertainty
        self.__provider = provider
        
    @property
    def uncertainty(self) -> float:
        return self.__uncertainty

    @uncertainty.setter
    def uncertainty(self, uncertainty: float):
        self.__uncertainty = uncertainty

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def metric_type(self) -> QoSMetricType:
        return self.__metric_type

    @metric_type.setter
    def metric_type(self, metric_type: QoSMetricType):
        self.__metric_type = metric_type

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, description: str):
        self.__description = description

    @property
    def unit(self) -> QoSMetricUnit:
        return self.__unit

    @unit.setter
    def unit(self, unit: QoSMetricUnit):
        self.__unit = unit

    @property
    def provider(self):
        return self.__provider

    @provider.setter
    def provider(self, value):
        self.__provider = value

class QoSDriftMetric(QoSMetric):

    def __init__(self, name: str, description: str, metric_type: QoSMetricType, unit: QoSMetricUnit, uncertainty: float, window: int, aggregation: AggregationFunction, window_unit: WindowUnit, provider: "Provider"):
        super().__init__(name, description, metric_type, unit, uncertainty, provider)
        self.__window = window
        self.__aggregation = aggregation
        self.__window_unit = window_unit
        
    @property
    def window(self) -> int:
        return self.__window

    @window.setter
    def window(self, window: int):
        self.__window = window

    @property
    def aggregation(self) -> AggregationFunction:
        return self.__aggregation

    @aggregation.setter
    def aggregation(self, aggregation: AggregationFunction):
        self.__aggregation = aggregation

    @property
    def window_unit(self) -> WindowUnit:
        return self.__window_unit

    @window_unit.setter
    def window_unit(self, window_unit: WindowUnit):
        self.__window_unit = window_unit

class DerivedQoSMetric(QoSMetric):

    def __init__(self, name: str, description: str, metric_type: QoSMetricType, unit: QoSMetricUnit, uncertainty: float, window: int, aggregation: AggregationFunction, window_unit: WindowUnit, provider: "Provider"):
        super().__init__(name, description, metric_type, unit, uncertainty, provider)
        self.__window = window
        self.__aggregation = aggregation
        self.__window_unit = window_unit
        
    @property
    def window_unit(self) -> WindowUnit:
        return self.__window_unit

    @window_unit.setter
    def window_unit(self, window_unit: WindowUnit):
        self.__window_unit = window_unit

    @property
    def aggregation(self) -> AggregationFunction:
        return self.__aggregation

    @aggregation.setter
    def aggregation(self, aggregation: AggregationFunction):
        self.__aggregation = aggregation

    @property
    def window(self) -> int:
        return self.__window

    @window.setter
    def window(self, window: int):
        self.__window = window

class BoolExpression:
    pass

class Or(BoolExpression):
    def __init__(self, expressions: list[BoolExpression]):
        self.__expressions = expressions

    @property
    def expressions(self) -> list[BoolExpression]:
        return self.__expressions

    @expressions.setter
    def expressions(self, expressions: list[BoolExpression]):
        self.__expressions = expressions

class And(BoolExpression):
    def __init__(self, expressions: list[BoolExpression]):
        self.__expressions = expressions

    @property
    def expressions(self) -> list[BoolExpression]:
        return self.__expressions

    @expressions.setter
    def expressions(self, expressions: list[BoolExpression]):
        self.__expressions = expressions

class Comparison(BoolExpression):

    def __init__(self, operator: Operator, value: float, qosmetric: "QoSMetric" = None):
        self.__operator = operator
        self.__value = value
        self.__qosmetric = qosmetric
        
    @property
    def operator(self) -> Operator:
        return self.__operator

    @operator.setter
    def operator(self, operator: Operator):
        self.__operator = operator

    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, value: float):
        self.__value = value

    @property
    def qosmetric(self):
        return self.__qosmetric

    @qosmetric.setter
    def qosmetric(self, value):
        self.__qosmetric = value


class SLO:

    def __init__(self, name: str, guaranteeterm: "GuaranteeTerm" = None, boolexpression: "BoolExpression" = None):
        self.__name = name
        self.__guaranteeterm = guaranteeterm
        self.__boolexpression = boolexpression
        
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def boolexpression(self):
        return self.__boolexpression

    @boolexpression.setter
    def boolexpression(self, value):
        self.__boolexpression = value

    @property
    def guaranteeterm(self):
        return self.__guaranteeterm

    @guaranteeterm.setter
    def guaranteeterm(self, value):
        # Bidirectional consistency
        old_value = self.__guaranteeterm
        self.__guaranteeterm = value
        
        # Remove self from old opposite end
        if old_value is not None:
            old_value.slo = [x for x in old_value.slo if x is not self]
                
        # Add self to new opposite end
        if value is not None:
            value.slo.append(self)

class QualifyingCondition:

    def __init__(self, name: str, guaranteeterm: "GuaranteeTerm" = None, boolexpression: "BoolExpression" = None):
        self.__name = name
        self.__guaranteeterm = guaranteeterm
        self.__boolexpression = boolexpression
        
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def boolexpression(self):
        return self.__boolexpression

    @boolexpression.setter
    def boolexpression(self, value):
        # Bidirectional consistency
        old_value = self.__boolexpression
        self.__boolexpression = value

        # Remove self from old opposite end
        if old_value is not None:
            old_value.qualifying_condition = [x for x in old_value.qualifying_condition if x is not self]

        # Add self to new opposite end
        if value is not None:
            value.qualifying_condition.append(self)

    @property
    def guaranteeterm(self):
        return self.__guaranteeterm

    @guaranteeterm.setter
    def guaranteeterm(self, value):
        # Bidirectional consistency
        old_value = self.__guaranteeterm
        self.__guaranteeterm = value

        # Remove self from old opposite end
        if old_value is not None:
            old_value.qualifying_condition = [x for x in old_value.qualifying_condition if x is not self]

        # Add self to new opposite end
        if value is not None:
            value.qualifying_condition.append(self)

# class Agent:
#
#     def __init__(self, description: str, url: str, name: str, modelcard: "ModelCard" = None):
#         self.__description = description
#         self.__url = url
#         self.__name = name
#         self.__modelcard = modelcard
#
#     @property
#     def description(self) -> str:
#         return self.__description
#
#     @description.setter
#     def description(self, description: str):
#         self.__description = description
#
#     @property
#     def url(self) -> str:
#         return self.__url
#
#     @url.setter
#     def url(self, url: str):
#         self.__url = url
#
#     @property
#     def name(self) -> str:
#         return self.__name
#
#     @name.setter
#     def name(self, name: str):
#         self.__name = name
#
#     @property
#     def modelcard(self):
#         return self.__modelcard
#
#     @modelcard.setter
#     def modelcard(self, value):
#         self.__modelcard = value

class Scope:

    def __init__(self, name: str, guaranteeterm: "GuaranteeTerm" = None, tasks: list[str] = []):
        self.__name = name
        self.__guaranteeterm = guaranteeterm
        self.__tasks = tasks
        
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def tasks(self):
        return self.__tasks

    @tasks.setter
    def tasks(self, value):
        self.__tasks = value

    @property
    def guaranteeterm(self):
        return self.__guaranteeterm

    @guaranteeterm.setter
    def guaranteeterm(self, value):
        # Bidirectional consistency
        old_value = self.__guaranteeterm
        self.__guaranteeterm = value

        # Remove self from old opposite end
        if old_value is not None:
            old_value.scope = [x for x in old_value.scope if x is not self]

        # Add self to new opposite end
        if value is not None:
            value.scope.append(self)

class GuaranteeTerm:
    def __init__(self, slo: list[SLO], qualifying_condition: list[QualifyingCondition], scope: list[Scope]):
        self.__slo = slo
        self.__qualifying_condition = qualifying_condition
        self.__scope = scope

    @property
    def slo(self) -> list[SLO]:
        return self.__slo

    @slo.setter
    def slo(self, slo: list[SLO]):
        self.__slo = slo

    @property
    def qualifying_condition(self) -> list[QualifyingCondition]:
        return self.__qualifying_condition

    @qualifying_condition.setter
    def qualifying_condition(self, qualifying_condition: list[QualifyingCondition]):
        self.__qualifying_condition = qualifying_condition

    @property
    def scope(self) -> list[Scope]:
        return self.__scope

    @scope.setter
    def scope(self, scope: list[Scope]):
        self.__scope = scope

class SLA:

    def __init__(self, guarantee_term: list[GuaranteeTerm]):
        self.__guarantee_term = guarantee_term

    @property
    def guarantee_term(self) -> list[GuaranteeTerm]:
        return self.__guarantee_term

    @guarantee_term.setter
    def guarantee_term(self, guarantee_term: list[GuaranteeTerm]):
        self.__guarantee_term = guarantee_term