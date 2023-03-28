import functions
import models
import os
import uvicorn
import sqlmodel

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

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


@app.get("/hosts")
async def get_hosts():
    with sqlmodel.Session(models.engine) as session:
        heroes = session.exec(sqlmodel.select(models.Host)).all()
        return heroes


@app.post("/hosts")
async def create_host(hosts: List[models.Host]):
    with sqlmodel.Session(models.engine) as session:
        try:
            for host in hosts:
                session.add(host)

            session.commit()

            for host in hosts:
                session.refresh(host)

            return hosts

        except IntegrityError as e:
            return JSONResponse(
                status_code=409,
                content={
                    'error': f"{type(e).__name__}: " + str(e).replace('\n', ' '),
                    'status_code': 409
                }
            )


@app.delete("/hosts")
async def delete_hosts():
    with sqlmodel.Session(models.engine) as session:
        try:
            deleted_hosts = []
            hosts = session.exec(sqlmodel.select(models.Host))
            for host in hosts:
                deleted_hosts.append(host.dict())
                session.delete(host)

            session.commit()
            return deleted_hosts

        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={
                    'error': f"{type(e).__name__}: " + str(e).replace('\n', ' '),
                    'status_code': 400
                }
            )


@app.get("/hosts/{host_id}")
async def get_host(host_id: int):
    with sqlmodel.Session(models.engine) as session:
        host = session.get(models.Host, host_id)
        return host if host else []


@app.delete("/hosts/{host_id}")
async def delete_host(host_id: int):
    with sqlmodel.Session(models.engine) as session:
        try:
            host = session.get(models.Host, host_id)
            if host:
                session.delete(host)
                session.commit()
                return host
            else:
                return JSONResponse(
                    status_code=404,
                    content={
                        'error': 'Host not found.',
                        'status_code': 404
                    }
                )

        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={
                    'error': f"{type(e).__name__}: " + str(e).replace('\n', ' '),
                    'status_code': 400
                }
            )


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
