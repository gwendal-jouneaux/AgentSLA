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
    answer = "An action from agent 3"
    print(answer)
    return answer

@app.get("/generate")
def generate():
    answer = "A generation from agent 3"
    print(answer)
    return answer

config = Config()
config.bind = [f"127.0.0.1:8083"]
asyncio.run(serve(app, config))