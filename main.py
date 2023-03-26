import functions
import models
import os
import uvicorn
import sqlmodel

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List

load_dotenv()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        'home.html',
        {
            'request': request,
            'items': ['hosts', 'tests'],
            'route_curr': '/',
            'route_prev': None,
            'title': 'Home',
        })


@app.get("/hosts", response_model=List[models.Host])  # response_class=HTMLResponse)
async def get_hosts():
    with sqlmodel.Session(models.engine) as session:
        heroes = session.exec(sqlmodel.select(models.Host)).all()
        return heroes


@app.get("/hosts/{host_id}", response_model=models.Host)
async def get_host(host_id: int):
    with sqlmodel.Session(models.engine) as session:
        host = session.get(models.Host, host_id)
        return host if host else []


@app.get("/ping/{ip_addr}")
async def ping_host(ip_addr: str, amount: int = 3):
    if functions.is_ipv4_address(ip_addr) or functions.is_ipv6_address(ip_addr):
        host = {
            'host': ip_addr,
            'pings': [],
        }
        for i in range(0, amount):
            res = await functions.ping_host(ip_addr)
            host['pings'].append({False: 'error', None: 'timeout'}.get(res, res))
        return host
    else:
        return {'error': 'invalid IP address.'}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.environ.get('APP_HOST', 'localhost'),
        port=int(os.environ.get('APP_TCP_PORT', 3000)),
        log_level=os.environ.get('APP_LOG_LEVEL', 'info'),
        reload=os.environ.get('APP_AUTO_RELOAD', 'True') == 'True',
    )
