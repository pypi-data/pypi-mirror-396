
import logging
import os
import pandas as pd
import requests
import zipfile
from raga.raga_schema import StringElement, VideoDetectionObject
from raga import spinner
import tempfile
from typing import Optional
import time

from raga.exception import RagaException

logger = logging.getLogger(__name__)

class PollingException(RagaException):
    pass

class JobFailedException(RagaException):
    pass

class FileUploadError(Exception):
    pass

def check_key_value_existence(column_list, key, value):
    return any(column.get(key) == value for column in column_list)

def data_extractor_helper(element):
    if isinstance(element, (int, str, float)):
        return element
    else:
        return element.get()

def ds_temp_get_set(ds, action="get"):
    import pandas as pd
    temp_dir = tempfile.gettempdir()
    file_name = f"{ds.name}.csv"
    temp_csv_path = os.path.join(temp_dir, file_name)
    dataset = ds.raga_extracted_dataset
    if action == "set":
        dataset.to_csv(temp_csv_path, index=False)
        return dataset
    else:
        if os.path.exists(temp_csv_path):
            return pd.read_csv(temp_csv_path)
    logger.debug(f"TEMP Data file does not exist.")
    return pd.DataFrame()


def data_frame_extractor(test_df: pd.DataFrame):
    extracted_df = test_df.applymap(lambda element: data_extractor_helper(element))
    return extracted_df

def make_arg(model_name, inference_col_name, embedding_col_name):
    payload = [
        {"customerColumnName": "file_name", "type": "imageName", "modelName": "", "ref_col_name": ""},
        {"customerColumnName": "coco_url", "type": "imageUri", "modelName": "", "ref_col_name": ""},
        {"customerColumnName": "date_captured", "type": "timestamp", "modelName": "", "ref_col_name": ""},
        {"customerColumnName": f"{inference_col_name}_{model_name}", "type": "inference", "modelName": model_name, "ref_col_name": ""},
    ]
    if embedding_col_name:
        payload.append({"customerColumnName": f"{embedding_col_name}_{model_name}", "type": "imageEmbedding", "modelName": model_name, "ref_col_name": ""})
    return payload

def upload_files(pre_signed_urls, file_paths):
    for pre_signed_url, file_path in zip(pre_signed_urls, file_paths):
        upload_file(pre_signed_url, file_path, success_callback=on_upload_success,failure_callback=on_upload_failed,)
    
def upload_file(pre_signed_url, file_path, success_callback=None, failure_callback=None):
    """
    Uploads a file to the server using a pre-signed URL.

    Args:
        pre_signed_url (str): The pre-signed URL for uploading the file.
        file_path (str): The path of the file to be uploaded.
        success_callback (Optional[function]): The callback function to be called on successful upload.
        failure_callback (Optional[function]): The callback function to be called on upload failure.

    Raises:
        ValueError: If the pre-signed URL or file path is missing.
        FileUploadError: If there is an error uploading the file.
    """
    if not pre_signed_url:
        raise ValueError("Pre-signed URL is required.")
    if not file_path:
        raise ValueError("File path is required.")
    if not os.path.isfile(file_path):
        raise ValueError(f"Invalid file path: {file_path}.")
    logger.debug(f"UPLOADING {file_path}")
    spinner.text = "Uploading..."
    try:
        with open(file_path, "rb") as file:
            headers = {"Content-Type": "application/zip"}
            if "blob.core.windows.net" in pre_signed_url:  # Azure
                headers["x-ms-blob-type"] = "BlockBlob"
            response = requests.put(pre_signed_url, data=file, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            if response.status_code == 200 or response.status_code == 201:
                if success_callback:
                    success_callback()
                return True
            else:
                if failure_callback:
                    failure_callback(response.status_code)
                raise FileUploadError(f"File upload failed with status code: {response.status_code}")
    except requests.RequestException as e:
        if failure_callback:
            failure_callback(str(e))
        raise FileUploadError(f"Error uploading file: {e}")

def check_csv_file_size(csv_file):
    file_size_bytes = os.path.getsize(csv_file)
    file_size_gb = file_size_bytes / (1024**3)
    if file_size_gb > 5:
        error_message = f"The size of {csv_file} is greater than 5 GB."
        logger.error(error_message)
        raise ValueError(error_message)
        
def create_csv_and_zip_from_data_frames(data_chunks, csv_files, zip_files):
    for data_chunk, csv_file, zip_file, in zip(data_chunks, csv_files, zip_files):
        create_csv_and_zip_from_data_frame(data_chunk, csv_file, zip_file)


def delete_files_of_data_chunks(csv_files, zip_files):
    for csv_file, zip_file in zip(csv_files, zip_files):
        delete_files(csv_file, zip_file)

def create_csv_and_zip_from_data_frame(data_frame:pd.DataFrame, csv_file, zip_file):
        """
        Creates a CSV file from the data frame and compresses it into a zip file.
        """
        # Validate the CSV file path
        if not csv_file or not isinstance(csv_file, str):
            raise ValueError(
                "Invalid CSV file path. Please provide a valid file path.")

        # Save the DataFrame as a CSV file
        data_frame.to_csv(csv_file, index=False)
        # Validate the size of csv
        check_csv_file_size(csv_file)
        logger.debug("Data frame has been saved to CSV")

        # Create a zip file containing the CSV file
        with zipfile.ZipFile(zip_file, "w") as zip_file:
            zip_file.write(csv_file, os.path.basename(csv_file))

        logger.debug(f"CSV file has been zipped: {zip_file}")
        # print(f"CSV file has been zipped: {zip_file}")


def delete_files(csv_file, zip_file):
    """
    Deletes the CSV and zip files associated with the dataset.
    """
    if os.path.exists(csv_file):
        os.remove(csv_file)
        logger.debug("CSV file deleted")
    else:
        logger.debug("CSV file not found")
        raise FileNotFoundError("CSV file not found.")

    if os.path.exists(zip_file):
        os.remove(zip_file)
        logger.debug("Zip file deleted")
    else:
        logger.debug("Zip file not found")
        raise FileNotFoundError("Zip file not found.")
    return True

def on_upload_success():
    """
    Callback function to be called on successful file upload.
    """
    logger.debug("File uploaded successfully")
    spinner.succeed("File uploaded successfully")
    spinner.text = "Loading..."

def on_upload_failed(error):
    """
    Callback function to be called on file upload failure.
    """
    logger.debug(f"ERROR: {error}")
    print("File upload failed")
    
def wait_for_status(test_session, job_id: int, status: Optional[str]='In Progress', spin: Optional[bool]=False):
        # maximum time to wait for the job to complete
        MAX_DURATION = 15 * 60 # 15 minutes
        SLEEP_DURATION = 5 # wait for 5 seconds before polling again
        start_time = time.time()
        while time.time() - start_time < MAX_DURATION:
            res_data = test_session.http_client.post(
                'api/job/status',
                {"jobId": job_id},
                {"Authorization": f'Bearer {test_session.token}'},
                spin=spin
            )
            if res_data.get('data').get('status') != status:
                if res_data.get('data').get('status') == 'Failed':
                    raise JobFailedException("Job Failed")
                return
            else:
                time.sleep(SLEEP_DURATION)
        from raga import MAX_DURATION_EXCEEDED
        raise PollingException(MAX_DURATION_EXCEEDED)