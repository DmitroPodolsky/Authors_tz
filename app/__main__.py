import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.auth.routers import auth_router
from app.author.routers import user_router
from app.category.routers import category_router
from app.config import settings
from app.db.auto_migrate import migrate
from app.post.routers import post_router

app = FastAPI(title="waifu")

app.mount("/static", StaticFiles(directory=settings.STATIC_PATH), name="static")
app.include_router(auth_router)
app.include_router(user_router)

app.include_router(post_router)
app.include_router(category_router)

if __name__ == "__main__":
    migrate()
    uvicorn.run(app, host=settings.HOST, port=8000)
