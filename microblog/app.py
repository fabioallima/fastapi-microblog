from fastapi import FastAPI

app = FastAPI(
    title="Microblog",
    version="0.0.1",
    description="A simple microblog app",
)

@app.get('/')
async def index():
    return {"hello": "world"}