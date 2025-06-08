from fastapi import FastAPI
from microblog.routes import main_router
from microblog.database import init_db

app = FastAPI(
    title="Microblog",
    version="0.0.1",
    description="A simple microblog app",
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get('/')
async def index():
    return {"hello": "world"}


app.include_router(main_router)
