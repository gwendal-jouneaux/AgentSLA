import asyncio
import json
import time
from threading import Thread

from fastapi import FastAPI, Request
from hypercorn import Config
from hypercorn.asyncio import serve

from agent.sla.framework.sla_check import check_sla
from agent.sla.lang.metamodel import QoSMetricType
from agent.sla.lang.parser import parse_file

class Measurement:
    def __init__(self, metric:QoSMetricType, value:float, client):
        self._timestamp = time.time()
        self._metric = metric
        self._value = value
        self._client = client

class Agreement:
    def __init__(self, sla, host, service_state):
        self._sla = sla
        self._host = host
        self._agreement_state = AgreementState()
        self._service_state = service_state
        self._guarantee_state = GuaranteeState()

class StateMachine:
    def __init__(self, transitions, init_state):
        self._transitions = transitions
        self._state = init_state

    def transition_to(self, new_state):
        if new_state in self._transitions[self._state]:
            self._state = new_state

    def __getattr__(self, attr):
        self.transition_to(attr)

class AgreementState(StateMachine):
    def __init__(self):
        transitions = {
            "Pending": {"PendingAndTerminating", "Observed", "Rejected"},
            "Observed": {"ObservedAndTerminating", "Completed", "Terminated"},
            "PendingAndTerminating": {"Pending", "ObservedAndTerminating", "Terminated"},
            "ObservedAndTerminating": {"Observed", "Terminated"},
            "Rejected": {},
            "Completed": {},
            "Terminated": {}
        }
        super().__init__(transitions, "NotReady")

class ServiceState(StateMachine):
    def __init__(self):
        transitions = {
            "NotReady": {"Ready", "Processing", "Idle"},
            "Ready": {"NotReady", "Processing", "Idle", "Completed"},
            "Processing": {"NotReady", "Ready", "Idle", "Completed"},
            "Idle": {"NotReady", "Processing", "Ready", "Completed"},
            "Completed": {}
        }
        super().__init__(transitions, "NotReady")

class GuaranteeState(StateMachine):
    def __init__(self):
        transitions = {
            "NotDetermined": {"Fulfilled", "Violated"},
            "Fulfilled": {"NotDetermined", "Violated"},
            "Violated": {"Fulfilled", "NotDetermined"}
        }
        super().__init__(transitions, "NotDetermined")

class AgentSLAInterface:
    _instance = None
    _needs_init = False

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_)
            class_._needs_init = True
        return class_._instance

    def __init__(self, metrics: list[QoSMetricType], agreement_acceptance):
        if not AgentSLAInterface._needs_init:
            return
        AgentSLAInterface._needs_init = False
        self.__agreement_acceptance = agreement_acceptance
        self._metrics = metrics
        self.__agreements = []
        self._measurements = { metric:[] for metric in metrics }
        self._service_state = ServiceState()
        self.app = FastAPI()
        app = self.app


        @app.get("/status")
        def get_status():
            status = {
                "state": self._service_state._state,
                "metrics": self._metrics
            }
            return json.dumps(status)

        @app.post("/agreements")
        def create_agreement(json_sla, request: Request):
            sla = parse_file(json_sla)
            accept = self.__agreement_acceptance(sla)
            if not accept:
                return {
                    "agreement_state": "Rejected"
                }

            agreement = Agreement(sla, request.client.host, self._service_state)
            agreement._agreement_state.Observed
            self.__agreements.append(agreement)
            return {
                "id": len(self.__agreements) - 1,
                "agreement_state": agreement._agreement_state._state,
                "service_state": agreement._service_state._state,
                "guarantee_state": agreement._guarantee_state._state
            }

        @app.get("/agreements/{id}/states")
        def get_states(id:int):
            agreement = self.__agreements[id]
            out = {
                "agreement_state": agreement._agreement_state._state,
                "service_state": agreement._service_state._state,
                "guarantee_state": agreement._guarantee_state._state
            }
            return json.dumps(out)

        @app.delete("/agreements/{id}")
        def terminate_agreement(self, id:int):
            agreement = self.__agreements[id]
            agreement._agreement_state.Terminated

        self._service_state.Ready

    def log_metric_value(self, metric, value):
        self._measurements[metric].append(Measurement(metric, value, None))
        self.check_agreements()

    def check_agreements(self):
        for agreement in self.__agreements:
            if agreement._agreement_state._state != "Observed":
                continue
            sla = agreement._sla
            check_sla(sla, self._measurements)

    def start(self, port:int = 19121):
        # Run new loop in thread
        loop = asyncio.new_event_loop()
        def start_thread_loop(loop):
            asyncio.set_event_loop(loop)
            # loop.run_forever()
            config = Config()
            config.bind = [f"127.0.0.1:{port}"]
            loop.run_until_complete(serve(self.app, config, shutdown_trigger=lambda: asyncio.Future()))
        t = Thread(target=start_thread_loop, args=[loop])
        t.start()