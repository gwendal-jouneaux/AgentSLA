import asyncio

from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve
# from starlette.requests import Request

from agent.sla.framework.agent import AgentSLAInterface

def acceptance(sla):
    return True

interface = AgentSLAInterface(["AUC", "TTFT"], acceptance)
interface.start()

app = FastAPI()
@app.get("/action")
def action():
    # host = request.client.host
    answer = "An action from agent 1"
    print(answer)
    return answer

@app.get("/summarize")
def summary():
    # host = request.client.host
    answer = "A summary from agent 1"
    print(answer)
    return answer

config = Config()
config.bind = [f"127.0.0.1:8081"]
asyncio.run(serve(app, config))