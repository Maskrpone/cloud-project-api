import os
from sqlalchemy import create_engine

USERNAME = os.environ.get("admin_username")
PASSWORD = os.environ.get("admin_password")
SERVER = os.environ.get("sql_server_name")
DATABASE = "cloud-project-db"
DRIVER = "{ODBC Driver 18 for SQL Server}"

DRIVER_OPTIONS = (
    f"DRIVER={DRIVER};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

CONN_STR = f"mssql+pyodbc://?odbc_connect={DRIVER_OPTIONS}"

print(CONN_STR)

engine = create_engine(CONN_STR, echo=True)


def get_db_session():
    from sqlmodel import Session

    with Session(engine) as session:
        yield session
