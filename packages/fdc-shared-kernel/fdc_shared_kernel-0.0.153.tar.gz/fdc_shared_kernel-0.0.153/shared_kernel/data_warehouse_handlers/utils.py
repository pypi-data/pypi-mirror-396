import base64
from datetime import date, datetime, time
from decimal import Decimal
from redshift_connector.utils.oids import get_datatype_name
from sqlalchemy.engine import Row


def get_column_info(row_desc):
    return [
        {
            "name": col["label"].decode("utf-8"),
            "type": get_datatype_name(col["type_oid"]).lower()
        }
        for col in row_desc
    ]


def extract_error_message(error) -> str:
    """
    Extracts the 'M' (message) field from a Redshift/PostgreSQL-style error dict.
    If format is unexpected or 'M' not found, returns the input stringified.
    """
    try:
        # If already a dict (like boto3 Redshift response), extract 'M'
        if isinstance(error, dict):
            return error.get("M", str(error))
        
        # If it's a string that looks like a dict, try to parse it
        if isinstance(error, str) and error.strip().startswith("{"):
            import ast
            error_dict = ast.literal_eval(error)
            if isinstance(error_dict, dict) and "M" in error_dict:
                return error_dict["M"]
        
        return str(error)
    except Exception:
        return str(error)
    

def extract_snowflake_error_message(error) -> str:
    """
    Creates user friendly error messages for Snowflake errors.
    """
    try:
        if isinstance(error, str):
            if "250001" in error:
                message = "Please verify the provided credentials."
                return message
            elif "250003" in error:
                message = "Please ensure the specified Snowflake account is correct."
                return message
        
        return str(error)
    except Exception:
        return str(error)
    

def extract_sql_server_error_message(error) -> str:
    """
    Creates user friendly error messages for SQL Server errors.
    """
    try:
        if isinstance(error, str):
            if "HYT00" in error:
                message = "login timeout. Please verify the provided credentials."
            elif "42000" in error:
                message = "the target database being unavailable or misconfigured. Please verify the provided credentials."
            elif "28000" in error:
                message = "login error. Please ensure the specified SQL Server username & password are correct."
            return message
        
        return str(error)
    except Exception:
        return str(error)
    

def make_json_serializable(obj):
    """
    Recursively convert database values to JSON-serializable types.
    Handles Decimal, datetime, date, time, Row objects, and nested structures.
    """
    # Handle SQLAlchemy Row objects
    if isinstance(obj, Row):
        return [make_json_serializable(value) for value in obj]
    # Handle datetime types
    elif isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    # Handle Decimal - convert to int if whole number, otherwise float
    elif isinstance(obj, Decimal):
        float_val = float(obj)
        return int(float_val) if float_val.is_integer() else float_val
    # Handle bytes
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    # Handle float - convert to int if whole number
    elif isinstance(obj, float):
        return int(obj) if obj.is_integer() else obj
    # Handle collections
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, set):
        return [make_json_serializable(item) for item in obj]
    # Return as-is for other types (int, str, bool, None, etc.)
    else:
        return obj
    