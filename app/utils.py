from fastapi import HTTPException
from app.models import Food
from sqlmodel import Session, select, func
from typing import List, Dict


def valid_category(category: str, keyword: str) -> bool:
    """
    Utility to filter out some useless categories
    """
    forbidden_keywords = ["boissons", "sucreries", "bonbons"]

    for word in forbidden_keywords:
        if word in category.lower():
            return False

    if keyword == "Fruits" and "fruits de mer" in category.lower():
        return False

    return True


def map_categories(session: Session, categories: List[str]) -> Dict[str, List[str]]:
    all_categories_statement = select(Food.categorie).distinct()
    all_categories = session.exec(all_categories_statement).all()

    category_mapping = {}
    for keyword in categories:
        category_mapping[keyword] = [
            category
            for category in all_categories
            if keyword.lower() in category.lower() and valid_category(category, keyword)
        ]

    return category_mapping


def validate_params(nutrient, percentage) -> None:
    if not (0.0 < percentage <= 1.0):
        raise HTTPException(
            status_code=400, detail="Percentage must be between 0.0 and 1.0."
        )

    if not hasattr(Food, nutrient):
        raise HTTPException(status_code=400, detail=f"Nutrient {nutrient} not found.")


def get_top_foods_by_category(
        session: Session, category: str, percentage: float, nutrient: str
):
    count_statement = select(func.count()).where(Food.categorie.in_(category))
    total_count = session.exec(count_statement).one()

    limit = max(1, round(total_count * percentage))

    top_food_statement = (
        select(Food.nom)
        .where(Food.categorie.in_(category))
        .order_by(getattr(Food, nutrient).desc())
        .limit(limit)
    )

    top_food = session.exec(top_food_statement).all()

    return top_food
