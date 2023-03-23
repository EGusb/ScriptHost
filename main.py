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


@app.get("/{route}", response_class=HTMLResponse)
async def read_hosts(request: Request, route: str):
    if route in data.routes:
        return templates.TemplateResponse(
            'list.html',
            {
                'request': request,
                'items': data.routes[route],
                'route_curr': route,
                'route_prev': '/',
                'title': route.capitalize(),
            })
    else:
        return RedirectResponse('/', status_code=303)


@app.get("/{route}/{index}", response_class=HTMLResponse)
async def read_host(request: Request, route: str, index: int):
    if route in data.routes:
        items = data.routes[route]
        item = dict(items[index]) if index in range(0, len(items)) else {'error': 'Item not found.'}
        return templates.TemplateResponse(
            'detail.html',
            {
                'request': request,
                'content': item,
                'route_curr': f"{route}/{index}",
                'route_prev': f"/{route}",
                'title': item['name'] if 'name' in dict(item) else 'Error',
            })
    else:
        return RedirectResponse('/', status_code=303)


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
