from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from microblog.config import settings
from microblog.database import init_db
from microblog.routes import auth, post, user

app = FastAPI(
    title="Microblog",
    version="0.0.1",
    description="A simple microblog app",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(post.router, prefix="/posts", tags=["posts"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Microblog API"}
