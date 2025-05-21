from fastapi import FastAPI
from auth.routes import auth_router
from code_rev.routes import code_router
from middleware import register_middleware 

version = 'v1'

app = FastAPI(
    title = "Code Reviewer",
    description = "A REST API for code review",
    version=version
)


register_middleware(app=app)

app.include_router(auth_router, prefix = f'/api/{version}/auth')
app.include_router(code_router, prefix = f'/api/{version}/codereview')