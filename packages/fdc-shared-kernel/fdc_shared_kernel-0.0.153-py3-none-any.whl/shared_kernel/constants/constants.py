def get_constant(section: str, key: str) -> str:
    if section == "mssql":
        if key == "CONNECTION_STRING":
            return "mssql+pyodbc://{}:{}@{}:{}/{}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    return ""
