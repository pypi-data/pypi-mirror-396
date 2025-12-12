import logging

from raga import TestSession, spinner
from raga.utils.dataset_util import wait_for_status

logger = logging.getLogger(__name__)

def inference_generator(test_session: TestSession,
                        dataset_name: str,
                        output_type: str,
                        model_name: str,
                        model_inference_col_name: str):
    
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2
    
    # validate dataset
    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(model_name, str) and model_name, f"{REQUIRED_ARG_V2.format('model_name', 'str')}"
    assert isinstance(model_inference_col_name, str) and model_inference_col_name, f"{REQUIRED_ARG_V2.format('model_inference_col_name', 'str')}"

    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})
    if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)
    
    dataset_id = res_data.get("data", {}).get("id")
    if not dataset_id:
          raise KeyError(INVALID_RESPONSE_DATA)
    
    payload = {
          "datasetId": dataset_id,
          "outputType": output_type,
          "model": model_name,
          "modelInferenceColName": model_inference_col_name,
    }

    post_url = f"api/experiment/test/inferenceGenerator"
    post_headers = {"Authorization": f'Bearer {test_session.token}'}
    res_data = test_session.http_client.post(post_url, data=payload, headers=post_headers)

    if not isinstance(res_data, dict):
        spinner.stop()
        raise ValueError(INVALID_RESPONSE)
    data = res_data.get('data')
    spinner.start()
    if isinstance(data, dict) and data.get('jobId', None):
        wait_for_status(test_session, data.get('jobId', None))
    spinner.stop()
    spinner.succeed("Succeed!")

    
