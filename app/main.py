from fastapi import FastAPI, Depends
from sqlmodel import Session
from typing import List, Dict, Any

from app.utils import map_categories, validate_params, get_top_foods_by_category
from app.db import get_db_session

app = FastAPI()


@app.get("/top-foods/", response_model=List[Dict])
def read_top_foods(
    nutrient,
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

    validate_params(nutrient, percentage)

    category_mapping: Dict[str, List[str]] = map_categories(session, categories)

    final_result: List[Dict[str, Any]] = []

    for key, value in category_mapping.items():
        top_foods = get_top_foods_by_category(session, value, percentage, nutrient)
        final_result.append({"categorie": key, "aliments": top_foods})

    return final_result
