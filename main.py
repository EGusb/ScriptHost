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
    return templates.TemplateResponse('home.html', {'request': request})


@app.get("/{route}", response_class=HTMLResponse)
async def read_hosts(request: Request, route: str):
    if route in data.routes:
        return templates.TemplateResponse(
            'list.html',
            {
                'request': request,
                'items': data.routes[route],
                'title': route.capitalize(),
            })
    else:
        return RedirectResponse('/', status_code=303)


@app.get("/{route}/{index}", response_class=HTMLResponse)
async def read_host(request: Request, route: str, index: int):
    host = data.hosts[index] if index in range(0, len(data.hosts)) else {'error': 'Host not found.'}
    return templates.TemplateResponse(
        'detail.html',
        {
            'request': request,
            'content': host,
            'title': host.name if 'name' in dict(host) else 'Error',
        })


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
