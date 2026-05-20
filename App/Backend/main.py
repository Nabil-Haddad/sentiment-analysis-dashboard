from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.base import Base
from db.session import engine
from db.seed import seed_temp_user, seed_aspects
from routers.analysis import router
from routers.aspects import AspectRouter
from models.user import UserDB
from models.analysis import AnalysisDB, AspectAnalysisDB, WithoutAspectAnalysisDB
from models.aspect import AspectDB
from services.inference import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_temp_user()
    seed_aspects()
    print("Loading model...")
    load_model()
    print("Model ready.")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(AspectRouter)


@app.get("/")
def index():
    return {"message": "Hello There !!!!"}