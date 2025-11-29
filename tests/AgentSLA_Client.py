import requests

from agent.sla.framework.client import Agent, executeTask, set_uncertainty_mode, set_sla
from agent.sla.framework.sla_check import UncertaintyMode
from agent.sla.lang.parser import parse_file

respecting_agent = Agent("http://127.0.0.1:19121")
violating_agent = Agent("http://127.0.0.1:19122")
uncertain_agent = Agent("http://127.0.0.1:19123")

set_sla(parse_file("./tests/test_sla.json"))

respecting_agent_url = "http://127.0.0.1:8081"
violating_agent_url = "http://127.0.0.1:8084"
uncertain_agent_url = "http://127.0.0.1:8083"

action_log:list[str] = []

@respecting_agent.task("action")
def action1():
    url = f"{respecting_agent_url}/action"
    response = requests.get(url)
    action_log.append("Result: " + response.text)

@violating_agent.task("action")
def action2():
    url = f"{violating_agent_url}/action"
    response = requests.get(url)
    action_log.append("Result: " + response.text)

@uncertain_agent.task("action")
def action3():
    url = f"{uncertain_agent_url}/action"
    response = requests.get(url)
    action_log.append("Result: " + response.text)

@respecting_agent.task("respecting")
def respecting():
    url = f"{respecting_agent_url}/respecting"
    response = requests.get(url)
    action_log.append("Result: " + response.text)

@violating_agent.task("violating")
def violating():
    url = f"{violating_agent_url}/violating"
    response = requests.get(url)
    action_log.append("Result: " + response.text)

@uncertain_agent.task("uncertain")
def uncertain():
    url = f"{uncertain_agent_url}/uncertain"
    response = requests.get(url)
    action_log.append("Result: " + response.text)






print("#########################################################")
print("               TESTING PROCEDURE RESULT                  ")
print("#########################################################")
print()



# Default uncertainty mode
print("Test agents in default uncertainty mode")

executeTask("respecting")
assert respecting_agent._respects_sla
executeTask("respecting")
print("\t Respecting agent: \tOK")

executeTask("violating")
assert not violating_agent._respects_sla
fails_after = False
try:
    executeTask("violating")
except:
    fails_after = True
assert fails_after
print("\t Violating agent: \tOK")

executeTask("uncertain")
executeTask("uncertain")
assert uncertain_agent._respects_sla
print("\t Uncertain agent: \tOK")



# Strict uncertainty mode
set_uncertainty_mode(UncertaintyMode.STRICT)
# reset respect state for previous failing agents
violating_agent._respects_sla = True

print("Test agents in strict uncertainty mode")

executeTask("respecting")
assert respecting_agent._respects_sla
executeTask("respecting")
print("\t Respecting agent: \tOK")

executeTask("violating")
assert not violating_agent._respects_sla
fails_after = False
try:
    executeTask("violating")
except:
    fails_after = True
assert fails_after
print("\t Violating agent: \tOK")

executeTask("uncertain")
assert not uncertain_agent._respects_sla
fails_after = False
try:
    executeTask("uncertain")
except:
    fails_after = True
assert fails_after
print("\t Uncertain agent: \tOK")


# Relaxed uncertainty mode
set_uncertainty_mode(UncertaintyMode.RELAXED)
# reset respect state for previous failing agents
violating_agent._respects_sla = True
uncertain_agent._respects_sla = True

print("Test agents in relaxed uncertainty mode")

executeTask("respecting")
assert respecting_agent._respects_sla
executeTask("respecting")
print("\t Respecting agent: \tOK")

executeTask("violating")
assert not violating_agent._respects_sla
fails_after = False
try:
    executeTask("violating")
except:
    fails_after = True
assert fails_after
print("\t Violating agent: \tOK")

executeTask("uncertain")
executeTask("uncertain")
assert uncertain_agent._respects_sla
print("\t Uncertain agent: \tOK")

print()
print()
print("#########################################################")
print("                    FINAL TASK LOG                       ")
print("#########################################################")
print("\n".join(action_log))