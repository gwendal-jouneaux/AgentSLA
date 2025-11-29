import asyncio

from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve

from agent.sla.framework.agent import AgentSLAInterface
from agent.sla.lang.metamodel import QoSMetricType


def acceptance(sla):
    return True

interface = AgentSLAInterface(["TTFT"], acceptance)
interface.start(port=19121)

app = FastAPI()
@app.get("/action")
def action():
    answer = "An action from respecting agent"
    interface.log_metric_value(QoSMetricType.TTFT,0.5)
    return answer

@app.get("/respecting")
def summary():
    answer = "Respecting agent specific task"
    interface.log_metric_value(QoSMetricType.TTFT, 0.5)
    return answer

config = Config()
config.bind = [f"127.0.0.1:8081"]
asyncio.run(serve(app, config))