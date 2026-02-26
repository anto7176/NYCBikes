#
#   Imports
#

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Perso

from api.router import router

#
#   Script
#

app = FastAPI()

#
#   Middlewares
#

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#
#   Routes
#

app.include_router(router)