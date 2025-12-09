from sqlmodel import Field, SQLModel
from typing import Optional 

class Food(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    synonymes: str = None
    categorie: str
    unite_de_matrice: str
    energie_kilojoules: Optional[int]
    energie_calories: Optional[int]
    lipides_totaux: Optional[float]
    acides_gras_satures: Optional[float]
    acides_gras_mono-insatures: 
    "acides_gras_poly-insatures",
    "cholesterol","glucides_disponibles",
    "sucres",
    "amidon",
    "fibres_alimentaires",
    "proteines",
    "sel",
    "alcool",
    "eau",
    "retinol",
    "betacarotene",
    "vitamine_b1",
    "vitamine_b2",
    "vitamine_b6",
    "vitamine_b12",
    "niacine",
    "folate",
    "acide_pantothenique",
    "vitamine_c",
    "vitamine_d",
    "vitamine_e",
    "potassium",
    "sodium",
    "chlore",
    "calcium",
    "magnesium",
    "phosphore",
    "fer",
    "iode",
    "zinc",
    "selenium"
