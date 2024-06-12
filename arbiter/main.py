from agent import Agent
from fastapi import FastAPI


app = FastAPI()


@app.get('/status/arbiter')
def status_arbiter():
    return {"Arbiter alive": True}


@app.get('/status/master')
def status_master():
    if agent.connect_master():
        return {"Master alive": True}
    else:
        return {"Master alive": False}

agent = Agent()

agent.init_connections()
