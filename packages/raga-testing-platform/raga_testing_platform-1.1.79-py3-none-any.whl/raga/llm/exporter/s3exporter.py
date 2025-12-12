import json
import re

import requests
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
import pandas as pd
from raga import *
from raga.llm.exporter import constants


class S3Exporter(SpanExporter):
    def __init__(self, test_session: TestSession):
        self.test_session = test_session
        self.trace_spans = dict()
        self.dataframe = pd.DataFrame()

    def export(self, spans):
        for span in spans:
            span_json = json.loads(span.to_json())
            trace_id = span_json.get(constants.CONTEXT).get(constants.TRACE_ID)

            if trace_id not in self.trace_spans:
                self.trace_spans[trace_id] = list()

            self.trace_spans[trace_id].append(span_json)

            if span_json[constants.PARENT_ID] is None:
                trace = self.trace_spans[trace_id]
                trace_uri = self.upload_to_s3(trace_id, trace)
                self.add_to_dataframe(trace_id, trace_uri, trace)
                del self.trace_spans[trace_id]

        return SpanExportResult.SUCCESS

    def add_to_dataframe(self, trace_id, trace_uri, trace):
        data = dict()
        data[constants.TRACE_ID] = trace_id
        data[constants.TRACE_URI] = trace_uri
        for span in trace:
            attributes = span[constants.ATTRIBUTES]
            if constants.OPEN_INFERENCE_SPAN_KIND in attributes and attributes[
                constants.OPEN_INFERENCE_SPAN_KIND] == constants.CHAIN:
                data[constants.PROMPT] = attributes[constants.INPUT_VALUE]
                data[constants.RESPONSE] = attributes[constants.OUTPUT_VALUE]
            elif constants.OPEN_INFERENCE_SPAN_KIND in attributes and attributes[
                constants.OPEN_INFERENCE_SPAN_KIND] == constants.RETRIEVER:
                data[constants.CONTEXT] = attributes[constants.OUTPUT_VALUE]
        trace_dataframe = pd.DataFrame(data, index=[0])
        self.dataframe = pd.concat([self.dataframe, trace_dataframe], ignore_index=True)

    def upload_to_s3(self, trace_id, trace):
        trace_uri, file_path = self.get_pre_signed_s3_url(trace_id)
        json_data = {constants.TRACE: trace}
        response = requests.put(trace_uri, data=json.dumps(json_data), headers={'Content-Type': constants.APPLICATION_JSON})
        if response.status_code == 200:
            print('Upload successful.')
        else:
            print(f'Upload failed with status code: {response.status_code}')
        trace_uri_component_list = trace_uri.split("?")
        if trace_uri_component_list:
            return trace_uri_component_list[0]
        else:
            return None

    def shutdown(self):
        pass

    def get_dataframe(self):
        return self.dataframe

    def get_pre_signed_s3_url(self, file_name: str):
        try:
            res_data = self.test_session.http_client.post(endpoint=f"{constants.GET_PRE_SIGNED_URL_API}",
                                                         data={"projectName": self.test_session.project_name, "fileNames": [f'{file_name}.json'], "contentType": constants.APPLICATION_JSON},
                                                         headers={"Authorization": f'Bearer {self.test_session.token}'}
                                                         )
            data = res_data.get(constants.DATA)
            if data and 'urls' in data and 'filePaths' in data:
                logger.debug("Pre-signed URL generated")
                return data['urls'][0], data['filePaths'][0]
            else:
                error_message = "Failed to get pre-signed URL. Required keys not found in the response."
                logger.error(error_message)
                raise ValueError(error_message)
        except Exception as e:
            logger.exception("An error occurred while getting pre-signed URL for trace id %s: %s", file_name, e)
