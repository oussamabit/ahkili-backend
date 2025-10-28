from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, posts, comments, communities, reactions,admin , upload,verification ,comment_reactions , notification

import os

app = FastAPI(title="Ahkili API", version="1.0.0")

# Get allowed origins from environment or use defaults
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"
).split(",")

# Add your Vercel domain once deployed
# Example: ALLOWED_ORIGINS.append("https://ahkili.vercel.app")

# CORS - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(communities.router)
app.include_router(reactions.router)
app.include_router(admin.router)
app.include_router(upload.router)
app.include_router(verification.router)
app.include_router(comment_reactions.router)
app.include_router(notification.router)




@app.get("/")
def read_root():
    return {
        "message": "Welcome to Ahkili API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}