#!/usr/bin/env python3

from fastapi import FastAPI
from api import GameRoutes, SessionRoutes

app = FastAPI()
app.include_router(GameRoutes.router)
app.include_router(SessionRoutes.router)
