import os
import uvicorn
import functions

import data

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
            'items': list(data.routes.keys()),
            'route_curr': '/',
            'route_prev': None,
            'title': 'Home',
        })


@app.get("/hosts", response_class=HTMLResponse)
async def read_hosts(request: Request):
    return templates.TemplateResponse(
        'list.html',
        {
            'request': request,
            'items': data.hosts,
            'route_curr': "hosts",
            'route_prev': '/',
            'title': 'Hosts',
        })


@app.get("/hosts/{host_id}", response_class=HTMLResponse)
async def read_host(request: Request, host_id: int):
    hosts = data.hosts
    if host_id in range(0, len(hosts)):
        host = hosts[host_id]
        return templates.TemplateResponse(
            'detail.html',
            {
                'request': request,
                'content': host,
                'route_curr': f"hosts/{host_id}",
                'route_prev': f"/hosts",
                'title': host.name,
            })
    else:
        return templates.TemplateResponse(
            'detail.html',
            {
                'request': request,
                'content': {'message': 'Host not found.', 'status_code': 404},
                'route_curr': f"hosts/{host_id}",
                'route_prev': f"/hosts",
                'title': 'Error 404',
            },
            status_code=404
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
