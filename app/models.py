from sqlmodel import Field, SQLModel
from typing import Optional


class Food(SQLModel, table=True):
    __tablename__ = "food_table"
    __table_args__ = {"schema": "dbo"}

    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str
    synonymes: str = None
    categorie: str
    unite_de_matrice: str
    energie_kilojoules: Optional[int]
    energie_calories: Optional[int]
    lipides_totaux: Optional[float]
    acides_gras_satures: Optional[float]
    acides_gras_mono_insatures: Optional[float]
    acides_gras_poly_insatures: Optional[float]
    acide_linoleique: Optional[float]
    acide_alpha_linolenique: Optional[float]
    cholesterol: Optional[int]
    glucides_disponibles: Optional[float]
    sucres: Optional[float]
    amidon: Optional[float]
    fibres_alimentaires: Optional[float]
    proteines: Optional[float]
    sel: Optional[float]
    alcool: Optional[float]
    eau: Optional[float]
    retinol: Optional[int]
    betacarotene: Optional[float]
    vitamine_b1: Optional[float]
    vitamine_b2: Optional[float]
    vitamine_b6: Optional[float]
    vitamine_b12: Optional[float]
    niacine: Optional[float]
    folate: Optional[float]
    acide_pantothenique: Optional[float]
    vitamine_c: Optional[float]
    vitamine_d: Optional[float]
    vitamine_e: Optional[float]
    potassium: Optional[float]
    sodium: Optional[float]
    chlore: Optional[float]
    calcium: Optional[float]
    magnesium: Optional[float]
    phosphore: Optional[float]
    fer: Optional[float]
    iode: Optional[float]
    zinc: Optional[float]
    selenium: Optional[float]
