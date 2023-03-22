import os
import uvicorn

from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World", "status": "FAILURE"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=os.environ.get('APP_TCP_PORT', 3000),
        log_level=os.environ.get('APP_LOG_LEVEL', 'info'),
    )
