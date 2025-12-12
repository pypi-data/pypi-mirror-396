import os
import time
import requests
import logging
from typing import Callable, Any

from tqdm import tqdm

from raga import TestSession, spinner
from raga.exception import RagaException

logger = logging.getLogger(__name__)


class ModelException(RagaException):
    pass


class Model:

    MAX_RETRIES = 3
    RETRY_DELAY = 5

    def __init__(
        self,
        test_session: TestSession,
        name: str,
        version: str,
        description: str,
        docker_image: str,
        config_params: dict = {},
        infra_params: dict = {},
        input_func: Callable[[Any], Any] = None,
        output_func: Callable[[Any], Any] = None,
        is_raga_internal: bool = False,
        ignore_model_upload: bool = False,
    ):
        self.test_session = test_session
        self.name = name
        self.version = version
        self.description = description
        self.docker_image = docker_image
        self.config_params = config_params
        self.infra_params = infra_params
        self.input_func = input_func
        self.output_func = output_func
        self.is_raga_internal = is_raga_internal
        self.ignore_model_upload = ignore_model_upload
    
    def load(self):
        spinner.start()
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                self.upload_model()
                spinner.succeed("Model upload successful!")
                break
            except requests.exceptions.RequestException as e:
                logger.info(f"Network error occured: {str(e)}")
                retries += 1
                if retries < self.MAX_RETRIES:
                    logger.info(f"Retrying in {self.RETRY_DELAY} second(s)...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    spinner.fail("Fail!")
            except Exception as e:
                spinner.fail(str(e))
                break

    def upload_model(self):
        model_s3_path, registry_path = None, None
        if "/" in self.docker_image:
            registry_path = self.docker_image
        else:
            model_s3_path = self.save_model_to_s3()
            logger.debug(f"model s3 path : {model_s3_path}")

        payload = {
            "projectName": self.test_session.project_name,
            "modelName": self.name,
            "modelVersion": self.version,
            "modelTarPath": model_s3_path,
            "registryPath": registry_path,
            "dockerImage": self.docker_image,
            "description": self.description,
            "configParams": self.config_params,
            "infraParams": self.infra_params,
            "isInternal": self.is_raga_internal,
            "ignoreModelUpload": self.ignore_model_upload,
        }
        if self.input_func and self.output_func:
            import base64
            import inspect
            input_func_string = inspect.getsource(self.input_func)
            output_func_string = inspect.getsource(self.output_func)
            payload["inputFunc"] = base64.b64encode(input_func_string.encode()).decode()
            payload["outputFunc"] = base64.b64encode(output_func_string.encode()).decode()

        response = self.test_session.http_client.post(
            f"api/model/upload",
            headers={"Authorization": f'Bearer {self.test_session.token}'},
            data=payload
        )
        if not response["success"]:
            logger.debug(f"upload error : {response['message']}")
            raise ModelException(response)

    def save_model_to_s3(self):
        # save image tar ball
        import docker
        docker_cli = docker.from_env()
        image = docker_cli.images.get(self.docker_image)
        tar_file_name = f"{self.name}-{self.version}.tar"
        tar_file_path = f"/tmp/{tar_file_name}"
        logger.debug(f"saving docker image {self.docker_image} to {tar_file_path}")
        with open(tar_file_path, 'wb') as fd:
            for chunk in image.save():
                fd.write(chunk)

        # upload to s3
        pre_signed_url, s3_path = self.get_pre_signed_s3_url(tar_file_name)
        logger.debug(f"UPLOADING {tar_file_path} to {s3_path}")
        self.upload_file_to_s3(pre_signed_url, tar_file_path)
        os.remove(tar_file_path)
        return s3_path

    def get_pre_signed_s3_url(self, file_name: str):
        try:
            res_data = self.test_session.http_client.post(
                f"api/model/upload/preSignedUrls",
                headers={"Authorization": f'Bearer {self.test_session.token}'},
                data={
                    "projectName": self.test_session.project_name, 
                    "fileNames": [file_name],
                    "contentType": "application/x-tar",
                 },
            )
            if res_data.get("data") and "urls" in res_data["data"] and "filePaths" in res_data["data"]:
                logger.debug("Pre-signed URL generated")
                return res_data["data"]["urls"][0], res_data["data"]["filePaths"][0]
            else:
                error_message = "Failed to get pre-signed URL. Required keys not found in the response."
                logger.error(error_message)
                raise ValueError(error_message)
        except Exception as e:
            logger.exception("An error occurred while getting pre-signed URL: %s", e)
            raise

    def upload_file_to_s3(self, pre_signed_url, file_path):
        logger.debug(f"uploading {file_path} to s3 via pre signed url")
        print("Uploading model to s3")
        spinner.start()
        try:
            with open(file_path, "rb") as fd:
                headers = {"Content-Type": "application/x-tar"}
                if "blob.core.windows.net" in pre_signed_url:  # Azure
                    headers["x-ms-blob-type"] = "BlockBlob"
                response = requests.put(pre_signed_url, data=fd, stream=True, headers=headers)
                response.raise_for_status()  # Raise an exception for HTTP errors
                if response.status_code == 200 or response.status_code == 201:
                    return
                else:
                    raise ModelException(f"File upload failed with status code: {response.status_code}")
            spinner.stop()
        except Exception as e:
            raise ModelException(f"Error uploading file: {e}")