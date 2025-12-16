import json
from urllib.parse import parse_qs, urlencode
import requests
import urllib
from .config import BASE_URL, TIMEOUT
from .exceptions import AuthenticationError, RequestError
from .utils import (
    format_date_range_offset,
    format_from_date_to_date_by_offset,
    format_query_params_to_query_string,
    generate_headers,
    get_string_to_sign,
    get_timestamp,
    modify_query_string,
    serialize_payload,
)
import hmac
import hashlib
import base64
from datetime import datetime


class ReportClient:
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        ref_id: int,
        base_url: str = BASE_URL,
        offset: int = 7,
    ):
        """
        Initializes the API client with authentication and configuration settings.

        Args:
            api_key (str): The API key used for authentication.
            secret_key (str): The secret key used for generating request signatures.
            base_url (str, optional): The base URL of the API. Defaults to BASE_URL.
            ref_id (int): A reference ID used for specific API requests.
            offset (int, optional): The time offset (in hours) for timestamp calculations. Defaults to 7.
        """
        self.api_key = api_key  # Store API key for authentication
        self.secret_key = secret_key  # Store secret key for HMAC signature
        self.base_url = base_url  # Store base URL for API requests
        self.ref_id = ref_id  # Store reference ID for API operations (if applicable)
        self.offset = offset  # Store time offset (default is 7 hours)

    def get_report(self, end_point: str, body: dict = None, params: dict = None):
        """
        Sends a GET request to retrieve a report from the API.

        Args:
            end_point (str): The API endpoint for fetching the report.
            body (dict, optional): The request payload containing report details. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            AuthenticationError: If the API key or signature is invalid (HTTP 401).
            RequestError: If the request fails or encounters an HTTP error.
        """
        query_string = format_query_params_to_query_string(params, self.ref_id)
        query_string = modify_query_string(query_string, self.offset)
        url = f"{self.base_url}{end_point}?{query_string}"  # Construct full URL
        headers = generate_headers(
            self.api_key, self.secret_key, method="GET", end_point=end_point, body=body
        )  # Generate headers

        try:
            response = requests.get(
                url, headers=headers, timeout=TIMEOUT
            )  # Send GET request
            response.raise_for_status()  # Raise error for HTTP failures
            return response  # Return parsed JSON response
        except requests.exceptions.HTTPError as e:
            if response.status_code == 500:
                raise RequestError(
                    f"HTTP error: {response.status_code}: {str(e)}"
                ) from e
            return response
        except requests.exceptions.RequestException as e:
            raise RequestError(
                "Request failed."
            ) from e  # Handle general request exceptions

    def create_report(self, end_point: str, body: dict = None, params: dict = None):
        """
        Sends a POST request to create a new report.

        Args:
            end_point (str): The API endpoint for creating the report.
            body (dict, optional): The request payload containing report details. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            AuthenticationError: If the API key or signature is invalid (HTTP 401).
            RequestError: If the request fails or encounters an HTTP error.
        """
        query_string = format_query_params_to_query_string(params, self.ref_id)
        query_string = modify_query_string(query_string, self.offset)
        url = f"{self.base_url}{end_point}?{query_string}"  # Construct full URL
        # payload = json.dumps(body)  # Convert body to JSON string
        headers = generate_headers(
            self.api_key, self.secret_key, method="POST", end_point=end_point, body=body
        )  # Generate headers

        try:
            response = requests.post(
                url, headers=headers, json=body, timeout=TIMEOUT
            )  # Send POST request
            response.raise_for_status()  # Raise error for HTTP failures
            return response  # Return parsed JSON response
        except requests.exceptions.HTTPError as e:
            if response.status_code == 500:
                raise RequestError(
                    f"HTTP error: {response.status_code}: {str(e)}"
                ) from e
            return response
        except requests.exceptions.RequestException as e:
            raise RequestError(
                "Request failed."
            ) from e  # Handle general request exceptions

    def get_detail_report(self, end_point: str, body: dict = None, params: dict = None):
        """
        Sends a GET request to retrieve details of a specific report.

        Args:
            report_id (int): The ID of the report to retrieve.
            params (dict, optional): Additional query parameters.

        Returns:
            Response: The response object from the API.
        """
        query_string = format_query_params_to_query_string(params, self.ref_id)
        query_string = modify_query_string(query_string, self.offset)
        url = f"{self.base_url}{end_point}?{query_string}"  # Construct full URL
        headers = generate_headers(
            self.api_key, self.secret_key, method="GET", end_point=end_point, body=body
        )  # Generate headers

        try:
            response = requests.get(
                url, headers=headers, timeout=TIMEOUT
            )  # Send GET request
            response.raise_for_status()  # Raise error for HTTP failures
            return response  # Return parsed JSON response
        except requests.exceptions.HTTPError as e:
            if response.status_code == 500:
                raise RequestError(
                    f"HTTP error: {response.status_code}: {str(e)}"
                ) from e
            return response
        except requests.exceptions.RequestException as e:
            raise RequestError(
                "Request failed."
            ) from e  # Handle general request exceptions

    def update_report(self, end_point: str, body: dict, params: dict = None):
        """
        Sends a PUT request to update a specific report.

        Args:
            report_id (int): The ID of the report to update.
            body (dict): The updated report data.
            params (dict, optional): Additional query parameters.

        Returns:
            Response: The response object from the API.
        """
        query_string = format_query_params_to_query_string(params, self.ref_id)
        query_string = modify_query_string(query_string, self.offset)
        url = f"{self.base_url}{end_point}?{query_string}"
        headers = generate_headers(
            self.api_key, self.secret_key, method="PUT", end_point=end_point, body=body
        )
        try:
            response = requests.put(
                url, headers=headers, json=body, timeout=TIMEOUT
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if response.status_code == 500:
                raise RequestError(
                    f"HTTP error: {response.status_code}: {str(e)}"
                ) from e
            return response
        except requests.exceptions.RequestException as e:
            raise RequestError(
                "Request failed."
            ) from e

    def delete_report(self, end_point: str, body: dict, params: dict = None):
        """
        Sends a DELETE request to remove a specific report.

        Args:
            report_id (int): The ID of the report to delete.
            params (dict, optional): Additional query parameters.

        Returns:
            Response: The response object from the API.
        """
        query_string = format_query_params_to_query_string(params, self.ref_id)
        query_string = modify_query_string(query_string, self.offset)
        url = f"{self.base_url}{end_point}?{query_string}"
        headers = generate_headers(
            self.api_key, self.secret_key, method="DELETE", end_point=end_point, body=body
        )
        try:
            response = requests.delete(
                url, headers=headers, timeout=TIMEOUT
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if response.status_code == 500:
                raise RequestError(
                    f"HTTP error: {response.status_code}: {str(e)}"
                ) from e
            return response
        except requests.exceptions.RequestException as e:
            raise RequestError(
                "Request failed."
            ) from e

    def get_list_report(self, body: dict = None, params: dict = {}):
        """
        Endpoint: /api/report/
        Required params: from_date, to_date, report_type
        - from_date: YYYY-MM-dd / YYYY-MM-dd HH:mm:ss
        - to_date: YYYY-MM-dd / YYYY-MM-dd HH:mm:ss
        - report_type: SALE, SALE_SERVICE, SALE_ADD_ON, DEDUCTION, DISCOUNT, SOLD_GIFT_CARD
        """
        end_point = "/api/report/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def get_total_report(self, body: dict = None, params: dict = {}):
        """
        Endpoint: /api/report/total/
        Required params: from_date, to_date, report_type
        - from_date: YYYY-MM-dd / YYYY-MM-dd HH:mm:ss
        - to_date: YYYY-MM-dd / YYYY-MM-dd HH:mm:ss
        - report_type: SALE, SALE_SERVICE, SALE_ADD_ON, DEDUCTION, DISCOUNT, SOLD_GIFT_CARD, TIP
        """
        end_point = "/api/report/total/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def get_summary_report(self, body: dict = None, params: dict = {}):
        """
        Endpoint: /api/report/summary/
        Required params: from_date, to_date
        - from_date: YYYY-MM-dd / YYYY-MM-dd HH:mm:ss
        - to_date: YYYY-MM-dd / YYYY-MM-dd HH:mm:ss
        """
        end_point = "/api/report/summary/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def push_data_report(self, body: dict, params: dict = {}):
        """
        Endpoint: /api/report/add-data/
        """
        params["source_id"] = body.get("id")
        end_point = "/api/report/add-data/"
        return self.create_report(
            end_point=end_point, body=serialize_payload(body), params=params
        )

    def get_revenue_summary(self, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/revenue/summary/
        """
        end_point = "/api/report/v2/revenue/summary/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def get_revenue_breakdown(self, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/revenue/breakdown/
        """
        end_point = "/api/report/v2/revenue/breakdown/"
        return self.get_report(end_point=end_point, body=body, params=params)

    # Staff Performance APIs
    def get_staff_performance_summary(self, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/staff-performance/summary/
        """
        end_point = "/api/report/v2/staff-performance/summary/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def get_staff_performance_breakdown(self, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/staff-performance/breakdown/
        """
        end_point = "/api/report/v2/staff-performance/breakdown/"
        return self.get_report(end_point=end_point, body=body, params=params)

    # Payroll APIs
    def get_payroll_summary(self, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/payroll/summary/
        """
        end_point = "/api/report/v2/payroll/summary/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def get_payroll_breakdown(self, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/payroll/breakdown/
        """
        end_point = "/api/report/v2/payroll/breakdown/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def get_detail_payroll_batch(self, batch_id:str, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/payroll-batch/{id}/
        """
        end_point = f"/api/report/v2/payroll-batch/{batch_id}/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def get_payroll_batch_histories_of_owner(self, owner_id:str, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/payroll-batch/histories/owners/{id}/
        """
        end_point = f"/api/report/v2/payroll-batch/histories/owners/{owner_id}/"
        return self.get_report(end_point=end_point, body=body, params=params)

    # Transactions APIs
    def get_transaction_summary(self, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/transactions/summary/
        """
        end_point = "/api/report/v2/transactions/summary/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def get_transaction_breakdown(self, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/transactions/breakdown/
        """
        end_point = "/api/report/v2/transactions/breakdown/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def create_payroll(self, body: dict = None, params: dict = {}):
        """
        POST /api/report/v2/payroll/
        """
        end_point = "/api/report/v2/payroll/"
        return self.create_report(end_point=end_point, body=body, params=params)

    def add_payroll_batch_multiple(self, body: dict, params: dict = {}):
        """
        POST /api/report/v2/payroll-batch/add-multiple/
        """
        end_point = "/api/report/v2/payroll-batch/add-multiple/"
        return self.create_report(end_point=end_point, body=serialize_payload(body), params=params)

    def approve_payroll_batch_multiple(self, body: dict, params: dict = {}):
        """
        POST /api/report/v2/payroll-batch/approve-multiple/
        """
        end_point = "/api/report/v2/payroll-batch/approve-multiple/"
        return self.create_report(end_point=end_point, body=serialize_payload(body), params=params)

    def get_payroll_batch(self, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/payroll-batch/
        """
        end_point = "/api/report/v2/payroll-batch/"
        return self.get_report(end_point=end_point, body=body, params=params)

    # Payroll Adjustment APIs
    def get_payroll_adjustment(self, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/payroll-adjustment/
        """
        end_point = "/api/report/v2/payroll-adjustment/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def create_payroll_adjustment(self, body: dict, params: dict = {}):
        """
        POST /api/report/v2/payroll-adjustment/
        """
        end_point = "/api/report/v2/payroll-adjustment/"
        return self.create_report(end_point=end_point, body=serialize_payload(body), params=params)

    def get_payroll_adjustment_by_id(self, adj_id: str, body: dict = None, params: dict = {}):
        """
        GET /api/report/v2/payroll-adjustment/{adj_id}/
        """
        end_point = f"/api/report/v2/payroll-adjustment/{adj_id}/"
        return self.get_report(end_point=end_point, body=body, params=params)

    def update_payroll_adjustment(self, adj_id: str, body: dict, params: dict = {}):
        """
        PUT /api/report/v2/payroll-adjustment/{adj_id}/
        """
        end_point = f"/api/report/v2/payroll-adjustment/{adj_id}/"
        return self.update_report(end_point=end_point, body=serialize_payload(body), params=params)

    def delete_payroll_adjustment(self, adj_id: str, body: dict = None, params: dict = {}):
        """
        DELETE /api/report/v2/payroll-adjustment/{adj_id}/
        """
        end_point = f"/api/report/v2/payroll-adjustment/{adj_id}/"
        # Assuming delete_report might take a body as well
        return self.delete_report(end_point=end_point, body=body, params=params)

    # Adjust Tips, Services, Technician APIs
    def adjust_tips(self, body: dict, params: dict = {}):
        """
        PUT /api/report/v2/adjust-tips/
        Adjust tips for staff in a booking transaction.
        """
        end_point = "/api/report/v2/adjust-tips/"
        return self.update_report(end_point=end_point, body=serialize_payload(body), params=params)

    def adjust_services(self, body: dict, params: dict = {}):
        """
        POST /api/report/v2/adjust-services/
        Add services to a paid booking transaction.
        """
        end_point = "/api/report/v2/adjust-services/"
        return self.create_report(end_point=end_point, body=serialize_payload(body), params=params)

    def adjust_technician(self, body: dict, params: dict = {}):
        """
        PUT /api/report/v2/adjust-technician/
        Reassign technician for services and optionally reallocate tips.
        """
        end_point = "/api/report/v2/adjust-technician/"
        return self.update_report(end_point=end_point, body=serialize_payload(body), params=params)

