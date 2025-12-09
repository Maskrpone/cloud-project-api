import pandas as pd
from io import BytesIO
import requests
import re
import unicodedata
import os
from sqlalchemy import create_engine

DATASET_URL = "https://web.archive.org/web/20240423194012/https://naehrwertdaten.ch/wp-content/uploads/2023/08/Base_de_donnees_suisse_des_valeurs_nutritives.xlsx"  # web archive to have a fix URL

CONVERSION_FACTORS = {"g": 1, "mg": 0.001, "kj": 1000, "µg": 0.000001, "kcal": 1000}

USERNAME = os.environ.get("TF_VAR_admin_username")
PASSWORD = os.environ.get("TF_VAR_admin_password")
SERVER = os.environ.get("TF_VAR_sql_server_name")
DATABASE = "cloud-project-db"
DRIVER = "{ODBC Driver 18 for SQL Server}"

DRIVER_OPTIONS = (
    f"DRIVER={DRIVER};"
    f"SERVER={SERVER}.database.windows.net;"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

CONN_STR = f"mssql+pyodbc://?odbc_connect={DRIVER_OPTIONS}"
print(f"Connection String being used: {CONN_STR}")

engine = create_engine(CONN_STR)

dtype_food = {
    "id": "int",
    "nom": "str",
    "synonymes": "str",
    "categorie": "str",
    "unite_de_matrice": "str",
    "energie_kilojoules": "int64",
    "energie_calories": "int64",
    "lipides_totaux": "float64",
    "acides_gras_satures": "float64",
    "acides_gras_mono_insatures": "float64",
    "acides_gras_poly_insatures": "float64",
    "cholesterol": "int64",
    "glucides_disponibles": "float64",
    "sucres": "float64",
    "amidon": "float64",
    "fibres_alimentaires": "float64",
    "proteines": "float64",
    "sel": "float64",
    "alcool": "float64",
    "eau": "float64",
    "retinol": "int64",
    "betacarotene": "int64",
    "vitamine_b1": "float64",
    "vitamine_b2": "float64",
    "vitamine_b6": "float64",
    "vitamine_b12": "float64",
    "niacine": "float64",
    "folate": "float64",
    "acide_pantothenique": "float64",
    "vitamine_c": "float64",
    "vitamine_d": "float64",
    "vitamine_e": "float64",
    "potassium": "float64",
    "sodium": "float64",
    "chlore": "float64",
    "calcium": "float64",
    "magnesium": "float64",
    "phosphore": "float64",
    "fer": "float64",
    "iode": "float64",
    "zinc": "float64",
    "selenium": "float64",
}


def fetch_data(URL):
    try:
        response = requests.get(URL, stream=True)
        response.raise_for_status()
        data = BytesIO(response.content)
        print("Data fetched")
        df = pd.read_excel(data, engine="openpyxl", skiprows=2)
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error during download : {e}")
        return


def remove_accents(text):
    normalized_text = unicodedata.normalize("NFKD", text)
    return normalized_text.encode("ascii", "ignore").decode("utf-8")

def clean_data(df: pd.DataFrame):
    df = df.drop_duplicates()
    df = df.drop(columns=["ID V 4.0", "ID SwissFIR", "Densité", "Entrée modifiée"])
    df = df.drop(df.filter(regex=r"^Source.*").columns, axis=1)
    df = df.drop(df.filter(regex=r"^Dérivation de la valeur.*").columns, axis=1)
    df = df.drop(df.filter(regex=r"^Activité de *").columns, axis=1)

    double_parenthesis_pattern = r"\s*\([^)]+\)(?=\s*\([^)]+\))"
    df.columns = df.columns.str.replace(double_parenthesis_pattern, "", regex=True)

    df.columns = [
        col.strip()
        .replace(",", "")
        .replace(" ", "_")
        .replace("-", "_")
        .lower() 
        for col in df.columns
    ]

    df.columns = [remove_accents(col) for col in df.columns]

    return df

dtype_measures = {
        "name": "str",
        "unit": "str",
        "conversion": "float64"
}

def create_measures_table(df: pd.DataFrame):
    measures = []

    columns = df.columns
    for col in columns:
        match = re.search(r"\((.*?)\)", col)
        if match:
            measures.append(
                {
                    "name": re.sub(r"\((.*?)\)", "", col).strip("_"),
                    "unit": match.group(1),
                    "conversion": CONVERSION_FACTORS[match.group(1)],
                }
            )

    df = pd.DataFrame(measures).astype(dtype_measures)
    
    return df 

def create_food_table(df: pd.DataFrame):
    numerical_cols = [
        "energie_kilojoules",
        "energie_calories",
        "lipides_totaux",
        "acides_gras_satures",
        "acides_gras_mono_insatures",
        "acides_gras_poly_insatures",
        "cholesterol",
        "glucides_disponibles",
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
        "selenium",
    ]
    

    df.columns = [
            re.sub(r"\((.*?)\)", "", col).strip("_") 
            for col in df.columns
    ]

    df[numerical_cols] = df[numerical_cols].replace(
        ["tr.", "n.i.", ""], 0
    )  # Handle potential characters or empty values

    df[numerical_cols] = df[numerical_cols].fillna(0)  # Handle NaN

    for col in numerical_cols:
        df[col] = df[col].astype(str).str.replace("<", "", regex=False)

    df = df.astype(dtype_food)

    return df

def create_tables(df: pd.DataFrame):
    data = clean_data(df)

    measures_table = create_measures_table(data)
    food_table = create_food_table(data)

    measures_table_name = "measure_table"
    food_table_name = "food_table"

    measures_table.to_sql(measures_table_name, con=engine, if_exists="replace", index=False)
    food_table.to_sql(food_table_name, con=engine, if_exists="replace", index=False)


if __name__ == "__main__":
    df = fetch_data(DATASET_URL)
    create_tables(df)
