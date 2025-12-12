import logging
import time
import pandas as pd
from typing import Any, Dict, Optional, List, Union
import json
import re
import requests
logging.basicConfig(level=logging.INFO, format='%(message)s')


class SodecoBase:
    """Base class for Sodeco API endpoints."""

    def __init__(self, sodeco):
        self.sodeco = sodeco
        self.max_attempts = 25
        self.poll_interval = 5  # seconds

    def _make_request_with_polling(self, url: str, method: str = 'GET', employer: str = None, headers: Optional[Dict] = None, document=False, **kwargs) -> Any:
        """
        Make a request and poll for results for each employer.

        This method handles the following status codes:
        - 200: Success, data is returned
        - 202: Request accepted, still processing
        - 204: No Content, endpoint exists but no data found

        For each employer in the list:
        1. Updates headers with employer information
        2. Makes initial request to get GUID
        3. Polls result endpoint until data is ready (200) or no data found (204)
        4. Adds employer information to each record

        Args:
            url: The URL to make the initial request to
            method: HTTP method to use (default: 'GET')
            headers: Additional headers to include in the request
            **kwargs: Additional arguments to pass to requests

        Returns:
            list: List of dictionaries containing data from all employers. Each record includes
                 an 'employer' field. Returns empty list if no data found (status 204).

        Raises:
            requests.exceptions.HTTPError: If any request fails
        """
        all_data = []

        self.sodeco.update_headers(str(employer))

        if headers:
            self.sodeco.session.headers.update(headers)

        response = self.sodeco.session.request(
            method=method,
            url=url,
            timeout=self.sodeco.timeout,
            **kwargs
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_content = response.content.decode('utf-8', errors='replace')
            logging.error(f"Request failed with status {response.status_code}. Response content: {error_content}")
            raise
        guid = response.json()

        while True:
            poll_url = f"{self.sodeco.base_url}result/{guid}"
            poll_response = self.sodeco.session.get(poll_url, timeout=self.sodeco.timeout)
            try:
                poll_response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                error_content = poll_response.content.decode('utf-8', errors='replace')
                logging.error(f"Polling request failed with status {poll_response.status_code}. Response content: {error_content}")
                raise
            result = poll_response.json()
            status = result.get("Statuscode")

            if status == "204":
                logging.info(f"No data found for employer {employer}")
                break
            elif status == "200" or status == "201":
                result_data = result.get("Response")
                if document:
                    return result_data
                result_json = json.loads(result_data) if result_data else {}
                if method == 'GET':
                    record_count = len(result_json)
                    logging.info(f"Received {record_count} records for employer {employer}")
                    if not isinstance(result_json, list):
                        result_json = [result_json]
                    all_data.extend([{**record, 'employer': employer} for record in result_json])
                else:  # POST, PUT
                    logging.info(f"Successfully processed request for employer {employer}")
                    all_data.append({**result_json, 'employer': employer})
                break
            elif status == "202" or status == "302":
                logging.info(f"Request still processing for employer {employer}, waiting {self.poll_interval} seconds...")
                time.sleep(self.poll_interval)
            else:
                try:
                    error_content = response.content.decode('utf-8', errors='replace')
                    error_content_poll_response = poll_response.content.decode('utf-8', errors='replace')
                except:
                    error_content = response.content
                    error_content_poll_response = poll_response.content
                logging.error(error_content)
                logging.error(error_content_poll_response)
                error_msg = f"Unexpected status code: {status}, initial request returned: {error_content} and polling request returned: {error_content_poll_response}"
                logging.error(error_msg)
                raise ValueError(error_msg)


        return all_data


    def _make_request_with_polling_for_employers(self, url: str, employers: list = None, use_pagination: bool = True, **kwargs) -> Any:
        """
        Make a request and poll for results for each employer.
        """
        all_data = []
        for employer in employers:
            if use_pagination:
                # Fetch all data with pagination
                limit = 100
                offset = 0
                data = []

                while True:
                    batch_data = self._make_request_with_polling(url, employer=employer, params={"limit": limit, "offset": offset})
                    data.extend(batch_data)

                    # If we got fewer results than the limit, we've reached the end
                    if len(batch_data) < limit:
                        break

                    # Increment offset for next batch
                    offset += limit

                total_records = len(data)
                logging.info(f"Completed processing employer {employer}. Total records: {total_records}")
            else:
                data = self._make_request_with_polling(url, employer=employer)

            all_data.extend(data)

        logging.info(f"Completed processing all employers. Total records: {len(all_data)}")

        return all_data


    def _filter_nan_values(self, data: Any) -> Any:
        """
        Recursively filter out NaN values from nested data structures.

        Args:
            data: The data to filter (can be dict, list, or scalar value)

        Returns:
            Filtered data with NaN values removed
        """
        if isinstance(data, dict):
            return {k: v for k, v in ((k, self._filter_nan_values(v)) for k, v in data.items()) if v is not None}
        elif isinstance(data, list):
            return [v for v in (self._filter_nan_values(x) for x in data) if v is not None]
        else:
            return None if pd.isna(data) else data

    def _prepare_raw_request(self, data: dict) -> tuple:
        """
        Prepare data for raw format request.

        Args:
            data: The data to convert to raw format

        Returns:
            tuple: (headers, data) tuple for the request
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        filtered_data = self._filter_nan_values(data)
        return headers, json.dumps(filtered_data)

    def _rename_camel_columns_to_snake_case(self, df: pd.DataFrame) -> pd.DataFrame:
        def camel_to_snake_case(column):
            # Replace periods with underscores
            column = column.replace('.', '_')
            # Insert underscores before capital letters and convert to lowercase
            return re.sub(r'(?<!^)(?=[A-Z])', '_', column).lower()

        df.columns = map(camel_to_snake_case, df.columns)
        return df
