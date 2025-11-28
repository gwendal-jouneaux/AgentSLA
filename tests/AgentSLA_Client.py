import requests

from agent.sla.framework.client import Agent, executeTask

agent1 = Agent("http://127.0.0.1:19121")
agent2 = Agent("http://127.0.0.1:19122")
agent3 = Agent("http://127.0.0.1:19123")

agent1_url = "http://127.0.0.1:8081"
agent2_url = "http://127.0.0.1:8084"
agent3_url = "http://127.0.0.1:8083"

@agent1.task("action")
def action1():
    url = f"{agent1_url}/action"
    response = requests.get(url)
    print("Result: " + response.text)

@agent2.task("action")
def action2():
    url = f"{agent2_url}/action"
    response = requests.get(url)
    print("Result: " + response.text)

@agent3.task("action")
def action3():
    url = f"{agent3_url}/action"
    response = requests.get(url)
    print("Result: " + response.text)

@agent1.task("summarize")
def summarize():
    url = f"{agent1_url}/summarize"
    response = requests.get(url)
    print("Result: " + response.text)

@agent2.task("classify")
def classify():
    url = f"{agent2_url}/classify"
    response = requests.get(url)
    print("Result: " + response.text)

@agent3.task("generate")
def generate():
    url = f"{agent3_url}/generate"
    response = requests.get(url)
    print("Result: " + response.text)


executeTask("action")
executeTask("summarize")
executeTask("classify")
executeTask("generate")
executeTask("action")