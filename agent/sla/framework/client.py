import csv
import json
from collections.abc import Callable

import requests
from aenum import extend_enum

from agent.sla.framework.errors import NoValidAgentFound, NoReadyAgentFound, RefusedAgreement, AgentRefusedAgreement, \
    MetricNotAvailable
from agent.sla.framework.sla_check import UncertaintyMode
from agent.sla.lang.metamodel import SLA, Comparison, QoSMetricType
from agent.sla.lang.pretty_printer import SLAPrettyPrinter

class TaskAction:
    def __init__(self, task, agent, fn):
        self._task = task
        self._agent = agent
        self._fn = fn

class Agent:
    agent_pool = set()
    task_actions:dict[str,set[TaskAction]] = dict()

    def __init__(self, url):
        self._url = url
        self._respects_sla = True
        self._status = None
        self.update_status()
        Agent.agent_pool.add(self)

    def update_status(self):
        status_url = self._url + "/status"
        result = requests.get(status_url)
        self._status = json.loads(result.json())

    def propose(self, sla_json:str):
        agreements_url = self._url + "/agreements"
        payload = {"agreement": sla_json}
        result = requests.post(agreements_url, json=payload)
        return json.loads(result.json())

    def get_states(self, id:int):
        states_url = f"{self._url}/agreements/{id}/states"
        result = requests.get(states_url)
        return json.loads(result.json())

    def terminate(self, id:int):
        agreements_url = f"{self._url}/agreements/{id}"
        requests.delete(agreements_url)

    def task(self, task:str):
        def decorator(function):
            def wrapper(*args, **kwargs):
                sla:SLA = AgentSLA.sla
                if sla is None:
                    result = function(*args, **kwargs)
                    return result

                terms = self._tailor_sla(sla, task)
                tailored_sla = SLA(terms)
                agreement = SLAPrettyPrinter(tailored_sla).json()
                state = self.propose(agreement)
                if state["agreement_state"] == "Rejected":
                    raise AgentRefusedAgreement(self)
                result = function(*args, **kwargs)
                states = self.get_states(state["id"])
                if states["agreement_state"] not in {"Completed", "Terminated"}:
                    self.terminate(state["id"])
                if states["guarantee_state"] == "Violated":
                    self._respects_sla = False
                return result

            if task not in Agent.task_actions:
                Agent.task_actions[task] = set()
            Agent.task_actions[task].add(TaskAction(task, self, wrapper))
            return wrapper
        return decorator

    def _tailor_sla(self, sla:SLA, task):
        tailored_terms = list()
        for term in sla.guarantee_term:
            does_apply = False
            for scope in term.scope:
                for target_task in scope.tasks:
                    if target_task == task:
                        does_apply = True
                        break
            if not does_apply:
                break

            for cond in term.qualifying_condition:
                self._is_addressing_metrics(cond.boolexpression)

            for slo in term.slo:
                self._is_addressing_metrics(slo.boolexpression)

            tailored_terms.append(term)
        return tailored_terms

    def _is_addressing_metrics(self, expression):
        expressions = [expression]
        index = 0
        while index < len(expressions):
            expr = expressions[index]
            if isinstance(expr, Comparison):
                if expr.qosmetric.metric_type.value not in self._status["metrics"]:
                    raise MetricNotAvailable(self,expr.qosmetric.metric_type.value)
            else:
                expressions.extend(expr.expressions)
            index += 1

class AgentSLA:
    sla = None
    order_taskactions = lambda x: list(x)

def set_sla(sla):
    AgentSLA.sla = sla

def set_uncertainty_mode(mode:UncertaintyMode):
    for agent in Agent.agent_pool:
        uncertainty_url = agent._url + f"/uncertainty/{mode.name}"
        requests.post(uncertainty_url)

def set_agent_preference(ordering_function:Callable[[set[TaskAction]], list[TaskAction]]):
    AgentSLA.order_taskactions = ordering_function

def extend_metrics(csv_path):
    with open(csv_path, newline='') as csvfile:
        additional_metrics = csv.reader(csvfile)
        for line in additional_metrics:
            metric = line[0]
            extend_enum(QoSMetricType, metric, metric)

def executeTask(task_name, *args, **kwargs):
    task_actions = Agent.task_actions[task_name] or set()
    actions_with_respecting_agent = {action for action in task_actions if action._agent._respects_sla}
    if len(actions_with_respecting_agent) == 0:
        raise NoValidAgentFound(task_name)
    for action in actions_with_respecting_agent:
        action._agent.update_status()
    actions_with_ready_agents = {action for action in actions_with_respecting_agent if action._agent._status["state"] not in {"NotReady", "Completed"}}
    if len(actions_with_ready_agents) == 0:
        raise NoReadyAgentFound(task_name)
    sorted_actions = AgentSLA.order_taskactions(actions_with_ready_agents)
    for selected_action in sorted_actions:
        try:
            result = selected_action._fn(*args, **kwargs)
            return result
        except AgentRefusedAgreement:
            pass
        except MetricNotAvailable:
            pass
    raise RefusedAgreement(task_name)