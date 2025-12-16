from decimal import Decimal
from enum import Enum
import hashlib
import hmac
from urllib.parse import parse_qs, urlencode
from django.utils import timezone
from datetime import datetime


def get_timestamp() -> str:
    """
    Returns the current timestamp in seconds as a string.

    Returns:
        str: The current timestamp in seconds.
    """
    return str(datetime.now().timestamp())  # Convert timestamp to string


def get_string_to_sign(
    method: str, endpoint: str, timestamp: str, body: dict = None
) -> str:
    """
    Constructs the string to sign for request authentication.

    Args:
        method (str): The HTTP method (e.g., "GET", "POST").
        endpoint (str): The API endpoint being accessed.
        timestamp (str): The timestamp of the request.
        body (str, optional): The request body (if applicable). Defaults to None.

    Returns:
        str: The formatted string to sign.
    """
    return f"{str(method).upper()}\n{endpoint}\n{timestamp}\n{body or ''}"  # Format string with newline separators


def modify_query_string(
    query_string, offset, modified_fields: set = ("from_date", "to_date")
) -> str:
    """
    Modify query params by applying the given modifications.

    Args:
        query_string (str): Original query string (e.g., "from_date=2024-02-15&to_date=2024-02-16").
        modified_fields (set): Default is set('from_date', 'to_date')
    Returns:
        str: Updated query string.
    """
    # Parse the query params into a dictionary
    query_dict = parse_qs(query_string)

    # Apply modifications
    if (
        query_dict.get(modified_fields[0], [])
        and query_dict.get(modified_fields[1], [])
        and query_dict.get(modified_fields[0])[0]
        and query_dict.get(modified_fields[1])[0]
    ):
        try:
            from_date_ = datetime.strptime(
                query_dict.get(modified_fields[0])[0], "%Y-%m-%d %H:%M:%S"
            )
            to_date_ = datetime.strptime(
                query_dict.get(modified_fields[1])[0], "%Y-%m-%d %H:%M:%S"
            ).replace(hour=0, minute=0, second=0, microsecond=0)
            from_date, to_date = format_date_range_offset(from_date_, to_date_, offset)
        except Exception as ex:
            from_date, to_date = format_from_date_to_date_by_offset(
                query_dict.get(modified_fields[0])[0],
                query_dict.get(modified_fields[1])[0],
                offset,
            )
        query_dict[modified_fields[0]] = [from_date]
        query_dict[modified_fields[1]] = [to_date]
    else:
        return query_string

    # Convert back to query string
    updated_query = urlencode(query_dict, doseq=True)
    return updated_query


def generate_signature(secret_key: str, string_to_sign: str) -> str:
    """
    Generates an HMAC SHA-256 signature.

    Args:
        string_to_sign (str): The string that needs to be signed.

    Returns:
        str: The generated HMAC SHA-256 hexadecimal signature.
    """
    return hmac.new(
        secret_key.encode("utf-8"),  # Convert secret key to bytes
        string_to_sign.encode("utf-8"),  # Convert string to sign to bytes
        hashlib.sha256,  # Use SHA-256 hashing algorithm
    ).hexdigest()  # Return the hexadecimal representation of the hash


def generate_headers(
    api_key: str, secret_key: str, method: str, end_point: str, body: dict = None
) -> dict:
    """
    Generates request headers with authentication details.

    Args:
        method (str): The HTTP method (e.g., "GET", "POST").
        end_point (str): The API endpoint being accessed.
        body (dict, optional): The request body (if applicable). Defaults to None.

    Returns:
        dict: A dictionary containing headers including content type, API key, signature, and timestamp.
    """
    timestamp = get_timestamp()  # Get current timestamp
    string_to_sign = get_string_to_sign(
        method, end_point, timestamp, body
    )  # Generate the string to sign
    signature = generate_signature(
        secret_key, string_to_sign
    )  # Generate HMAC signature
    # print(string_to_sign)
    # print(signature)

    return {
        "Content-Type": "application/json",  # Specify JSON content type
        "API-KEY": api_key,  # Include API key for authentication
        "Signature": signature,  # Include computed signature
        "Timestamp": timestamp,  # Include timestamp to prevent replay attacks
    }


def format_query_params_to_query_string(params, ref_id) -> str:
    return urlencode(params) + f"&ref_id={ref_id}" if params is not None else f"ref_id={ref_id}"


def format_date_range_offset(from_date, to_date, offset):
    from_date_offset = from_date - timezone.timedelta(hours=offset)
    to_date_offset = (
        to_date + timezone.timedelta(days=1) - timezone.timedelta(hours=offset)
    )

    return from_date_offset, to_date_offset


def format_str_to_date(str_date):
    """
    Validate date format of string

    Return: string with date format
    """
    format = f"%Y-%m-%d"
    try:
        date = datetime.strptime(str_date, format)
        return date
    except Exception as ex:
        raise ValueError("Invalid format. Format: yyyy-MM-dd")


def format_from_date_to_date(from_date, to_date):
    try:
        from_date = format_str_to_date(from_date)
        to_date = format_str_to_date(to_date)
    except:
        return datetime.strptime(from_date, "%Y-%m-%d"), datetime.strptime(
            to_date, "%Y-%m-%d"
        )
    return from_date, to_date


def format_from_date_to_date_by_offset(from_date, to_date, offset):
    from_date, to_date = format_from_date_to_date(from_date, to_date)
    from_date_offset, to_date_offset = format_date_range_offset(
        from_date, to_date, offset
    )
    return from_date_offset, to_date_offset


def serialize_payload(data: dict) -> dict:
    """Convert all Enum fields in a dict to their string representation."""
    for key, value in data.items():
        if isinstance(value, Enum):  # Check if the value is an Enum instance
            data[key] = value.value
        elif isinstance(value, dict):  # Recursively process nested dictionaries 
            data[key] = serialize_payload(value)
        elif isinstance(value, list):  # Recursively process lists of dictionaries
            data[key] = [
                serialize_payload(item) if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(value, Decimal):
            data[key] = float(value)
        elif isinstance(value, datetime):  # Xử lý datetime objects
            data[key] = value.isoformat()
        elif isinstance(value, bytes):  # Xử lý bytes objects
            data[key] = value.decode('utf-8')
        elif isinstance(value, set):  # Xử lý set objects
            data[key] = list(value)
        elif isinstance(value, complex):  # Xử lý complex numbers
            data[key] = str(value)
        elif hasattr(value, '__dict__'):  # Xử lý custom objects
            data[key] = serialize_payload(value.__dict__)
        elif value is None:  # Xử lý None values
            data[key] = None
    return data
