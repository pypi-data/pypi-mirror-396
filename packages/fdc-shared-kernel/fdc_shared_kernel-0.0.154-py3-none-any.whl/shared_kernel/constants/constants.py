def get_constant(section: str, key: str) -> str:
    if section == "mssql":
        if key == "CONNECTION_STRING":
            return "mssql+pyodbc://{}:{}@{}:{}/{}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    elif section == "postgres":
        if key == "CONNECTION_STRING":
            return "postgresql+psycopg2://{}:{}@{}:{}/{}"
    return ""
