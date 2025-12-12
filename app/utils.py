from fastapi import HTTPException
from bs4 import BeautifulSoup
from app.models import Food
from sqlmodel import Session, select, func
from typing import List, Dict
import requests
import datetime


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


def validate_phase(phase, phases):
    if phase not in phases:
        raise HTTPException(
            status_code=400,
            detail="Phase must be 'menstruelle', 'folliculaire', 'ovulatoire' or 'luteal'",
        )


# def get_top_food_by_nutrient(params: tuple[str, list[str]], percentage: float, session: Session) -> list[str]:
#     nutrient, category_keywords = params
#
#     if category_keywords:
#
#         for key in category_keywords:


def get_top_food_by_abs_nutrient(
    nutrient: str,
    percentage: float,
    session: Session,
    mois: int = datetime.date.today().month,
) -> list[str]:
    if not hasattr(Food, nutrient):
        return None

    order_by_clause = getattr(Food, nutrient).desc()
    # list_food_statement = select(Food.name).order_by(order_by_clause).limit()

    count_statement = select(func.count(getattr(Food, nutrient)))
    total_count = session.exec(count_statement).one()

    top_limit = max(1, round(total_count * percentage))

    # SELECT * FROM food_table ORDER BY nutrient DESC LIMIT top_limit
    statement = select(Food).order_by(order_by_clause).limit(top_limit)
    results = session.exec(statement).all()

    return results


SEASON_URL = "https://www.greenpeace.fr/guetteur/calendrier/"


def get_seasoned_food(mois: int):
    mois_mot = [
        "janvier",
        "fevrier",
        "mars",
        "avril",
        "mai",
        "juin",
        "juillet",
        "aout",
        "septembre",
        "octobre",
        "novembre",
        "decembre",
    ]
    mois_a_chercher = mois_mot[mois - 1]
    categories = [f"{mois_a_chercher}-legumes", f"{mois_a_chercher}-fruits"]
    print(f"Categories: {categories}")

    response = requests.get(SEASON_URL)
    if response.status_code == 200:
        response.encoding = "utf-8"
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        result = {}
        for cat in categories:
            a_balise = soup.find("a", id=cat)
            if a_balise:
                article_balise = a_balise.find_next_sibling("article")
                if article_balise:
                    li_tags = article_balise.find_all("li")
                    result[cat.split("-")[1]] = [
                        li.get_text(strip=True) for li in li_tags
                    ]
        print(result)
        return result
    else:
        print("Error in connexion")
        return
