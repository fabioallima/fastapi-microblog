from fastapi import FastAPI
from microblog.routes import main_router

app = FastAPI(
    title="Microblog",
    version="0.0.1",
    description="A simple microblog app",
)

@app.get('/')
async def index():
    return {"hello": "world"}


app.include_router(main_router)
