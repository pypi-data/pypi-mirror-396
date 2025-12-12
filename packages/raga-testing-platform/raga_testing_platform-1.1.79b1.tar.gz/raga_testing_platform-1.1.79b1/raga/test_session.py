import datetime
import json
import logging
import os
import sys
import time
import uuid


import requests
from raga.constants import AWS_RAGA_SECRET_KEY, AWS_RAGA_ACCESS_KEY, AWS_RAGA_ROLE_ARN, INVALID_RESPONSE
from raga.validators.test_session_validation import TestSessionValidator
from raga.utils import HTTPClient
from raga.utils import read_raga_config, get_config_value
from raga import spinner
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class TestSession():
    MAX_RETRIES = 6
    RETRY_DELAY = 1
    ACCESS_KEY = "raga_access_key_id"
    SECRET_KEY = "raga_secret_access_key"



    def __init__(self, 
                 project_name: str, 
                 run_name: str = None,
                 u_test=False,
                 host=None,
                 access_key=None,
                 secret_key=None,
                 aws_raga_secret_key=None,
                 aws_raga_access_key=None,
                 aws_raga_role_arn=None,
                 profile=None,
                 inline_raga_config=False):
        spinner.start()
        
        config_data = read_raga_config(profile=profile, inline_raga_config=inline_raga_config)
        self.api_host = host if host else get_config_value(config_data, 'api_host')
        self.raga_access_key_id = access_key if access_key else get_config_value(config_data, self.ACCESS_KEY)
        self.raga_secret_access_key = secret_key if secret_key else get_config_value(config_data, self.SECRET_KEY)
        self.aws_raga_secret = aws_raga_secret_key if aws_raga_secret_key else get_config_value(config_data, AWS_RAGA_SECRET_KEY)
        self.aws_raga_access = aws_raga_access_key if aws_raga_access_key else get_config_value(config_data, AWS_RAGA_ACCESS_KEY)
        self.aws_raga_arn = aws_raga_role_arn if aws_raga_role_arn else get_config_value(config_data, AWS_RAGA_ROLE_ARN)
        self.project_name = TestSessionValidator.validate_project_name(project_name)
        if run_name is not None:
            self.run_name = TestSessionValidator.validate_run_name(run_name)
        else:
            self.run_name = run_name
        self.http_client = HTTPClient(self.api_host)
        self.test_list = []
        self.added = False

        self.token = None
        self.project_id = None
        self.experiment_id = None
        if not u_test:
            self.initialize()
        spinner.stop()


    def initialize(self):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                self.token = self.create_token()
                self.project_id = self.get_project_id()
                break  # Exit the loop if initialization succeeds
            except requests.exceptions.RequestException as exception:
                print(f"Network error occurred: {str(exception)}")
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Retrying in {self.RETRY_DELAY} second(s)...")
                    time.sleep(self.RETRY_DELAY)

    def add(self, payload):
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty dictionary.")
        elif payload.get("test_type") == "ab":
            if payload.get("outputType") == "labelled-ss-metadata" or payload.get("outputType") == "labelled-ss-cluster":
                payload["api_end_point"] = "api/experiment/test/ab-labelled-semantic-segmentation"
            elif payload.get("subType") == "multi-label":
                if payload.get("outputType") == "labelled-ic-metadata" or payload.get("outputType") == "labelled-ic-cluster":
                    payload["api_end_point"] = "api/experiment/test/ab-labelled-image-classification"
            elif payload.get("outputType") == "labelled-od-metadata" or payload.get("outputType") == "labelled-od-cluster":
                payload["api_end_point"] = "api/experiment/test/ab-labelled-object-detection"
        elif payload.get("test_type") == "ab_test":
            if payload.get("type") == "unlabelled":
                payload["api_end_point"] =  "api/experiment/test/unlabelled"
            if payload.get("type") == "labelled":
                payload["api_end_point"] = "api/experiment/test/labelled"
                
        elif payload.get("test_type") == "event_ab_test":
            payload["api_end_point"] = "api/experiment/test/ab-event/v2"
            
        elif payload.get("test_type") == "drift_test":
            payload["api_end_point"] = "api/experiment/test/drift/v2"

        elif payload.get("type") == "label_drift":
            payload["api_end_point"] = "api/experiment/test/label-drift-detection"

        elif payload.get("test_type") == "guardrail":
            payload["api_end_point"] = "api/experiment/test/guardrail"
            
        elif payload.get("test_type") == "cluster":
            payload["api_end_point"] =  "api/experiment/test/fma/v2"
            if payload.get("outputType") == "event_detection":
                payload["api_end_point"] =  "api/experiment/test/fma-event/v2"
            if payload.get("outputType") == "instance_segmentation":
                payload["api_end_point"] = "api/experiment/test/fma/instance-segmentation"
            if payload.get("outputType") == "keypoint_detections":
                payload["api_end_point"] = "api/experiment/test/fma/keypoint-detection"


        elif payload.get("test_type") == "ocr_test":
            if payload.get("outputType")  == "missing_value":
                payload["api_end_point"] =  "api/experiment/test/ocr"
            elif payload.get("outputType")  == "anomaly_detection":
                payload["api_end_point"] =  "api/experiment/test/ocr/outlier-detection/v2"
                
        elif payload.get("test_type") == "labelling_quality" and payload.get("outputType") == "instance_segmentation":
            payload["api_end_point"] = "api/experiment/test/instance-segmentation/labelling-quality"

        elif payload.get("test_type") == "labelling_quality" and payload.get("outputType") == "keypoint_detection":
            payload["api_end_point"] = "api/experiment/test/key-point-detection/lqt"
        elif payload.get("test_type") == "scenario_imbalance" and payload.get("outputType") == "reference_dataset_metadata":
            payload["api_end_point"] = "api/experiment/test/scenario-imbalance/reference-dataset"
        elif payload.get("test_type") == "scenario_imbalance" and payload.get("outputType") == "reference_dataset_cluster":
            payload["api_end_point"] = "api/experiment/test/scenario-imbalance/reference-dataset"
        elif payload.get("test_type") == "scenario_imbalance" and payload.get("outputType") == "min_check_metadata":
            payload["api_end_point"] = "api/experiment/test/scenario-imbalance/reference-dataset"
        elif payload.get("test_type") == "scenario_imbalance" and payload.get("outputType") == "min_check_cluster":
            payload["api_end_point"] = "api/experiment/test/scenario-imbalance/reference-dataset"
        elif payload.get("test_type") == "labelling_quality":
            payload["api_end_point"] =  "api/experiment/test/labelling-quality/v2"
        elif payload.get("test_type") == "labelling_consistency":
            payload["api_end_point"] =  "api/experiment/test/labelling-consistency/v2"
        elif payload.get("test_type") == "active_learning":
            payload["api_end_point"] =  "api/experiment/test/active-learning"
        elif payload.get("test_type") == "semantic_similarity":
            payload["api_end_point"] =  "api/experiment/test/semantic-similarity/v2"
        elif payload.get("test_type") == "nearest-neighbour":
            if payload.get("outputType") == "keypoint_detections":
                payload["api_end_point"] = "api/experiment/test/key-point-detection/near-duplicate"
            else:
                payload["api_end_point"] = "api/experiment/test/near-duplicate/v2"
        elif payload.get("test_type") == "data_leakage":
            payload["api_end_point"] =  "api/experiment/test/data-leakage/v2"
        elif payload.get("test_type") == "data_augmentation":
            payload["api_end_point"] =  "api/experiment/test/data-augmentation"
        elif payload.get("test_type") == "fma-llm":
            payload["api_end_point"] =  "api/experiment/test/fma-llm/v2"
        elif  payload.get("test_type") == "fma_sd":
            payload["api_end_point"] =  "api/experiment/test/fma/structured-data"
        elif payload.get("test_type") == "class-imbalance":
            payload["api_end_point"] = "api/experiment/test/class-imbalance"
        elif payload.get("test_type") == "scenario_imbalance":
            if payload.get("outputType") == "keypoint_detections":
                payload["api_end_point"] = "api/experiment/test/key-point-detection/scenario-imbalance"
            else:
                payload["api_end_point"] = "api/experiment/test/scenario-imbalance"
        elif payload.get("test_type") == "stress_test":
            payload["api_end_point"] = "api/experiment/test/stress-test"
        elif payload.get("test_type") == "image-property-drift":
            payload["api_end_point"] = "api/experiment/test/image-property-drift"
        elif payload.get("test_type") == "llm-drift":
            payload["api_end_point"] = "api/experiment/test/llm-drift"
        elif payload.get("test_type") == "llm-performance":
            payload["api_end_point"] = "api/experiment/llm/performance-test"
        elif payload.get("test_type") == "fma_semantic_geospatial":
            payload["api_end_point"] = "api/experiment/test/fma/semantic-segmentation/spatio"
        elif payload.get("test_type") == "spatio-drift":
            payload["api_end_point"] = "api/experiment/test/spatio-drift"
        elif payload.get("test_type") == "entropy-analysis":
            payload["api_end_point"] = "api/experiment/test/entropy-analysis"
        elif payload.get("test_type") == "outlier_detection" and payload.get("outputType") == "structured_data":
            payload["api_end_point"] = "api/experiment/test/outlier-detection/structured-data"
        self.test_list.append(payload)
        self.added = True

    def link(self, execution_ids):
        api_end_point = "api/link-sibling-executions"
        _uuid = str(uuid.uuid4())
        test_payload = {
            "id": _uuid,
            "executionIds": execution_ids
        }
        self.http_client.post(api_end_point, data=test_payload, headers={"Authorization": f'Bearer {self.token}'})

    def  run(self):
        from raga.constants import INVALID_RESPONSE
        if self.run_name is not None:
            self.experiment_id = self.create_experiment()
        if self.experiment_id is None:
            raise ValueError("No run name passed in test session")
        # Check if already added
        if not self.added:
            raise ValueError("add() is not called. Call add() before run().")
        if not len(self.test_list):
            raise ValueError("Test not found.")
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                for test_payload in self.test_list:
                    api_end_point = test_payload.get("api_end_point")
                    test_payload['experimentId'] = self.experiment_id
                    test_payload.pop("api_end_point")
                    test_payload.pop("test_type")
                    res_data = self.http_client.post(api_end_point, data=test_payload, headers={"Authorization": f'Bearer {self.token}'})
                    if not isinstance(res_data, dict):
                        raise ValueError(INVALID_RESPONSE)
                    logger.debug(res_data.get('data', ''))
                    self.test_list = []
                    spinner.succeed("Succeed!")
                    return res_data.get('data', '')
            except requests.exceptions.RequestException as exception:
                print(f"Network error occurred: {str(exception)}")
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Retrying in {self.RETRY_DELAY} second(s)...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    spinner.fail("Fail!")
                self.test_list = []
                spinner.stop()
    def create_token(self):
        """
        Creates an authentication token by sending a request to the Raga API.

        Returns:
            str: The authentication token.

        Raises:
            KeyError: If the response data does not contain a valid token.
        """
        from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA
        res_data = self.http_client.post(
            "api/token",
            {"accessKey": self.raga_access_key_id, "secretKey": self.raga_secret_access_key},
        )
        if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)
        token = res_data.get("data", {}).get("token")
        if not token:
            print("access key and secret key expired, please create test session with new raga access and secret key")
            sys.exit(1)
            # raise KeyError(INVALID_RESPONSE_DATA)
        return token


    def get_project_id(self):
        """
        Get project id by sending a request to the Raga API.

        Returns:
            str: The ID of the project.

        Raises:
            KeyError: If the response data does not contain a valid project ID.
            ValueError: If the response data is not in the expected format.
        """
        from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA
        res_data = self.http_client.get(
            "api/project",
            params={"name": self.project_name},
            headers={"Authorization": f'Bearer {self.token}'},
        )

        if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)

        project_id = res_data.get("data", {}).get("id")

        if not project_id:
            raise KeyError(INVALID_RESPONSE_DATA)
        return project_id



    def create_experiment(self):
        """
        Creates an experiment by sending a request to the Raga API.

        Returns:
            str: The ID of the created experiment.

        Raises:
            KeyError: If the response data does not contain a valid experiment ID.
            ValueError: If the response data is not in the expected format.
        """
        from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA
        res_data = self.http_client.post(
            "api/experiment",
            {"name": self.run_name, "projectId": self.project_id},
            {"Authorization": f'Bearer {self.token}'},
        )

        if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)

        experiment_id = res_data.get("data", {}).get("id")

        if experiment_id is None:
            raise KeyError(INVALID_RESPONSE_DATA)
        return experiment_id

    def download_dataset(self, download_folder, run_name=None, test_name=None):
        url = "api/dataset/download?"
        if run_name is not None:
            url += f"experimentName={run_name}&"
        if test_name is not None:
            url += f"testName={test_name}"

        res_data = self.http_client.get(
            url,
            params={"name": self.project_name},
            headers={"Authorization": f'Bearer {self.token}'},
        )
        if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)

        presigned_url = res_data.get("data", {}).get("zipFileDownload")
        os.makedirs(download_folder, exist_ok=True)

        try:
            # Make a GET request to the presigned URL
            response = requests.get(presigned_url, stream=True)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

            # Extract the file name from the Content-Disposition header
            file_name = self.get_file_name(presigned_url)

            # Path to save the downloaded file
            file_path = os.path.join(download_folder, file_name)

            # Save the content to a file
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"File downloaded successfully: {file_path}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download file: {e}")

    def get_file_name(self, presigned_url):
        parsed_url = urlparse(presigned_url)
        return parsed_url.path.split('/')[-1]

