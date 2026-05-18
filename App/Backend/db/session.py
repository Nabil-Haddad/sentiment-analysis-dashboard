from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL ,
    connect_args = {"check_same_thread" : False}
)


SessionLocal = sessionmaker(bind = engine , autocommit = False , autoflush= False)
