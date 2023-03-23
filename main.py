import os
import uvicorn
import functions

import data

from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World", "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}


@app.get("/hosts")
async def read_param():
    return data.hosts


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
