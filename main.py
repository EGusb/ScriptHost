import os
import uvicorn

from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World", "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}


@app.get("/{param}")
async def read_param(param: str):
    return {"parameter": param, "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.environ.get('APP_HOST', 'localhost'),
        port=int(os.environ.get('APP_TCP_PORT', 3000)),
        log_level=os.environ.get('APP_LOG_LEVEL', 'info'),
        reload=os.environ.get('APP_AUTO_RELOAD', 'True') == 'True',
    )
