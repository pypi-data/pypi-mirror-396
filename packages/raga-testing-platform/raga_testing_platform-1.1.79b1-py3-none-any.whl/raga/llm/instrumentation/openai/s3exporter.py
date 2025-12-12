from raga.llm.exporter.s3exporter import S3Exporter as BaseS3Exporter
from raga.llm.exporter import constants
import pandas as pd

class S3Exporter(BaseS3Exporter):
    def add_to_dataframe(self, trace_id, trace_uri, trace):
        data = dict()
        data[constants.TRACE_ID] = trace_id
        data[constants.TRACE_URI] = trace_uri
        for span in trace:
            attributes = span[constants.ATTRIBUTES]
            if constants.OPEN_INFERENCE_SPAN_KIND in attributes and attributes[
                    constants.OPEN_INFERENCE_SPAN_KIND] == 'LLM':
                data[constants.PROMPT] = attributes[constants.INPUT_VALUE]
                data[constants.RESPONSE] = attributes[constants.OUTPUT_VALUE]
            elif constants.OPEN_INFERENCE_SPAN_KIND in attributes and attributes[
                    constants.OPEN_INFERENCE_SPAN_KIND] == constants.RETRIEVER:
                data[constants.CONTEXT] = attributes[constants.OUTPUT_VALUE]
        trace_dataframe = pd.DataFrame(data, index=[0])
        self.dataframe = pd.concat(
            [self.dataframe, trace_dataframe], ignore_index=True)
