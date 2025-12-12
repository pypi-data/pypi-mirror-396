import importlib
import json
import logging
import sys

import requests
from urllib.parse import urlparse, urlunparse

# from pip._internal.metadata import pkg_resources
import pkg_resources
from raga import spinner
import subprocess
logger = logging.getLogger(__name__)
from raga.constants import CLIENT_PACKAGE_NAME

class HTTPClient:
    def __init__(self, base_url: str):
        self.base_url = self.validate_base_url(base_url)
        logger.debug(f"Base URL: {self.base_url}")

    def remove_extra_slashes(self, url):
        parsed_url = urlparse(url)
        cleaned_path = "/".join(segment for segment in parsed_url.path.split("/") if segment)
        cleaned_url = urlunparse(parsed_url._replace(path=cleaned_path))
        return cleaned_url

    def validate_base_url(self, base_url: str) -> str:
        """
        Validates the base URL format and returns the validated URL.

        Args:
            base_url (str): The base URL to validate.

        Returns:
            str: The validated base URL.

        Raises:
            ValueError: If the base URL format is invalid.
        """
        base_url = f"{base_url}/"
        parsed_url = urlparse(base_url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError("Invalid base URL. Must be in the format 'http(s)://domain.com'.")
        return base_url

    def get_latest_version_from_pypi(self, package_name):
        url = f'https://pypi.org/pypi/{package_name}/json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
        else:
            raise Exception(f"Failed to fetch information for {package_name} from PyPI.")

    def check_and_update_package(self, package_name):
        try:
            installed_version = pkg_resources.get_distribution(package_name).version
            logging.debug(f"Installed version of {package_name}: {installed_version}")

            latest_version = self.get_latest_version_from_pypi(package_name)
            logging.debug(f"latest version is:{latest_version}")
            if installed_version != latest_version:
                print("Warning: Latest client package not installed.")
                print(f"Updating {package_name} to the latest version...")
                subprocess.run(['pip', 'install', f'{package_name}=={latest_version}', '-q'], check=True)
                print(f"{package_name} updated successfully.")
            else:
                print(f"{package_name} is already up-to-date.")
        except pkg_resources.DistributionNotFound:
            print(f"{package_name} is not installed.")

    def get(self, endpoint: str, params=None, data=None, headers=None):
        """
        Sends a GET request to the specified endpoint.

        Args:
            endpoint (str): The endpoint to send the GET request to.
            params (dict, optional): The query parameters for the GET request. Defaults to None.
            data (dict, optional): The request payload for the GET request. Defaults to None.
            headers (dict, optional): The headers for the GET request. Defaults to None.

        Returns:
            dict: The JSON response from the GET request.

        Raises:
            ValueError: If the GET request is unsuccessful or returns an error response.
        """
        url = self.remove_extra_slashes(self.base_url + endpoint)
        logger.debug(f"API ENDPOINT {url}")
        logger.debug(f"API PARAMS {json.dumps(params)}")
        logger.debug(f"API DATA {json.dumps(data)}")
        logger.debug(f"API HEADER {json.dumps(headers)}")

        default_headers = {'Content-Type': 'application/json'}
        if headers:
            headers = {**default_headers, **headers}
        else:
            headers = default_headers
            
        if data:
            data = json.dumps(data)

        response = requests.get(url, params=params, data=data, headers=headers)
        logger.debug(f"API RESPONSE {response.json()}")
        status_code = response.status_code
        json_data = response.json()

        if status_code in (200, 201) and json_data.get("success"):
            spinner.succeed(json_data.get("message"))
            logger.debug(json_data.get("message"))
            return json_data
        else:
            error_message = json_data.get("message")
            if status_code == 404:
                logging.error(f"HTTP error : {status_code} : {error_message}")
                package = CLIENT_PACKAGE_NAME
                try:
                    self.check_and_update_package(package)
                    print("Please rerun the test")
                except:
                    print("Install the latest version of python client and rerun the test")
            elif status_code == 401 or status_code == 400:
                logging.error(f"HTTP error : {status_code} : {error_message}")
                print(f"{status_code}: Authentication failed, please retry with correct or new raga access key and secret key")
            elif status_code == 403:
                logging.error(f"HTTP error : {status_code} : {error_message}")
                print(f"{status_code}: Don't have permission to access requested resource")
            elif str(status_code).startswith('5'):
                logging.error(f"HTTP error : {status_code} : {error_message}")
                print(f"{status_code}: Internal Server error occurred, retry")
            elif str(status_code).startswith('4'):
                logging.error(f"HTTP error : {status_code} : {error_message}")
                print(f"Invalid request - HTTP error : {status_code} : {error_message}")
                print("Retry with correct request")
            sys.exit(1)

    def post(self, endpoint: str, data=None, headers=None, file=None, spin=True):
        """
        Sends a POST request to the specified endpoint.

        Args:
            endpoint (str): The endpoint to send the POST request to.
            data (dict, optional): The request payload for the POST request. Defaults to None.
            headers (dict, optional): The headers for the POST request. Defaults to None.

        Returns:
            dict: The JSON response from the POST request.

        Raises:
            ValueError: If the POST request is unsuccessful or returns an error response.
        """
        url = self.remove_extra_slashes(self.base_url + endpoint)
        logger.debug(f"API ENDPOINT {endpoint}")
        logger.debug(f"API DATA {json.dumps(data)}")
        logger.debug(f"API HEADER {json.dumps(headers)}")
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            if file:
                headers = headers
            else:
                headers = {**default_headers, **headers}
        else:
            headers = default_headers

        if file:
            files=[
            ('file',('zip',open(file,'rb'),'application/zip'))
            ]
            response = requests.request("POST", url, headers=headers, data=data, files=files)
        else:
            response = requests.request('POST', url, json=data, headers=headers)


        logger.debug(f"API RESPONSE {response.json()}")
        status_code = response.status_code
        json_data = response.json()
        if status_code in (200, 201) and json_data.get("success"):
            if spin:
                spinner.succeed(json_data.get("message"))
            logger.debug(json_data.get("message"))
            return json_data
        else:
            error_message = json_data.get("message")
            if status_code == 404:
                logging.error(f"HTTP error : {status_code} : {error_message}")
                package = CLIENT_PACKAGE_NAME
                try:
                    self.check_and_update_package(package)
                    print("Please rerun the test")
                except:
                    print("Install the latest version of python client and rerun the test")
            elif status_code == 401 or status_code == 400:
                logging.error(f"HTTP error : {status_code} : {error_message}")
                print(f"{status_code}: Authentication failed, please retry with correct or new raga access key and secret key")
            elif status_code == 403:
                logging.error(f"HTTP error : {status_code} : {error_message}")
                print(f"{status_code}: Don't have permission to access requested resource")
            elif str(status_code).startswith('5'):
                logging.error(f"HTTP error : {status_code} : {error_message}")
                print(f"{status_code}: Internal Server error occurred, retry")
            elif str(status_code).startswith('4'):
                logging.error(f"HTTP error : {status_code} : {error_message}")
                print(f"Invalid request - HTTP error : {status_code} : {error_message}")
                print("Retry with correct request")
            sys.exit(1)


    def put(self, endpoint: str, data=None, headers=None, spin=True):
        """
        Sends a PUT request to the specified endpoint.

        Args:
            endpoint (str): The endpoint to send the PUT request to.
            data (dict, optional): The request payload for the PUT request. Defaults to None.
            headers (dict, optional): The headers for the PUT request. Defaults to None.

        Returns:
            dict: The JSON response from the PUT request.

        Raises:
            ValueError: If the PUT request is unsuccessful or returns an error response.
        """

        url = self.remove_extra_slashes(self.base_url + endpoint)
        logger.debug(f"API ENDPOINT {endpoint}")
        logger.debug(f"API DATA {json.dumps(data)}")
        logger.debug(f"API HEADER {json.dumps(headers)}")
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            headers = {**default_headers, **headers}
        else:
            headers = default_headers

        response = requests.request('PUT', url, json=data, headers=headers)
            
        logger.debug(f"API RESPONSE {response.json()}")
        status_code = response.status_code
        json_data = response.json()

        if status_code in (200, 201) and json_data.get("success"):
            if spin:
                spinner.succeed(json_data.get("message"))
            logger.debug(json_data.get("message"))
            return json_data
        else:
            error_message = json_data.get("message")
            if error_message:
                raise ValueError(f"Request failed with status code {status_code}: {error_message}")
            else:
                raise ValueError(f"Request failed with status code {status_code}")


