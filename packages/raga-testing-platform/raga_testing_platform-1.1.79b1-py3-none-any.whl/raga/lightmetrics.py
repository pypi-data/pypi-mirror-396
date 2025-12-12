import json
import logging
import os
import pathlib
import zipfile

from raga import Filter, TestSession, spinner
from raga.utils.dataset_util import upload_file, wait_for_status

logger = logging.getLogger(__name__)


def lightmetrics_inference_generator(test_session: TestSession, dataset_name: str, model_name: str,
                                     model_inference_col_name: str, event_inference_col_name: str,
                                     filter:Filter, model_param_mapping: dict):
    from raga.constants import (INVALID_RESPONSE, INVALID_RESPONSE_DATA,
                                REQUIRED_ARG_V2)
    dataset_id = lightmetrics_inference_generator_validation(test_session, dataset_name, model_name,
                                                             model_inference_col_name, event_inference_col_name, filter)
    payload = {
            "datasetId": dataset_id,
            "projectId": test_session.project_id,
            "model": model_name,
            "modelInferenceColName": model_inference_col_name,
            "eventInferenceColName": event_inference_col_name,
            "filter": filter.get(),
            "modelParamMapping": model_param_mapping
        }
    res_data = test_session.http_client.post(f"api/experiment/test/lm/inferenceGenerator", data=payload, headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        spinner.stop()
        raise ValueError(INVALID_RESPONSE)
    data = res_data.get('data')
    spinner.start()
    if isinstance(data, dict) and data.get('jobId', None):
        wait_for_status(test_session, data.get('jobId', None))
    spinner.stop()
    spinner.succeed("Succeed!")


def lightmetrics_inference_generator_validation(test_session:TestSession, dataset_name:str, model_name:str, model_inference_col_name:str, event_inference_col_name:str, filter:Filter):
    from raga.constants import (INVALID_RESPONSE, INVALID_RESPONSE_DATA,
                                REQUIRED_ARG_V2)

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)
    
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    assert isinstance(model_name, str) and model_name, f"{REQUIRED_ARG_V2.format('model_name', 'str')}"
    assert isinstance(model_inference_col_name, str) and model_inference_col_name, f"{REQUIRED_ARG_V2.format('model_inference_col_name', 'str')}"
    assert isinstance(event_inference_col_name, str) and event_inference_col_name, f"{REQUIRED_ARG_V2.format('event_inference_col_name', 'str')}"
    assert isinstance(filter, Filter) and filter, f"{REQUIRED_ARG_V2.format('filter', 'instance of the Filter')}"
    return dataset_id


def lightmetrics_model_upload(test_session: TestSession, file_path: str, name: str, version: str,  events, model_params,
                              description: str, api_version="v1"):
    if api_version == "v2":
        lightmetrics_model_upload_v2(test_session, file_path, name, events, model_params, description, version)
    else:
        lightmetrics_model_upload_v1(test_session, file_path, name, version)


def lightmetrics_model_upload_v1(test_session: TestSession, file_path: str, name: str, version: str,
                              override: bool = True):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2
    assert isinstance(file_path, str) and file_path, f"{REQUIRED_ARG_V2.format('file_path', 'str')}"
    assert isinstance(name, str) and name, f"{REQUIRED_ARG_V2.format('name', 'str')}"
    assert isinstance(version, str) and version, f"{REQUIRED_ARG_V2.format('version', 'str')}"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist.")
    if not file_path.lower().endswith(".zip"):
        raise TypeError("File mush be zip")
    model_zip_validation(file_path, name)

    payload = {
        "projectId": test_session.project_id,
        "modelName": name,
        "modelVersion": version
    }

    res_data = test_session.http_client.post(f"api/model-upload", data=payload,
                                             headers={"Authorization": f'Bearer {test_session.token}'}, file=file_path)

    if not isinstance(res_data, dict):
        spinner.stop()
        raise ValueError(INVALID_RESPONSE)
    spinner.stop()


def lightmetrics_model_upload_v2(test_session: TestSession, file_path: str, name: str, events, model_params,
                                 description: str, version: str):
    from raga.constants import (INVALID_RESPONSE, INVALID_RESPONSE_DATA,
                                REQUIRED_ARG_V2)
    assert isinstance(file_path, str) and file_path, f"{REQUIRED_ARG_V2.format('file_path', 'str')}"
    assert isinstance(name, str) and name, f"{REQUIRED_ARG_V2.format('name', 'str')}"
    assert isinstance(version, str) and version, f"{REQUIRED_ARG_V2.format('version', 'str')}"
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist.")
    if not file_path.lower().endswith(".zip"):
        raise TypeError("File mush be zip")
    model_zip_validation(file_path, name)
    
    payload = {
            "file": pathlib.Path(file_path).name,
            "projectId": test_session.project_id,
            "modelName": name,
            "modelVersion": version,
            "eventList": events,
            "modelParams": model_params,
            "description": description
        }
    
    res_data = test_session.http_client.post(f"api/model-upload/v2", data=payload, headers={"Authorization": f'Bearer {test_session.token}'})
    if not isinstance(res_data, dict):
        spinner.stop()
        raise ValueError(INVALID_RESPONSE)
    else:
        if res_data.get('success') == True:
            data = res_data.get('data')
            model_upload_to_url(data.get("uploadPreSignedUrl"), file_path)
        else:
            raise ValueError('Failed to upload model')
    spinner.stop()


def model_upload_to_url(url: str, file: str):
    # TODO: add retry mechanism
    upload_file(url, file)


def model_zip_validation(path, model_name):
    with zipfile.ZipFile(path, "r") as zip_file:
        all_names = zip_file.namelist()
        directories = [name for name in all_names if name.endswith("/") and '/' in name]
        if directories:
            directories.sort(key=lambda x: x.count('/'))
            model_dir_name = directories[0].split('/')[0]
            if model_dir_name != model_name:
                raise ValueError(f"The model name provided does not correspond to the directory contained in the ZIP file.")
        else:
            raise FileNotFoundError(f"{path} is empty.")

        run_sh_path = f"{model_dir_name}/run.sh"
        if run_sh_path not in all_names:
            raise ValueError("The model directory does not contain run.sh file.")
        return 1
            