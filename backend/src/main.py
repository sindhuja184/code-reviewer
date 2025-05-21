from fastapi import FastAPI
from auth.routes import auth_router
from code_rev.routes import code_router
version = 'v1'

app = FastAPI()


app.include_router(auth_router, prefix = f'/api/{version}/auth')
app.include_router(code_router, prefix = f'/api/{version}/codereview')