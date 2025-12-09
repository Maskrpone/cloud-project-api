from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from typing import List

from app.models import Food
from app.db import get_db_session

app = FastAPI()

# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)
#
# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/foods/", response_model=List[Food])
def read_foods(session: Session = Depends(get_db_session)):
    statement = select(Food)
    results = session.exec(statement).all()
    return results
