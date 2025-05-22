#!/usr/bin/env python3

from fastapi import FastAPI
from api import GameStart, PlaceBet, PlayerDecisions, Session

app = FastAPI()
app.include_router(GameStart.router)
app.include_router(PlaceBet.router)
app.include_router(PlayerDecisions.router)
app.include_router(Session.router)
