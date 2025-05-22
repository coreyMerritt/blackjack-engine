#!/usr/bin/env python3

from fastapi import FastAPI
from api import GameStart, PlaceBet, Session

app = FastAPI()
app.include_router(PlaceBet.router)
app.include_router(Session.router)
app.include_router(GameStart.router)
