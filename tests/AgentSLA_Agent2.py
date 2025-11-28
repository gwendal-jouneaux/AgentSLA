import asyncio

from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve

from agent.sla.framework.agent import AgentSLAInterface

def acceptance(sla):
    return True

interface = AgentSLAInterface(["AUC", "TTFT"], acceptance)
interface.start()

app = FastAPI()
@app.get("/action")
def action():
    answer = "An action from agent 2"
    print(answer)
    return answer

@app.get("/classify")
def classify():
    answer = "A classification from agent 2"
    print(answer)
    return answer

config = Config()
config.bind = [f"127.0.0.1:8084"]
asyncio.run(serve(app, config))