#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from api import ExistingDataRoutes, GameRoutes, SessionRoutes, SimRoutes

app = FastAPI()
app.include_router(ExistingDataRoutes.router)
app.include_router(GameRoutes.router)
app.include_router(SessionRoutes.router)
app.include_router(SimRoutes.router)

load_dotenv()
assert os.getenv('BJE_YIELD_EVERY_X_HANDS') is not None
