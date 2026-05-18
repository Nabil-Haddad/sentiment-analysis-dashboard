from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.base import Base
from db.session import engine
from db.seed import seed_temp_user
from routers.analysis import router
from models.user import UserDB
from models.analysis import AnalysisDB, AspectAnalysisDB, WithoutAspectAnalysisDB
from services.inference import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create the database
    Base.metadata.create_all(bind=engine)
    # create the emp_user
    seed_temp_user()
    print("Loading model...")
    # load the model
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


@app.get("/")
def index():
    return {"message": "Hello There !!!!"}