from fastapi import FastAPI
from auth.routes import auth_router

version = 'v1'

app = FastAPI()


app.include_router(auth_router, prefix = f'/api/{version}/auth')