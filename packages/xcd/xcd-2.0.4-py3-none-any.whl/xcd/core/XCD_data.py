import pandas as pd
from django.conf import settings
from django.db import connection
import os

def load_quant_data(mode="file", source=None):
    """
    Načte kvantifikační data buď z CSV/XLS (offline) nebo z databáze (Django).
    - mode="file" → načte pandas DataFrame ze souboru
    - mode="db" → dotaz do databáze přes Django ORM nebo raw SQL
    """
    if mode == "file":
        if not source:
            return pd.DataFrame()
        df = pd.read_csv(source) if source.endswith(".csv") else pd.read_excel(source)
        return df

    elif mode == "db":
        query = "SELECT sample_name, human, male, DI_A, DI_Y, A_Y FROM quant_table"
        return pd.read_sql_query(query, connection)

    else:
        raise ValueError("Unknown data mode")