from fastapi import FastAPI

from monitor.controllers import lifespan
from monitor.routes import router

app = FastAPI(lifespan=lifespan)

app.include_router(router)
