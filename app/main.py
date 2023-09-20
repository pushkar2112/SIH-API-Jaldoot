from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from . import models
from .database import engine
from .routers import post, user, auth
from .config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure FastAPI to serve static files from the "upload_images" directory
app.mount("/images", StaticFiles(directory="app/upload_images"), name="images")

# API Routes
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def root():                                                                    
    return {"message": "Jaldoot"}