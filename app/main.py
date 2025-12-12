from fastapi import FastAPI, Depends
from sqlmodel import Session
from typing import List, Dict, Any

from app.utils import (
    map_categories,
    validate_params,
    get_top_foods_by_category,
    validate_phase,
    get_top_food_by_abs_nutrient,
)
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


phases = {
    "menstruelle": [
        ("fer", []),
        ("vitamine_c", ["Fruits", "Légumes"]),
        ("magnesium", []),
        ("acide_alpha_linolenique", ["Poissons"]),
    ],
    "folliculaire": [
        ("proteines", []),
        ("*", ["Légumes"]),
        ("glucides_disponibles", ["flocons et céréales"]),
    ],
    "ovulatoire": [
        ("zinc", ["Fruits de mer", "Viande"]),
        ("fibres_alimentaires", []),
        ("vitamine_c", []),
        ("selenium", []),
        ("zinc", []),
    ],
    "luteale": [("vitamine_b", []), ("magnesium", [])],
}


@app.get("/food-by-phase/", response_model=List[Dict])
def read_food_by_phase(
    phase: str, percentage: float = 0.1, session: Session = Depends(get_db_session)
):
    validate_phase(phase, phases.keys())

    nutrients_array = phases[phase]
    top_food = {}
    for nutrient in nutrients_array:
        name, _ = (
            nutrient  # The _ stands for a specific category (not in use right now)
        )
        top_food[name] = get_top_food_by_abs_nutrient(name, percentage, session)

    return [top_food]
