import ast
import datetime
import json
import os
import sys
import time
import math
import tempfile

import requests
from typing import Optional
import pandas as pd
import logging
import zipfile
import boto3
import raga
from typing import Callable, Any
from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA


from raga.exception import RagaException
from raga.raga_schema import RagaSchema, ImageDetectionObject, ObjectDetection, PredictionSchemaElement, \
    ImageUriSchemaElement, AttributeSchemaElement, InferenceSchemaElement, StringElement, TimeStampElement, \
    TIFFSchemaElement, ImageEmbeddingSchemaElement, ImageEmbedding, Embedding, MistakeScoreSchemaElement, MistakeScore, \
    ImageClassificationElement, ImageClassificationSchemaElement, ParentSchemaElement, TimeOfCaptureSchemaElement
from raga.file_uploader import FileUploader
from raga.utils.dataset_util import create_csv_and_zip_from_data_frames, delete_files_of_data_chunks, upload_files
from raga.validators.dataset_validations import DatasetValidator
from raga.dataset_creds import DatasetCreds
from raga import TestSession, spinner, Filter

from raga.utils import (get_file_name, 
                        delete_files, 
                        upload_file, 
                        create_csv_and_zip_from_data_frame, 
                        data_frame_extractor, 
                        make_arg, 
                        on_upload_success, 
                        on_upload_failed, 
                        check_key_value_existence,
                        wait_for_status,
                        PollingException)


logger = logging.getLogger(__name__)


class DatasetException(RagaException):
    pass


class DATASET_TYPE:
    IMAGE = "image"
    VIDEO = "video"
    ROI = "roi"
    EVENT = "event"
    PROMPT = "prompt"
    STRUCTURED_DATA = "structured_data"


class Dataset:
    MAX_RETRIES = 6
    RETRY_DELAY = 1

    def __init__(
        self,
        test_session:TestSession,
        name: str,
        type:Optional[str]= None,
        data: (pd.DataFrame, str) = None,
        schema: Optional[RagaSchema] = None,
        creds: Optional[DatasetCreds] = None,
        parent_dataset: Optional[str] = "",
        format: Optional[str] = None,
        model_name: Optional[str] = None,
        inference_col_name: Optional[str] = None,
        embedding_col_name: Optional[str] = None,
        filter: Optional[Filter] = None,
        model_inference_col_name: Optional[str] = None,
        event_inference_col_name: Optional[str] = None,
        u_test: bool = False,
        temp:bool = False,
        init:bool = True
    ):
        spinner.start()
        self.test_session = test_session
        self.name = DatasetValidator.validate_name(name)
        self.creds = DatasetValidator.validate_creds(creds)
        self.type = type
        self.parent_dataset = parent_dataset
        self.filter = filter
        self.model_inference_col_name=model_inference_col_name
        self.event_inference_col_name = event_inference_col_name
        self.csv_file = f"experiment_{time.time_ns()}_{self.name}.csv"
        self.zip_file = f"experiment_{time.time_ns()}_{self.name}.zip"
        self.csv_files = []
        self.zip_files = []
        self.dataset_id = None
        self.temp = temp
        if not u_test and not model_inference_col_name:
            self.dataset_id = self.create_dataset()
            if self.creds and self.dataset_id:
                self.create_dataset_creds()

        self.dataset_file_id = None
        self.dataset_file_ids = []
        self.data_set_top_five_rows = {}
        self.raga_dataset = data
        self.raga_extracted_dataset = None
        self.raga_schema = schema
        self.dataset_schema_columns = None
        self.format = format
        self.model_name = model_name
        self.inference_col_name = inference_col_name
        self.embedding_col_name = embedding_col_name
        self.parent_dataset_id = self.parent_dataset_validation()
        if init:
            self.init()

    def init(self):
        from raga import EMPTY_DATA_FRAME, INVALID_DATA_ARG, INVALID_SCHEMA, EMPTY_TEMP_DATA_FRAME
        from raga.utils.dataset_util import ds_temp_get_set
        if self.temp:
            self.raga_dataset = ds_temp_get_set(self)
            if self.raga_dataset.empty:
                raise DatasetException(EMPTY_TEMP_DATA_FRAME)
            
        if isinstance(self.raga_dataset, str) and not self.model_inference_col_name:
            pass
        elif isinstance(self.raga_dataset, pd.DataFrame) and not self.model_inference_col_name:
            if self.raga_dataset.empty:
                raise DatasetException(EMPTY_DATA_FRAME)
                
            if self.raga_schema is None:
                raise DatasetException(INVALID_SCHEMA)
            
            if not isinstance(self.raga_schema, RagaSchema):
                raise DatasetException(INVALID_SCHEMA)
            
            self.dataset_schema_columns = self.raga_schema.columns
            self.raga_extracted_dataset = data_frame_extractor(self.raga_dataset)
        elif self.event_inference_col_name and self.model_inference_col_name:
            res_data = self.test_session.http_client.get(f"api/dataset?projectId={self.test_session.project_id}&name={self.name}", headers={"Authorization": f'Bearer {self.test_session.token}'})

            if not isinstance(res_data, dict):
                    raise ValueError(INVALID_RESPONSE)
            
            self.dataset_id = res_data.get("data", {}).get("id")

            if not self.dataset_id:
                raise KeyError(INVALID_RESPONSE_DATA)  
        else:
            raise DatasetException(INVALID_DATA_ARG)

    def load(self,  schema: Optional[RagaSchema] = None, org=None):
        self.type = DatasetValidator.validate_type(self.type)
        self.raga_schema = schema if schema else self.raga_schema
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                if self.format == "coco":
                    self.load_dataset_from_file()
                elif org=="lm" or org=="lm-v2" or org=="lm-img-v2":
                    self.load_data_frame_for_lm(org)
                else:
                    self.load_data_frame(org)
                    
                spinner.succeed("Data loaded successful!")
                spinner.succeed("Succeed!")
                break  # Exit the loop if initialization succeeds
            except requests.exceptions.RequestException as e:
                print(f"Network error occurred: {str(e)}")
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Retrying in {self.RETRY_DELAY} second(s)...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    spinner.fail("Fail!")
                spinner.stop()
            except PollingException as e:
                spinner.fail(str(e))
                break
    
    def load_data_frame_for_lm(self, org=None):
        """
        Loads the data frame, creates a CSV file, zips it, and uploads it to the server.
        """
        self.data_frame_validation()
        create_csv_and_zip_from_data_frame(self.raga_extracted_dataset, self.csv_file, self.zip_file)
        signed_upload_paths, file_paths = self.get_pre_signed_s3_url([self.zip_file])
        signed_upload_path = signed_upload_paths[0]
        file_path = file_paths[0]
        upload_file(
            signed_upload_path,
            self.zip_file,
            success_callback=on_upload_success,
            failure_callback=on_upload_failed,
        )
        delete_files(self.csv_file, self.zip_file)

        self.dataset_file_id = self.create_dataset_load_definition(file_path, "csv", self.raga_schema.columns)
        res_data = self.notify_server(org=org)
        data = res_data.get('data')
        if isinstance(data, dict) and data.get('jobId', None):
            spinner.start()            
            wait_for_status(self.test_session, data.get('jobId', None))            
            if org == "lm-v2":      
                spinner.start()        
                res_data = self.notify_server(org="lm-img-v2")
                data = res_data.get('data')
                if isinstance(data, dict) and data.get('jobId', None):
                    wait_for_status(self.test_session, data.get('jobId', None))
            spinner.stop()

    def calculate_number_of_chunks(self):
        sample_size = min(1000, self.raga_extracted_dataset.shape[0])
        random_rows = self.raga_extracted_dataset.sample(n=sample_size)
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, "1.csv")

        random_rows.to_csv(temp_file_path, index=False)
        file_size = os.path.getsize(temp_file_path)
        os.remove(temp_file_path)
        estimated_size = file_size * (self.raga_extracted_dataset.shape[0] / sample_size)
        size_of_one_row = estimated_size / self.raga_extracted_dataset.shape[0]
        max_rows_per_chunk = min(40000, int(1e9 / size_of_one_row))
        number_of_chunks = math.ceil(self.raga_extracted_dataset.shape[0] / max_rows_per_chunk)
        logger.debug(f"Estimated size of one row: {size_of_one_row}")
        logger.debug(f"Max rows per chunk: {max_rows_per_chunk}")
        logger.debug(f"Number of chunks: {number_of_chunks}")
        logger.debug(f"Estimated size of the dataset: {estimated_size}")

        return number_of_chunks, max_rows_per_chunk


    def break_into_chunks(self):
        # Estimate the average size of one row (in bytes)
        number_of_chunks, max_rows_per_chunk = self.calculate_number_of_chunks()
        data_chunks = []

        # Create chunks based on calculated rows per GB
        for i in range(0, self.raga_extracted_dataset.shape[0], max_rows_per_chunk):
            chunk = self.raga_extracted_dataset[i: min(i+max_rows_per_chunk, self.raga_extracted_dataset.shape[0])]
            data_chunks.append(chunk)

        csv_file_names = []
        zip_file_names = []  

        for i in range(len(data_chunks)):
            csv_file_name = f"{self.csv_file[:-4]}_{i}{self.csv_file[-4:]}"
            zip_file_name = f"{self.zip_file[:-4]}_{i}{self.zip_file[-4:]}"
            csv_file_names.append(csv_file_name)
            zip_file_names.append(zip_file_name)
            logger.debug(f"Data chunk {i} created")

        self.csv_files = csv_file_names
        self.zip_files = zip_file_names
        logger.debug(f"self.csv_files: {self.csv_files}")
        logger.debug(f"self.zip_files: {self.zip_files}")

        return data_chunks 



    def load_data_frame(self, org=None):
        """
        Loads the data frame, creates a CSV file, zips it, and uploads it to the server.
        """
        self.data_frame_validation()
        data_chunks = self.break_into_chunks()
        logger.debug(f"Data chunks created: {len(data_chunks)}")
        create_csv_and_zip_from_data_frames(data_chunks, self.csv_files, self.zip_files)
        signed_upload_paths, s3_file_paths = self.get_pre_signed_s3_url(self.zip_files)
        logger.debug(f"Signed upload paths: {signed_upload_paths}")
        logger.debug(f"S3 file paths: {s3_file_paths}")
        upload_files(signed_upload_paths, self.zip_files)
        delete_files_of_data_chunks(self.csv_files, self.zip_files)
        self.dataset_file_ids = self.create_dataset_load_definitions(s3_file_paths, "csv", self.raga_schema.columns)
        logger.debug(f"Dataset file IDs: {self.dataset_file_ids}")
        res_data = self.notify_server_data_chunks(org=org)
        data = res_data.get('data')
        if isinstance(data, dict) and data.get('jobId', None):
            spinner.start()            
            wait_for_status(self.test_session, data.get('jobId', None))

    def load_dataset_from_file(self):
        from raga import REQUIRED_ARG
        if not self.format:
            raise DatasetException(f"{REQUIRED_ARG.format('format')}")
        if not self.model_name:
            raise DatasetException(f"{REQUIRED_ARG.format('model_name')}")
        if not self.inference_col_name:
            raise DatasetException(f"{REQUIRED_ARG.format('inference_col_name')}")
            
        file_dir = os.path.dirname(self.raga_dataset)
        file_name_without_ext, file_extension, file_name = get_file_name(
            self.raga_dataset)
        zip_file_name = os.path.join(file_dir, file_name_without_ext + ".zip")
        with zipfile.ZipFile(zip_file_name, "w") as zip_file:
            zip_file.write(self.raga_dataset, file_name)
        signed_upload_paths, file_paths  = self.get_pre_signed_s3_url(
            [file_name_without_ext + ".zip"])
        signed_upload_path = signed_upload_paths[0]
        file_path = file_paths[0]
        upload_file(
            signed_upload_path,
            zip_file_name,
            success_callback=on_upload_success,
            failure_callback=on_upload_failed,
        )
        if os.path.exists(zip_file_name):
            os.remove(zip_file_name)
            logger.debug("Zip file deleted")
        else:
            logger.debug("Zip file not found")

        arguments = make_arg(self.model_name, self.inference_col_name, self.embedding_col_name)

        self.dataset_file_id = self.create_dataset_load_definition(file_path, self.format, arguments)
        self.notify_server()
    

    def lightmetrics_data_upload(self, api_version="v1"):
        if api_version == "v1":
            self.load(org="lm")
        else:
            self.load(org="lm-v2")


    def head(self):
        res_data = self.test_session.http_client.post(
            f"api/dataset/data",
            headers={"Authorization": f'Bearer {self.test_session.token}'},
            data={
                "datasetId":self.dataset_id
            }
        )
        if not res_data or 'data' not in res_data or 'rows' not in res_data['data'] or 'columns' not in res_data['data']:
            raise DatasetException("Record not found!")
        
        
        print(self.filter_head(res_data.get('data', {}).get('rows', {}).get('docs', []), res_data.get('data', {}).get('columns', {})))

    def filter_head(self, rows, columns):
        pd_data = pd.DataFrame(rows)
        columns_temp = [col.get("columnName") for col in columns]
        existing_columns = [col for col in columns_temp if col in pd_data.columns]
        return pd_data[existing_columns]

    def get_pre_signed_s3_url(self, file_names):
        try:
            res_data = self.test_session.http_client.post(
                f"api/dataset/upload/preSignedUrls",
                {"datasetId": self.dataset_id, "fileNames": file_names, "contentType": "application/zip"},
                {"Authorization": f'Bearer {self.test_session.token}'},
            )
            if res_data.get("data") and "urls" in res_data["data"] and "filePaths" in res_data["data"]:
                logger.debug("Pre-signed URL generated")
                return res_data["data"]["urls"], res_data["data"]["filePaths"]
            else:
                error_message = "Failed to get pre-signed URL. Required keys not found in the response."
                logger.error(error_message)
                raise ValueError(error_message)
        except Exception as e:
            logger.exception("An error occurred while getting pre-signed URL: %s", e)
            raise

    def notify_server(self, org=None) -> dict:
        """
        Notifies the server to load the dataset with the provided experiment ID and data definition.
        """
        spinner.start()
        end_point = "api/experiment/load-data"
        if org=="lm":
            end_point = "api/experiment/load-data-lm"
        if org=="lm-v2":
            end_point = "api/experiment/load-data-lm/v2"
        if org=="lm-img-v2":
            end_point = "api/experiment/load-image-data-lm"
            
        res_data = self.test_session.http_client.post(
            end_point,
            {"datasetFileId": self.dataset_file_id},
            {"Authorization": f'Bearer {self.test_session.token}'},
        )
        logger.debug(res_data.get('data', ''))
        return res_data

    def notify_server_data_chunks(self, org=None) -> dict:
        """
        Notifies the server to load the dataset with the provided experiment ID and data definition.
        """
        spinner.start()
        end_point = "api/experiment/load-data"
        res_data = self.test_session.http_client.post(
            end_point,
            {"datasetFileIds": self.dataset_file_ids},
            {"Authorization": f'Bearer {self.test_session.token}'},
        )
        logger.debug(res_data.get('data', ''))
        return res_data

    def create_dataset(self):
        if not self.test_session.project_id:
            raise DatasetException("Project ID is required.")
        if not self.test_session.token:
            raise DatasetException("Token is required.")

        res_data = self.test_session.http_client.post(
            "api/dataset",
            {"name": self.name,
             "projectId": self.test_session.project_id,
             "type": self.type,
             "parentDataset": self.parent_dataset},
            {"Authorization": f'Bearer {self.test_session.token}'},
        )

        if not res_data or 'data' not in res_data or 'id' not in res_data['data']:
            raise DatasetException("Failed to create dataset.")

        return res_data['data']['id']

    def create_dataset_creds(self,):
        if not self.dataset_id:
            raise DatasetException("Dataset ID is required.")
        if not self.test_session.token:
            raise DatasetException("Token is required.")

        data = {
            "datasetId": self.dataset_id,
            "storageService": "s3",
            "json": {'region': self.creds.region}
        }
        res_data = self.test_session.http_client.post(
            "api/dataset/credential",
            data,
            {"Authorization": f'Bearer {self.test_session.token}'},
        )

        if not res_data or 'data' not in res_data or 'id' not in res_data['data']:
            raise DatasetException("Failed to create dataset credentials.")

        return res_data['data']['id']
    
    def create_dataset_load_definition(self, filePath: str, type: str, arguments: dict):
        spinner.start()
        payload = {
            "datasetId": self.dataset_id,
            "filePath": filePath,
            "type": type,
            "arguments": arguments
        }

        res_data = self.test_session.http_client.post(
            "api/dataset/definition", payload,
            {"Authorization": f'Bearer {self.test_session.token}'},
        )
        return res_data.get('data',{}).get('id')

    def create_dataset_load_definitions(self, filePaths, type: str, arguments: dict):
        res_data = []
        for filePath in filePaths:
            res_data.append(self.create_dataset_load_definition(filePath, type, arguments))
        return res_data

    def get_data_frame(self, columns:list):
        image_id_column = next((item['customerColumnName'] for item in self.raga_schema.columns if item['type'] == 'imageName'), None)
        if image_id_column not in columns:
            columns.append(image_id_column)
        
        missing_columns = [col for col in columns if col not in self.raga_extracted_dataset.columns]
        if not missing_columns:
            return self.raga_extracted_dataset[columns], image_id_column
        else:
            missing_columns_str = ', '.join(missing_columns)
            raise DatasetException(f"The following columns do not exist in the DataFrame: {missing_columns_str}")

    def set_data_frame(self, data_frame:pd.DataFrame):
        image_id_column = next((item['customerColumnName'] for item in self.raga_schema.columns if item['type'] == 'imageName'), None)
        merged_df = pd.merge(self.raga_extracted_dataset, data_frame, on=image_id_column, how='inner', suffixes=('', '_right'))
        self.raga_extracted_dataset = merged_df
        return self.raga_extracted_dataset
    
    def data_frame_validation(self):
        from raga.constants import SCHEMA_KEY_DOES_NOT_EXIST, COL_DOES_NOT_EXIST

        column_list = self.raga_extracted_dataset.columns.to_list()
        for col in self.raga_schema.columns:
            if col.get("customerColumnName") not in column_list:
                raise DatasetException(f"{COL_DOES_NOT_EXIST.format(col.get('customerColumnName'), column_list)}")
            # self.validate_data_frame_value(col, self.raga_extracted_dataset.loc[0,col.get("customerColumnName")])

        if not check_key_value_existence(self.raga_schema.columns, 'type', 'imageName'):
            raise DatasetException(SCHEMA_KEY_DOES_NOT_EXIST)
    
    def validate_data_frame_value(self, col, col_value):
        from raga.constants import DATASET_FORMAT_ERROR

        if col.get('type') == "classification" and "confidence" not in col_value:
                raise DatasetException(f"{DATASET_FORMAT_ERROR.format(col.get('customerColumnName'))}")
        
        if (col.get('type') == "imageEmbedding" or col.get('type') == "roiEmbedding") and "embeddings" not in col_value:
                raise DatasetException(f"{DATASET_FORMAT_ERROR.format(col.get('customerColumnName'))}")
        
        if col.get('type') == "inference" and "detections" not in col_value:
                raise DatasetException(f"{DATASET_FORMAT_ERROR.format(col.get('customerColumnName'))}")
        return 1
    
    def parent_dataset_validation(self):
        if self.parent_dataset:
            res_data = self.test_session.http_client.get(f"api/dataset?projectId={self.test_session.project_id}&name={self.parent_dataset}", headers={"Authorization": f'Bearer {self.test_session.token}'})

            if not isinstance(res_data, dict):
                    raise ValueError(INVALID_RESPONSE)
            dataset_id = res_data.get("data", {}).get("id")

            if not dataset_id:
                raise KeyError(INVALID_RESPONSE_DATA)
            return dataset_id
        return None

    def upload_file_to_s3(self, local_file_path, bucket_name, s3_key, s3):
        parts = s3_key.split('/')
        object_key = '/'.join(parts[-1:])
        try:
            s3.upload_file(local_file_path, bucket_name, s3_key)
        except Exception as e:
            print(f"Cannot upload file to s3, object:{object_key} : {e}")


    def upload_images_to_s3(self, s3, dataframe, column:str, s3_bucket_name:str, s3_key:str):
        for each_row in dataframe[column]:
            local_file_path = each_row
            parts = local_file_path.split('/')
            file_name = '/'.join(parts[-1:])
            s3_file_loc = f'{s3_key}/{file_name}'
            self.upload_file_to_s3(local_file_path, s3_bucket_name, s3_file_loc, s3)

    def __obj_embedding(self, x):
        Embeddings = ImageEmbedding()
        try:
            listEmb = eval(x)
            for emb in listEmb:
                Embeddings.add(Embedding(emb))
            return Embeddings
        except:
            x = '[]'
            listEmb = eval(x)
            for emb in listEmb:
                Embeddings.add(Embedding(emb))
            return Embeddings


    def __obj_mistake_scores(self, x):
        mistake_score = MistakeScore()
        try:
            x = ast.literal_eval(x)
            for key, value in x.items():
                if value.get('area'):
                    mistake_score.add(key=key, value=value.get("mistake_score"), area=value.get('area'))
                else:
                    mistake_score.add(key=key, value=value.get("mistake_score"), area=0)
            return mistake_score
        except:
            x = '{}'
            x = ast.literal_eval(x)
            for key, value in x.items():
                mistake_score.add(key=key, value=value, area=value)
            return mistake_score


    def add_embeddings(self, userDataFrame:pd.DataFrame, model:str, col_name:str):
        df = self.raga_dataset
        schema = self.raga_schema
        if "embedding" not in userDataFrame:
            print("Your dataframe doesn't have embedding column")
            sys.exit(1)
        if col_name in df.columns:
            df=df.drop(columns=[col_name], axis=1)
            new_schema_columns = [column for column in schema.columns if column.get("customerColumnName") != col_name]
            schema.columns = new_schema_columns
        merged_df = pd.DataFrame()
        if "imageId" in df.columns and "imageId" in userDataFrame.columns:
            if df['imageId'].dtype != userDataFrame['imageId'].dtype:
                userDataFrame['imageId'] = userDataFrame['imageId'].astype(df['imageId'].dtype)
            merged_df = pd.merge(df, userDataFrame, on='imageId', how='outer')
        if "imageId" not in df.columns:
            merged_df = pd.concat([df, userDataFrame], axis=1)
            schema.add("imageId", PredictionSchemaElement())
        merged_df[col_name] = merged_df["embedding"].apply(self.__obj_embedding)
        merged_df = merged_df.drop("embedding", axis=1)
        self.raga_dataset = merged_df
        schema.add(col_name, ImageEmbeddingSchemaElement(model=model))
        self.raga_schema = schema
        self.raga_extracted_dataset = data_frame_extractor(self.raga_dataset)


    def add_mistake_scores(self, userDataFrame:pd.DataFrame, col_name:str, refColName:str=""):
        df = self.raga_dataset
        schema = self.raga_schema
        if "mistake_score" not in userDataFrame:
            print("Your dataframe doesn't have mistake_score column")
            sys.exit(1)
        if col_name in df.columns:
            df=df.drop(columns=[col_name], axis=1)
            new_schema_columns = [column for column in schema.columns if column.get("customerColumnName") != col_name]
            schema.columns = new_schema_columns
        merged_df = pd.DataFrame()
        if "imageId" in df.columns and "imageId" in userDataFrame.columns:
            if df['imageId'].dtype != userDataFrame['imageId'].dtype:
                userDataFrame['imageId'] = userDataFrame['imageId'].astype(df['imageId'].dtype)
            merged_df = pd.merge(df, userDataFrame, on='imageId', how='outer')
        if "imageId" not in df.columns:
            merged_df = pd.concat([df, userDataFrame], axis=1)
            schema.add("imageId", PredictionSchemaElement())
        merged_df[col_name] = merged_df["mistake_score"].apply(self.__obj_mistake_scores)
        merged_df = merged_df.drop("mistake_score", axis=1)
        self.raga_dataset = merged_df
        schema.add(col_name, MistakeScoreSchemaElement(ref_col_name=refColName))
        self.raga_schema = schema
        self.raga_extracted_dataset = data_frame_extractor(self.raga_dataset)


    def validate_dataset(self):
        if self.name:
            res_data = self.test_session.http_client.get(f"api/dataset?projectId={self.test_session.project_id}&name={self.name}",
                                                         headers={"Authorization": f'Bearer {self.test_session.token}'})
            if not isinstance(res_data, dict):
                    raise ValueError(INVALID_RESPONSE)
            dataset_id = res_data.get("data", {}).get("id")

            if not dataset_id:
                raise KeyError(INVALID_RESPONSE_DATA)
            return dataset_id
        return None


    def run_model_executor(self, payload):
        post_url = f"api/model/executor"
        post_headers = {"Authorization": f'Bearer {self.test_session.token}'}
        res_data = self.test_session.http_client.post(post_url, data=payload, headers=post_headers)

        if not isinstance(res_data, dict):
            spinner.stop()
            raise ValueError(INVALID_RESPONSE)
        data = res_data.get('data')
        spinner.start()
        if isinstance(data, dict) and data.get('jobId', None):
            wait_for_status(self.test_session, data.get('jobId', None))
        spinner.stop()
        spinner.succeed("Succeed!")


    def generate_inferences(self, model_name: str,
                            model_version: str,
                            inference_col_name: str,
                            output_type: str,
                            input_func: Callable[[Any], Any],
                            output_func: Callable[[Any], Any]):
        dataset_id = self.validate_dataset()
        import inspect, base64
        input_func_string = inspect.getsource(input_func)
        output_func_string = inspect.getsource(output_func)
        input_func_base64 = base64.b64encode(input_func_string.encode()).decode()
        output_func_base64 = base64.b64encode(output_func_string.encode()).decode()

        payload = {
            "datasetId": dataset_id,
            "modelName": model_name,
            "modelVersion": model_version,
            "outputType": output_type,
            "executionType": "inferences",
            "customerColumnName": inference_col_name,
            "inputFunc": input_func_base64,
            "outputFunc":  output_func_base64,
        }
        self.run_model_executor(payload)

    def generate_embeddings(self, model_name: str,
                            model_version: str,
                            embed_col_name: str,
                            output_type: str,
                            input_func: Callable[[Any], Any] = None,
                            output_func: Callable[[Any], Any] = None):

        def input_function():
            pass

        def output_function():
            pass

        dataset_id = self.validate_dataset()
        import inspect, base64

        # Use the provided functions if given, otherwise use default functions
        input_func_to_use = input_func if input_func is not None else input_function
        output_func_to_use = output_func if output_func is not None else output_function

        input_func_string = inspect.getsource(input_func_to_use)
        output_func_string = inspect.getsource(output_func_to_use)
        input_func_base64 = base64.b64encode(input_func_string.encode()).decode()
        output_func_base64 = base64.b64encode(output_func_string.encode()).decode()

        payload = {
            "datasetId": dataset_id,
            "modelName": model_name,
            "modelVersion": model_version,
            "outputType": output_type,
            "executionType": "embeddings",
            "customerColumnName": embed_col_name,
            "inputFunc": input_func_base64,
            "outputFunc": output_func_base64,
        }
        self.run_model_executor(payload)

    def generate_mistake_score(self, model_name: str,
                            model_version: str,
                            mistake_score_col_name: str,
                            ref_cloumn_name: str,
                            output_type: str,
                            input_func: Callable[[Any], Any] = None,
                            output_func: Callable[[Any], Any] = None):
        def input_function():
            pass

        def output_function():
            pass

        dataset_id = self.validate_dataset()
        import inspect, base64

        # Use the provided functions if given, otherwise use default functions
        input_func_to_use = input_func if input_func is not None else input_function
        output_func_to_use = output_func if output_func is not None else output_function

        input_func_string = inspect.getsource(input_func_to_use)
        output_func_string = inspect.getsource(output_func_to_use)
        input_func_base64 = base64.b64encode(input_func_string.encode()).decode()
        output_func_base64 = base64.b64encode(output_func_string.encode()).decode()

        payload = {
            "datasetId": dataset_id,
            "modelName": model_name,
            "modelVersion": model_version,
            "outputType": output_type,
            "executionType": "mistake_score",
            "customerColumnName": mistake_score_col_name,
            "refColumnName": ref_cloumn_name,
            "inputFunc": input_func_base64,
            "outputFunc": output_func_base64,
        }
        self.run_model_executor(payload)

    def upload_assets(self, batch_size, local_dir, batch_workers=5, upload_workers=5, csv_path=None):
        csv_file_path = self._file_upload(batch_size, local_dir, batch_workers=batch_workers, upload_workers=upload_workers,
                                          csv_path=csv_path)
        self._set_pd_dataframe(csv_file_path)
        self._set_raga_schema()
        return self.raga_extracted_dataset, self.raga_schema

    def _file_upload(self, batch_size, local_dir, batch_workers, upload_workers, csv_path):
        file_uploader = FileUploader(self.dataset_id, self.test_session, batch_workers=batch_workers,
                                     upload_workers=upload_workers, csv_path=csv_path)
        try:
            print("starting upload process")
            successful, failed, skipped, csv_file_path = file_uploader.process_batches(batch_size=batch_size,
                                                                        local_directory=local_dir)
            print("completed upload process")
            # Additional operations if needed...
            print(f"Final results: {successful} successful, {failed} failed, {skipped} skipped")
            return csv_file_path
        finally:
            print("Shutting down executor")
            # Always shut down the executor, even if an exception occurs
            file_uploader.shutdown()

    def _set_pd_dataframe(self, csv_file):
        self.raga_dataset = self._csv_parser(csv_file)
        self.raga_extracted_dataset = data_frame_extractor(self.raga_dataset)

    def _set_raga_schema(self):
        self.raga_schema = self._get_raga_schema()

    def _csv_parser(self, csv_file):
        df = pd.read_csv(csv_file)
        data_frame = pd.DataFrame()
        data_frame["ImageId"] = df["ImageId"].apply(lambda x: StringElement(x))
        data_frame["ImageUri"] = df["ImageUri"]
        return data_frame

    def _get_raga_schema(self):
        schema = RagaSchema()
        schema.add("ImageId", PredictionSchemaElement())
        schema.add("ImageUri", ImageUriSchemaElement())
        return schema

class CocoDataset(Dataset):

    def __init__(self, test_session: TestSession, name: str, type: Optional[str],
                 json_file_path: str, image_folder_path:str, s3_bucket_name: str, s3_key: str, aws_raga_access_key: str, aws_raga_secret_key: str,
                 aws_session_token: Optional[str] = None, bucket_region : Optional[str] = None, inherited_class = None):
        if(type != "object_detection" and type!="keypoint_detection"):
            print("Invalid type entered, please try again with type=object_detection")
            sys.exit(1)
        self.s3_bucket_name = s3_bucket_name
        self.s3_key = s3_key
        self.json_file_path = json_file_path
        self.image_folder_path = image_folder_path
        self.aws_raga_access_key = aws_raga_access_key
        self.aws_raga_secret_key = aws_raga_secret_key
        self.aws_session_token = aws_session_token
        self.inference_file_path = None
        self.s3 = boto3.client('s3', aws_access_key_id=aws_raga_access_key, aws_secret_access_key=aws_raga_secret_key,
                          aws_session_token=aws_session_token if aws_session_token is not None else None)
        cred = None
        if bucket_region is not None :
            cred = DatasetCreds(region=bucket_region)
        if inherited_class is None:
            pd_data_frame = self.__json_parser(self.json_file_path)
            schema = self.__create_coco_schema()
            super(CocoDataset, self).__init__(test_session=test_session, name=name, type=DATASET_TYPE.IMAGE, data=pd_data_frame, schema=schema, creds=cred)


    def __map_imageId_row_to_annotation(self, grouped_annotations, df: pd.DataFrame, column_name):
        annotations_df_column = []
        for index in range(len(df["imageId"])):
            imageId = df["imageId"][index]
            width = df["width"][index]
            height = df["height"][index]
            annotations_object = ImageDetectionObject()
            if imageId in grouped_annotations:
                i=0
                for detection in grouped_annotations[imageId]:
                    if column_name == "annotations":
                        detection['id'] = str(detection['id'])
                        category_name = self.category_id_to_name_map[detection['category_id']]
                        annotations_object.add(ObjectDetection(Id=detection['id'], ClassId=detection['category_id'], ClassName=category_name, Format="xn,yn_normalised", Confidence=1.0,  BBox= self.normalized_bbox(detection['bbox'],  width, height)))
                    else:
                        class_name = self.category_id_to_name_map[int(eval(detection['Class_id']))]
                        annotations_object.add(ObjectDetection(Id=i, ClassId=detection["Class_id"], ClassName=class_name, Confidence=detection['Confidence'], BBox= self.normalized_bbox(detection['bbox'], width, height), Format="xn,yn_normalised"))
                        i = i+1
                annotations_df_column.append(annotations_object)
            else:
                annotations_df_column.append(annotations_object)
        df[column_name] = annotations_df_column
        return df[column_name]
    

    def normalized_bbox(self, bbox: list, width: int, height: int) -> list:
        for i in bbox:
            if i>1:
                return [
                    bbox[0] / width,
                    bbox[1] / height,
                    bbox[2] / width,
                    bbox[3] / height
                ]
        return bbox


    def get_timestamp_x_hours_ago(self, hours):
        current_time = datetime.datetime.now()
        delta = datetime.timedelta(days=90, hours=hours)
        past_time = current_time - delta
        timestamp = int(past_time.timestamp())
        return timestamp

    def get_annotations_by_imageId(self, row):
        grouped_annotations = {}
        annotations = row
        for annotation in annotations:
            image_id = annotation['image_id']
            if image_id not in grouped_annotations:
                grouped_annotations[image_id] = []
            grouped_annotations[image_id].append(annotation)
        return grouped_annotations


    def __create_inference_mapping(self, inferences_file_path):
        import glob
        path = inferences_file_path
        keys = ["Class_id", "x1", "y1", "x2", "y2", "Confidence"]
        row_dict = {}
        for files in glob.glob(path +"/*.txt"):
            filename = os.path.basename(files)
            imageId = os.path.splitext(filename)[0]
            imageId = int(imageId)
            file1 = open(files, 'r')
            lines = file1.readlines()
            row_list = []

            for line in lines:
                values = line.strip().split(',')
                line_dict = dict(zip(keys, values))
                line_dict["Bbox"] = [line_dict["x1"], line_dict["y1"], line_dict["x2"], line_dict["y2"]]
                row_list.append(line_dict)

            row_dict[imageId]=row_list

            file1.close()
        return row_dict

    def create_category_id_to_name_map(self, category_list):
        self.category_id_to_name_map = {}
        for category_dict in category_list:
            self.category_id_to_name_map[category_dict["id"]] = category_dict["name"]
        return self.category_id_to_name_map

    def create_s3_url(self):
        return f"https://{self.s3_bucket_name}.s3.amazonaws.com/{self.s3_key}"


    def make_url(self, imageUri):
        parts = imageUri.split('/')
        imageName = '/'.join(parts[-1:])
        s3_url = self.create_s3_url()
        return f"{s3_url}/{imageName}"


    def __json_parser(self, json_file):
        with open(json_file, 'r') as f:
            coco_data = json.load(f)
        df = pd.DataFrame()
        df_images = pd.DataFrame(coco_data["images"])
        category_list = coco_data["categories"]
        self.category_id_to_name_map = self.create_category_id_to_name_map(category_list)
        df["imageId"] = df_images["id"]
        df["imageUri"] = df_images["file_name"].apply(lambda x: f"{self.image_folder_path}/{x}")
        df["timeStamp"] = df.apply(lambda row: TimeStampElement(self.get_timestamp_x_hours_ago(row.name)), axis=1)
        df["width"] = df_images["width"]
        df["height"] = df_images["height"]
        grouped_annotations = self.get_annotations_by_imageId(coco_data["annotations"])
        df["annotations"] = self.__map_imageId_row_to_annotation(grouped_annotations, df, "annotations")
        return df


    def __create_coco_schema(self):
        schema = RagaSchema()
        schema.add("imageId", PredictionSchemaElement())
        schema.add("imageUri", ImageUriSchemaElement())
        schema.add("width", AttributeSchemaElement())
        schema.add("height", AttributeSchemaElement())
        schema.add("timeStamp", TimeOfCaptureSchemaElement())
        schema.add("annotations", InferenceSchemaElement(model="gt"))
        return schema


    def __add_inference_schema(self, customer_col_name, model_name):
        schema = self.raga_schema
        new_schema_columns = [column for column in schema.columns if column.get("customerColumnName") != customer_col_name]
        schema.columns = new_schema_columns
        schema.add(customer_col_name, InferenceSchemaElement(model = model_name))
        self.raga_schema = schema


    def __add_inference_column_to_dataframe(self, inferences_file_path, customer_column_name, format):
        df = self.raga_dataset
        if customer_column_name in df.columns:
            df=df.drop(columns=[customer_column_name], axis=1)
        inference_map = self.__create_inference_mapping(inferences_file_path)
        df[customer_column_name] = self.__map_imageId_row_to_annotation(inference_map, df, customer_column_name)
        self.customer_column_name = customer_column_name
        self.raga_dataset = df


    def add_inference(self, inferences_file_path, format, model_name, customer_column_name):
        if str.lower(format) != "yolov5":
            print(f"format {format} is not supported, please try again with format YOLOv5")
            sys.exit(1)
        self.inference_file_path = inferences_file_path
        self.__add_inference_column_to_dataframe(inferences_file_path, customer_column_name, format)
        self.__add_inference_schema(customer_column_name, model_name)

    def upload(self):
        if self.inference_file_path is None:
            print("Uploading images to s3")
            spinner.start()
            self.upload_images_to_s3(self.s3, self.raga_extracted_dataset, "imageUri", self.s3_bucket_name, self.s3_key)
            spinner.stop()
        self.raga_dataset["imageUri"] = self.raga_dataset["imageUri"].apply(lambda x: self.make_url(x))
        self.raga_extracted_dataset = data_frame_extractor(self.raga_dataset)
        self.load()


class SSDataset(Dataset):
    def __init__(self, test_session: TestSession, name: str, type: Optional[str],
                 annotation_file_path:str, image_folder_path:str, s3_bucket_name: str, images_s3_key: str, annotation_s3_key:str,
                 label_map:dict, aws_raga_access_key: str, aws_raga_secret_key: str,
                 aws_session_token: Optional[str] = None, bucket_region : Optional[str] = None):
        if(type != "semantic_segmentation"):
            print("Invalid type entered, please try again with type=semantic_segmentation")
            sys.exit(1)
        self.s3_bucket_name = s3_bucket_name
        self.images_s3_key = images_s3_key
        self.annotation_s3_key = annotation_s3_key
        self.annotation_file_path = annotation_file_path
        self.image_folder_path = image_folder_path
        self.label_map = label_map
        self.aws_raga_access_key = aws_raga_access_key
        self.aws_raga_secret_key = aws_raga_secret_key
        self.aws_session_token = aws_session_token
        self.inference_file_path = None
        self.inference_s3_key = None
        self.customer_column_name_to_s3_key_map = {}
        self.s3 = boto3.client('s3', aws_access_key_id=aws_raga_access_key, aws_secret_access_key=aws_raga_secret_key,
                               aws_session_token=aws_session_token if aws_session_token is not None else None)
        pd_data_frame = self.__make_df(self.image_folder_path)
        schema = self.__create_semantic_schema()
        cred = None
        if bucket_region is not None :
            cred = DatasetCreds(region=bucket_region)
        super(SSDataset, self).__init__(test_session=test_session, name=name, type=DATASET_TYPE.IMAGE, data=pd_data_frame, schema=schema, creds=cred)


    def get_timestamp_x_hours_ago(self, hours):
        current_time = datetime.datetime.now()
        delta = datetime.timedelta(days=90, hours=hours)
        past_time = current_time - delta
        timestamp = int(past_time.timestamp())
        return timestamp

    def __upload_annotations_to_s3(self, column_name, s3_key):
        self.upload_images_to_s3(self.s3, self.raga_extracted_dataset, column_name, self.s3_bucket_name, s3_key)

    def __create_s3_url(self, s3_key):
        return f"https://{self.s3_bucket_name}.s3.amazonaws.com/{s3_key}"


    def __make_s3_url(self, imageName, s3_key):
        s3_url = self.__create_s3_url(s3_key)
        return f"{s3_url}/{imageName}"


    def __make_local_url(self, local_file_path, x):
        local_url = f"{local_file_path}/{x}"
        return local_url


    def __make_df(self, file_path):
        data_frame = pd.DataFrame()
        id_list = []
        for file_name in os.listdir(file_path):
            id_list.append(file_name)
        data_frame["imageId"] = id_list
        data_frame["imageUri"] = data_frame["imageId"].apply(lambda x: self.__make_local_url(self.image_folder_path, x))
        data_frame["timeStamp"] = data_frame.apply(lambda row: TimeStampElement(self.get_timestamp_x_hours_ago(row.name)), axis=1)
        data_frame["annotations"] = data_frame["imageId"].apply(lambda x: self.__make_local_url(self.annotation_file_path, x))
        return data_frame


    def __create_semantic_schema(self):
        schema = RagaSchema()
        schema.add("imageId", PredictionSchemaElement())
        schema.add("imageUri", ImageUriSchemaElement())
        schema.add("timeStamp", TimeOfCaptureSchemaElement())
        schema.add("annotations", TIFFSchemaElement(label_mapping=self.label_map, schema="tiff"))
        return schema


    def __add_inference_column_to_dataframe(self, customer_column_name):
        df = self.raga_dataset
        if customer_column_name in df.columns:
            df=df.drop(columns=[customer_column_name], axis=1)
        self.customer_column_name = customer_column_name
        df[customer_column_name] = df["imageId"].apply(lambda x: self.__make_local_url(self.inference_file_path, x))
        self.raga_dataset = df
        self.raga_extracted_dataset = data_frame_extractor(self.raga_dataset)


    def __add_inference_schema(self, customer_col_name, model_name):
        schema = self.raga_schema
        new_schema_columns = [column for column in schema.columns if column.get("customerColumnName") != customer_col_name]
        schema.columns = new_schema_columns
        schema.add(customer_col_name, TIFFSchemaElement(label_mapping=self.label_map, schema="tiff", model=model_name))
        self.raga_schema = schema


    def add_inference(self, inferences_file_path, inference_s3_key, model_name, customer_column_name):
        self.inference_file_path = inferences_file_path
        self.inference_s3_key = inference_s3_key
        self.__add_inference_column_to_dataframe(customer_column_name)
        self.customer_column_name_to_s3_key_map[customer_column_name] = inference_s3_key
        self.__add_inference_schema(customer_column_name, model_name)

    def upload(self):
        if self.inference_file_path is None:
            print("Uploading images to s3")
            spinner.start()
            self.upload_images_to_s3(self.s3, self.raga_extracted_dataset, "imageUri", self.s3_bucket_name, self.images_s3_key)
            spinner.stop()
            print("Uploading annotations to s3")
            spinner.start()
            self.__upload_annotations_to_s3("annotations", self.annotation_s3_key)
            spinner.stop()
        else:
            for key, value in self.customer_column_name_to_s3_key_map.items():
                print("Uploading inferences to s3")
                spinner.start()
                self.__upload_annotations_to_s3(key, value)
                spinner.stop()
                self.raga_dataset[key] = self.raga_dataset["imageId"].apply(lambda x: self.__make_s3_url(x, value))
        self.raga_dataset["imageUri"] = self.raga_dataset["imageId"].apply(lambda x: self.__make_s3_url(x, self.images_s3_key))
        self.raga_dataset["annotations"] = self.raga_dataset["imageId"].apply(lambda x: self.__make_s3_url(x, self.annotation_s3_key))
        self.raga_extracted_dataset = data_frame_extractor(self.raga_dataset)
        self.load()


class ODDataset(Dataset):

    def __init__(self, test_session: TestSession, name: str, type: Optional[str],
                 json_file_path: str, image_folder_path:str, model_name:str, s3_bucket_name: str, s3_key: str, aws_raga_access_key: str, aws_raga_secret_key: str,
                 aws_session_token: Optional[str] = None, bucket_region : Optional[str] = None):
        self.model_name = model_name
        self.json_file_path = json_file_path
        self.image_folder_path = image_folder_path
        self.coco_obj = CocoDataset(test_session, name, type, json_file_path, image_folder_path, s3_bucket_name, s3_key, aws_raga_access_key, aws_raga_secret_key, aws_session_token, bucket_region, "od")
        self.pd_data_frame = self.__json_parser(self.json_file_path)
        schema = self.__create_od_schema()
        cred = None
        if bucket_region is not None :
            cred = DatasetCreds(region=bucket_region)
        super(ODDataset, self).__init__(test_session=test_session, name=name, type=DATASET_TYPE.IMAGE, data=self.pd_data_frame, schema=schema, creds=cred)


    def get_timestamp_x_hours_ago(self, hours):
        current_time = datetime.datetime.now()
        delta = datetime.timedelta(days=90, hours=hours)
        past_time = current_time - delta
        timestamp = int(past_time.timestamp())
        return timestamp

    def __map_imageId_row_to_annotation(self, grouped_annotations, df, column_name):
        annotations_df_column = []
        for imageId in df["imageId"]:
            annotations_object = ImageDetectionObject()
            if imageId in grouped_annotations:
                for detection in grouped_annotations[imageId]:
                    category_name = self.category_id_to_name_map[detection['category_id']]
                    detection['id'] = str(detection['id'])
                    if column_name == "annotations":
                        annotations_object.add(ObjectDetection(Id=detection['id'], ClassId=detection['category_id'], ClassName=category_name, Format="xn,yn_normalised", Confidence=1.0,  BBox= detection['bbox']))
                    else:
                        annotations_object.add(ObjectDetection(Id=detection['id'], ClassId=detection['category_id'], ClassName=category_name, Format="xn,yn_normalised", Confidence=detection["confidence"],  BBox= detection['bbox']))
                annotations_df_column.append(annotations_object)
            else:
                annotations_df_column.append(annotations_object)
        df[column_name] = annotations_df_column
        return df[column_name]

    def get_timestamp_x_hours_ago(self, hours):
        current_time = datetime.datetime.now()
        delta = datetime.timedelta(days=90, hours=hours)
        past_time = current_time - delta
        timestamp = int(past_time.timestamp())
        return timestamp

    def __json_parser(self, json_file):
        with open(json_file, 'r') as f:
            coco_data = json.load(f)
        df = pd.DataFrame()
        df_images = pd.DataFrame(coco_data["images"])
        category_list = coco_data["categories"]
        self.category_id_to_name_map = self.coco_obj.create_category_id_to_name_map(category_list)
        df["imageId"] = df_images["id"]
        df["imageUri"] = df_images["file_name"].apply(lambda x: f"{self.image_folder_path}/{x}")
        df["timeStamp"] = df.apply(lambda row: TimeStampElement(self.get_timestamp_x_hours_ago(row.name)), axis=1)
        # df["width"] = df_images["width"]
        # df["height"] = df_images["height"]
        self.attribute_list = []
        for x in df_images.keys():
            if x.startswith("attribute"):
                customer_col_name = x.split(':')[-1]
                df[customer_col_name] = df_images[x]
                self.attribute_list.append(customer_col_name)
        if "annotations" in coco_data:
            grouped_annotations = self.coco_obj.get_annotations_by_imageId(coco_data["annotations"])
            df["annotations"] = self.__map_imageId_row_to_annotation(grouped_annotations, df, "annotations")
        if "inferences" in coco_data:
            grouped_inferences = self.coco_obj.get_annotations_by_imageId(coco_data["inferences"])
            df["model_inferences"] = self.__map_imageId_row_to_annotation(grouped_inferences, df, "inferences")
        return df


    def __create_od_schema(self):
        schema = RagaSchema()
        schema.add("imageId", PredictionSchemaElement())
        schema.add("imageUri", ImageUriSchemaElement())
        schema.add("timeStamp", TimeOfCaptureSchemaElement())
        # schema.add("width", AttributeSchemaElement())
        # schema.add("height", AttributeSchemaElement())
        if "annotations" in self.pd_data_frame:
            schema.add("annotations", InferenceSchemaElement(model="gt"))
        if "model_inferences" in self.pd_data_frame:
            schema.add("model_inferences", InferenceSchemaElement(model = self.model_name))
        for attribute_name in self.attribute_list:
            schema.add(attribute_name, AttributeSchemaElement())
        return schema

    def upload(self):
        print("Uploading images to s3")
        spinner.start()
        self.upload_images_to_s3(self.coco_obj.s3, self.raga_extracted_dataset, "imageUri", self.coco_obj.s3_bucket_name, self.coco_obj.s3_key)
        spinner.stop()
        self.raga_dataset["imageUri"] = self.raga_dataset["imageUri"].apply(lambda x: self.coco_obj.make_url(x))
        self.raga_extracted_dataset = data_frame_extractor(self.raga_dataset)
        self.load()


class ICDataset(Dataset):

    def __init__(self, test_session: TestSession, name: str, type: Optional[str],
                 json_file_path: str, image_folder_path:str, model_name:str, s3_bucket_name: str, s3_key: str, aws_raga_access_key: str, aws_raga_secret_key: str,
                 aws_session_token: Optional[str] = None, bucket_region : Optional[str] = None):
        if(type != "image_classification"):
            print("Invalid type entered, please try again with type=image_classification")
            sys.exit(1)
        self.model_name = model_name
        self.s3_bucket_name = s3_bucket_name
        self.s3_key = s3_key
        self.json_file_path = json_file_path
        self.image_folder_path = image_folder_path
        self.aws_raga_access_key = aws_raga_access_key
        self.aws_raga_secret_key = aws_raga_secret_key
        self.aws_session_token = aws_session_token
        self.s3 = boto3.client('s3', aws_access_key_id=aws_raga_access_key, aws_secret_access_key=aws_raga_secret_key,
                               aws_session_token=aws_session_token if aws_session_token is not None else None)
        self.pd_data_frame = self.__json_parser(self.json_file_path)
        schema = self.__create_ic_schema()
        cred = None
        if bucket_region is not None :
            cred = DatasetCreds(region=bucket_region)
        super(ICDataset, self).__init__(test_session=test_session, name=name, type=DATASET_TYPE.IMAGE, data=self.pd_data_frame, schema=schema, creds=cred)

    def get_timestamp_x_hours_ago(self, hours):
        current_time = datetime.datetime.now()
        delta = datetime.timedelta(days=90, hours=hours)
        past_time = current_time - delta
        timestamp = int(past_time.timestamp())
        return timestamp

    def __map_imageId_row_to_annotation(self, grouped_annotations, df, column_name):
        annotations_df_column = []
        for imageId in df["imageId"]:
            annotations_object = ImageClassificationElement()
            if imageId in grouped_annotations:
                for detection in grouped_annotations[imageId]:  # {'confidence' : {'bad':1}}
                    for confidence, value in detection.items():
                        for k, v in value.items():
                            annotations_object.add(k, v)
                annotations_df_column.append(annotations_object)
            else:
                annotations_df_column.append(annotations_object)
        df[column_name] = annotations_df_column
        return df[column_name]

    def __get_annotations_by_imageId(self, row):
        grouped_annotations = {}
        annotations = row
        for annotation in annotations:
            image_id = annotation['image_id']
            if image_id not in grouped_annotations:
                grouped_annotations[image_id] = []
            grouped_annotations[image_id].append(annotation['annotation'])
        return grouped_annotations

    def __create_s3_url(self):
        return f"https://{self.s3_bucket_name}.s3.amazonaws.com/{self.s3_key}"
    #
    #
    def __make_url(self, imageUri):
        parts = imageUri.split('/')
        imageName = '/'.join(parts[-1:])
        s3_url = self.__create_s3_url()
        return f"{s3_url}/{imageName}"

    def __annotation_v1(self, row):
        annotations = row["annotation"]
        classification = ImageClassificationElement()
        for annotation in annotations:
            for key, value in annotation.items():
                try:
                    classification.add(key, value)
                except Exception as exc:
                    classification.add(key, 0)
            return classification


    def __json_parser(self, json_file):
        with open(json_file, 'r') as f:
            coco_data = json.load(f)
        df = pd.DataFrame()
        df_images = pd.DataFrame(coco_data["images"])
        df["imageId"] = df_images["id"]
        df["imageUri"] = df_images["file_name"].apply(lambda x: f"{self.image_folder_path}/{x}")
        df["timeStamp"] = df.apply(lambda row: TimeStampElement(self.get_timestamp_x_hours_ago(row.name)), axis=1)
        # df["width"] = df_images["width"]
        # df["height"] = df_images["height"]
        self.attribute_list = []
        for x in df_images.keys():
            if x.startswith("attribute"):
                customer_col_name = x.split(':')[-1]
                df[customer_col_name] = df_images[x]
                self.attribute_list.append(customer_col_name)
        if "annotations" in coco_data:
            grouped_annotations = self.__get_annotations_by_imageId(coco_data["annotations"])
            df["annotations"] = self.__map_imageId_row_to_annotation(grouped_annotations, df, "annotations")
        if "inferences" in coco_data:
            grouped_inferences = self.__get_annotations_by_imageId(coco_data["inferences"])
            df["model_inferences"] = self.__map_imageId_row_to_annotation(grouped_inferences, df, "inferences")
        return df


    def __create_ic_schema(self):
        schema = RagaSchema()
        schema.add("imageId", PredictionSchemaElement())
        schema.add("imageUri", ImageUriSchemaElement())
        schema.add("timeStamp", TimeOfCaptureSchemaElement())
        # schema.add("width", AttributeSchemaElement())
        # schema.add("height", AttributeSchemaElement())
        if "annotations" in self.pd_data_frame:
            schema.add("annotations", ImageClassificationSchemaElement(model="gt"))
        if "model_inferences" in self.pd_data_frame :
            schema.add("model_inferences", ImageClassificationSchemaElement(model = self.model_name))
        for attribute_name in self.attribute_list:
            schema.add(attribute_name, AttributeSchemaElement())
        return schema

    def upload(self):
        print("Uploading images to s3")
        spinner.start()
        self.upload_images_to_s3(self.s3, self.raga_extracted_dataset, "imageUri", self.s3_bucket_name, self.s3_key)
        spinner.stop()
        self.raga_dataset["imageUri"] = self.raga_dataset["imageUri"].apply(lambda x: self.__make_url(x))
        self.raga_extracted_dataset = data_frame_extractor(self.raga_dataset)
        self.load()


class KDataset(Dataset):

    def __init__(self, test_session: TestSession, name: str, type: Optional[str],
                 json_file_path: str, label_map:Optional[dict] = None,
                 skeleton_map:Optional[dict] = None, s3_bucket_name: Optional[str] = None,
                 s3_key: Optional[str] = None, aws_raga_access_key: Optional[str] = None, aws_raga_secret_key: Optional[str] = None,
                 aws_session_token: Optional[str] = None, parent_dataset_name:Optional[str]=None,
                 image_folder_path:Optional[str]=None, bucket_region : Optional[str] = None,
                 model_name: Optional[str]=None, gt_name: Optional[str]=None):
        self.json_file_path = json_file_path
        self.image_folder_path = image_folder_path
        self.label_map = label_map
        self.skeleton_map = skeleton_map
        self.s3_bucket_name = s3_bucket_name
        self.s3_key = s3_key
        self.model_name = model_name
        self.gt_name = gt_name
        self.pd_data_frame = self.__json_parser(self.json_file_path)

        schema = self.__create_kd_schema()
        cred = None
        self.s3 = boto3.client('s3', aws_access_key_id=aws_raga_access_key, aws_secret_access_key=aws_raga_secret_key,
                               aws_session_token=aws_session_token if aws_session_token is not None else None)
        if bucket_region is not None :
            cred = DatasetCreds(region=bucket_region)
        super(KDataset, self).__init__(test_session=test_session, name=name, type=DATASET_TYPE.IMAGE, data=self.pd_data_frame, schema=schema, parent_dataset=parent_dataset_name, creds=cred)


    def get_timestamp_x_hours_ago(self, hours):
        current_time = datetime.datetime.now()
        delta = datetime.timedelta(days=90, hours=hours)
        past_time = current_time - delta
        timestamp = int(past_time.timestamp())
        return timestamp

    def __map_imageId_row_to_annotation(self, grouped_annotations, df, column_name):
        annotations_df_column = []
        for imageId in df["imageId"]:
            annotations_object = ImageDetectionObject()
            if imageId in grouped_annotations:
                for detection in grouped_annotations[imageId]:
                    detection['id'] = str(detection['id'])
                    category_name = self.category_id_to_name_map[detection['category_id']]
                    annotations_object.add(ObjectDetection(Id=detection['id'], ClassId=detection['category_id'], ClassName=category_name, Format=detection['format'], Confidence=detection["confidence"],  BBox=self.normalized_bbox(detection['bbox'],  detection['width'], detection['height'])))
                annotations_df_column.append(annotations_object)
            else:
                annotations_df_column.append(annotations_object)
        df[column_name] = annotations_df_column
        return df[column_name]

    def __json_parser(self, json_file):
        with open(json_file, 'r') as f:
            coco_data = json.load(f)
        df = pd.DataFrame()
        df_images = pd.DataFrame(coco_data["images"])
        category_list = coco_data["categories"]
        self.category_id_to_name_map = self.create_category_id_to_name_map(category_list)
        df["imageId"] = df_images["id"]
        if self.image_folder_path is not None:
            df["imageUri"] = df_images["file_name"].apply(lambda x: f"{self.image_folder_path}/{x}")
        if "parent_id" in df_images:
            df["parentId"] = df_images["parent_id"]
        df["timeStamp"] = df.apply(lambda row: TimeStampElement(self.get_timestamp_x_hours_ago(row.name)), axis=1)

        # df["width"] = df_images["width"]
        # df["height"] = df_images["height"]
        self.attribute_list = []
        for x in df_images.keys():
            if x.startswith("attribute"):
                customer_col_name = x.split(':')[-1]
                df[customer_col_name] = df_images[x]
                self.attribute_list.append(customer_col_name)
        if "annotations" in coco_data:
            grouped_annotations = self.get_annotations_by_imageId(coco_data["annotations"])
            df["annotations"] = self.__map_imageId_row_to_annotation(grouped_annotations, df, "annotations")
        if "inferences" in coco_data:
            grouped_inferences = self.get_annotations_by_imageId(coco_data["inferences"])
            df["model_inferences"] = self.__map_imageId_row_to_annotation(grouped_inferences, df, "inferences")
        return df

    def __create_kd_schema(self):
        schema = RagaSchema()
        schema.add("imageId", PredictionSchemaElement())
        if self.image_folder_path is not None:
            schema.add("imageUri", ImageUriSchemaElement())
        # schema.add("width", AttributeSchemaElement())
        # schema.add("height", AttributeSchemaElement())
        if "parentId" in self.pd_data_frame.columns:
            schema.add("parentId", ParentSchemaElement())
        if "annotations" in self.pd_data_frame:
            schema.add("annotations", InferenceSchemaElement(model=self.gt_name, label_mapping=self.label_map, skeleton_mapping=self.skeleton_map))
        if "inferences" in self.pd_data_frame:
            schema.add("model_inferences", InferenceSchemaElement(model=self.model_name))
        schema.add("timeStamp", TimeOfCaptureSchemaElement())
        for attribute_name in self.attribute_list:
            schema.add(attribute_name, AttributeSchemaElement())
        return schema

    def create_category_id_to_name_map(self, category_list):
        self.category_id_to_name_map = {}
        for category_dict in category_list:
            self.category_id_to_name_map[category_dict["id"]] = category_dict["name"]
        return self.category_id_to_name_map

    def get_annotations_by_imageId(self, row):
        grouped_annotations = {}
        annotations = row
        for annotation in annotations:
            image_id = annotation['image_id']
            if image_id not in grouped_annotations:
                grouped_annotations[image_id] = []
            grouped_annotations[image_id].append(annotation)
        return grouped_annotations

    def normalized_bbox(self, bbox: list, width: int, height: int) -> list:
        """
        Normalize a bounding box list, assuming the format [x, y, z, ...] repeated.
        Each triplet is interpreted as (x, y, z) where x and y are normalized if >1.

        :param bbox: List of bounding box values, grouped as [x1, y1, z1, x2, y2, z2, ...].
        :param width: Width of the image.
        :param height: Height of the image.
        :return: Normalized list of bounding box values.
        """
        normalized = []
        for i in range(0, len(bbox), 3):
            # Normalize x and y if they are > 1
            x = bbox[i] / width if bbox[i] > 1 else bbox[i]
            y = bbox[i + 1] / height if bbox[i + 1] > 1 else bbox[i + 1]
            # Keep z unchanged, as z will be 1
            z = bbox[i + 2]
            normalized.extend([x, y, z])
        return normalized

    def make_url(self, imageUri):
        parts = imageUri.split('/')
        imageName = '/'.join(parts[-1:])
        s3_url = self.create_s3_url()
        return f"{s3_url}/{imageName}"

    def create_s3_url(self):
        return f"https://{self.s3_bucket_name}.s3.amazonaws.com/{self.s3_key}"

    def upload(self):
        if self.s3_bucket_name is not None:
            print("Uploading images to s3")
            spinner.start()
            self.upload_images_to_s3(self.s3, self.raga_extracted_dataset, "imageUri", self.s3_bucket_name, self.s3_key)
            spinner.stop()
            self.raga_dataset["imageUri"] = self.raga_dataset["imageUri"].apply(lambda x: self.make_url(x))
            self.raga_extracted_dataset = data_frame_extractor(self.raga_dataset)
        self.load()
