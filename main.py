#!/usr/bin/env python3

from fastapi import FastAPI
from api import GameStart, PlaceBet, Session
from services.ServerLogger import ServerLogger

ServerLogger.debug("test1")

app = FastAPI()
app.include_router(PlaceBet.router)
app.include_router(Session.router)
app.include_router(GameStart.router)
