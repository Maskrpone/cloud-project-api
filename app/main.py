from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import List, Dict, Any

from app.utils import get_category_mapping
from app.models import Food
from app.db import get_db_session

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/foods/", response_model=List[Food])
def read_foods(session: Session = Depends(get_db_session)):
    statement = select(Food)
    results = session.exec(statement).all()
    return results


@app.get("/food/{item_id}", response_model=List[Food])
def read_food(item_id, session: Session = Depends(get_db_session)):
    statement = select(Food).where(Food.id == item_id)
    results = session.exec(statement).all()
    return results


@app.get("/categories/", response_model=List[str])
def read_category(session: Session = Depends(get_db_session)):
    statement = select(Food.categorie).distinct()
    results = session.exec(statement).all()
    return results


@app.get("/names/", response_model=List[str])
def read_names(session: Session = Depends(get_db_session)):
    statement = select(Food.nom).distinct()
    results = session.exec(statement).all()
    return results


@app.get("/top-foods/", response_model=List[Dict])
def read_top_foods(
    nutrient_column,
    percentage: float = 0.20,
    session: Session = Depends(get_db_session),
):
    categories = [
        "Fruits",
        "Légumes",
        "Lait",
        "Poisson",
        "Œufs",
        "Produits céréaliers",
        "Noix",
        "arômes",
        "viande",
        "petit-déjeuner",
    ]

    if not (0.0 < percentage <= 1.0):
        raise HTTPException(
            status_code=400, detail="Percentage must be between 0.0 and 1.0."
        )

    if not hasattr(Food, nutrient_column):
        raise HTTPException(
            status_code=400, detail=f"Nutrient {nutrient_column} not found."
        )

    all_categories_statement = select(Food.categorie).distinct()
    all_categories = session.exec(all_categories_statement).all()

    category_mapping: Dict[str, List[str]] = get_category_mapping(
        categories, all_categories
    )

    final_result: List[Dict[str, Any]] = []

    for key, value in category_mapping.items():
        count_statement = select(func.count()).where(Food.categorie.in_(value))
        total_count = session.exec(count_statement).one()

        limit = max(1, round(total_count * percentage))

        top_foods_statement = (
            select(Food.nom)
            .where(Food.categorie.in_(value))
            .order_by(getattr(Food, nutrient_column).desc())
            .limit(limit)
        )

        top_foods = session.exec(top_foods_statement).all()

        final_result.append(
            {"categorie": key, "aliments": top_foods}
        )

    return final_result
