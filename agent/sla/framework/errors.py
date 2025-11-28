class SLAFrameworkException(Exception):
    pass

class NoValidAgentFound(SLAFrameworkException):
    def __init__(self, task):
        self._task = task

    def __str__(self):
        return f"No agents respecting AgentSLA found for task: {self._task}"

class NoReadyAgentFound(SLAFrameworkException):
    def __init__(self, task):
        self._task = task

    def __str__(self):
        return f"No agents are ready for task: {self._task}"

class MetricNotAvailable(SLAFrameworkException):
    def __init__(self, agent, metric):
        self._agent = agent
        self._metric = metric

    def __str__(self):
        return f"Metric '{self._metric}' is not available on agent '{self._agent}'"

class AgentRefusedAgreement(SLAFrameworkException):
    def __init__(self, agent):
        self._agent = agent

    def __str__(self):
        return f"Agent {self._agent} refused the agreement"

class RefusedAgreement(SLAFrameworkException):
    def __init__(self, task):
        self._task = task

    def __str__(self):
        return f"All available agents refused the agreement for task: {self._task}"