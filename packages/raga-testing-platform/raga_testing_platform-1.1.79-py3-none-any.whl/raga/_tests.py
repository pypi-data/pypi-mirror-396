import logging
import json
from typing import Optional
import time
import uuid


from raga import TestSession, ModelABTestRules, FMARules, LQRules, LDTRules, EventABTestRules, Filter, OcrRules, \
    OcrAnomalyRules, \
    DARules, FMA_LLMRules, ClassImbalanceRules, SBRules, IPDRules, LLMRules, LlmGuardrailTestRules, MCTRules, \
    EntropyRules, OutlierDetectionRules
from raga import STRules

def model_ab_test(test_session:TestSession,
                  dataset_name: str, 
                  test_name: str, 
                  modelA: str, 
                  modelB: str,
                  type: str, 
                  rules: ModelABTestRules, 
                  aggregation_level:  Optional[list] = [],
                  gt: Optional[str] = "", 
                  filter: Optional[str] = ""):
    dataset_id = ab_test_validation(test_session, dataset_name, test_name, modelA, modelB, type, rules, gt, aggregation_level)    
    return {
            "datasetId": dataset_id,
            "experimentId": test_session.experiment_id,
            "name": test_name,
            "modelA": modelA,
            "modelB": modelB,
            "type": type,
            "rules": rules.get(),
            "aggregationLevels": aggregation_level,
            'filter':filter,
            'gt':gt,
            'test_type':'ab_test'
        }

def event_ab_test(test_session:TestSession, 
                  dataset_name: str, 
                  test_name: str, 
                  modelA: str,                  
                  modelB: str,                  
                  object_detection_modelA: str,                
                  object_detection_modelB: str,                
                  type: str, 
                  sub_type:str,
                  rules: EventABTestRules, 
                  aggregation_level:  Optional[list] = [],
                  output_type:Optional[str] = "", 
                  filter: Optional[Filter] = None):
    dataset_id = ab_event_test_validation(test_session, dataset_name, test_name, modelA, modelB, type, sub_type, rules, object_detection_modelA, object_detection_modelB, aggregation_level)    
    payload = {
            "datasetId": dataset_id,
            "experimentId": test_session.experiment_id,
            "name": test_name,
            "modelA": modelA,
            "modelB": modelB,
            "objectDetectionModelA":object_detection_modelA,
            "objectDetectionModelB":object_detection_modelB,
            "type": type,
            "subType":sub_type,
            "rules": rules.get(),
            "aggregationLevels": aggregation_level,
            'filter':"",
            'outputType':output_type,
            'test_type':'event_ab_test'
        }
    if isinstance(filter, Filter):
         payload["filter"] = filter.get()
    return payload

def ab_event_test_validation(test_session:TestSession, 
                       dataset_name: str, 
                       test_name: str, 
                       modelA: str,                        
                       modelB:str,                        
                       type: str, 
                       sub_type: str,
                       rules: ModelABTestRules,    
                       object_detection_modelA: str,
                       object_detection_modelB: str,                  
                       aggregation_level:Optional[list] = []):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"

    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)
    
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    
    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(modelA, str) and modelA, f"{REQUIRED_ARG_V2.format('modelA', 'str')}"
    assert isinstance(modelB, str) and modelB, f"{REQUIRED_ARG_V2.format('modelB', 'str')}"
    assert isinstance(object_detection_modelA, str) and object_detection_modelA, f"{REQUIRED_ARG_V2.format('object_detection_modelA', 'str')}"
    assert isinstance(object_detection_modelB, str) and object_detection_modelB, f"{REQUIRED_ARG_V2.format('object_detection_modelB', 'str')}"
    assert isinstance(sub_type, str), f"{REQUIRED_ARG_V2.format('sub_type', 'str')}"
    assert isinstance(type, str), f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(rules, ModelABTestRules) and rules.get(), f"{REQUIRED_ARG_V2.format('rules', 'instance of the ModelABTestRules')}"

    if aggregation_level:
        assert isinstance(aggregation_level, list), f"{REQUIRED_ARG_V2.format('aggregation_level', 'str')}"

    return dataset_id
def ab_labelled_test_validation(test_session:TestSession,
                                dataset_name: str,
                                test_name: str,
                                modelAColumnName: str,
                                modelBColumnName: str,
                                type: str,
                                rules: MCTRules,
                                gtColumnName: Optional[str] = "",
                                aggregation_levels:Optional[list] = []):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"

    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)

    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)

    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(modelAColumnName, str) and modelAColumnName, f"{REQUIRED_ARG_V2.format('modelAColumnName', 'str')}"
    assert isinstance(modelBColumnName, str) and modelBColumnName, f"{REQUIRED_ARG_V2.format('modelBColumnName', 'str')}"
    assert isinstance(type, str), f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(rules, MCTRules) and rules.get(), f"{REQUIRED_ARG_V2.format('rules', 'instance of the MCTRules')}"
    
    if aggregation_levels:
        assert isinstance(aggregation_levels, list), f"{REQUIRED_ARG_V2.format('aggregation_levels', 'str')}"

    if type == "labelled":
        assert isinstance(gtColumnName, str) and gtColumnName, f"{REQUIRED_ARG_V2.format('gtColumnName', 'str')}"


    return dataset_id


def failure_mode_analysis_geospatial_validation(test_session: TestSession,
                                dataset_name: str,
                                test_name: str,
                                modelColumnName: str,
                                type: str,
                                rules: FMARules,
                                gtColumnName: str):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session,
                      TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"

    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}",
                                            headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)

    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)

    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(modelColumnName,
                      str), f"{REQUIRED_ARG_V2.format('modelColumnName', 'str')}"
    assert isinstance(gtColumnName,
                      str) , f"{REQUIRED_ARG_V2.format('gtColumnName', 'str')}"
    assert isinstance(type, str), f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(rules, FMARules) and rules.get(), f"{REQUIRED_ARG_V2.format('rules', 'instance of the FMArules')}"
    return dataset_id

def ab_test_validation(test_session:TestSession, 
                       dataset_name: str, 
                       test_name: str, 
                       modelA: str, 
                       modelB: str,
                       type: str, 
                       rules: ModelABTestRules,
                       gt: Optional[str] = "", 
                       aggregation_level:Optional[list] = []):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"

    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)
    
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    
    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(modelA, str) and modelA, f"{REQUIRED_ARG_V2.format('modelA', 'str')}"
    assert isinstance(modelB, str) and modelB, f"{REQUIRED_ARG_V2.format('modelB', 'str')}"
    assert isinstance(type, str), f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(rules, ModelABTestRules) and rules.get(), f"{REQUIRED_ARG_V2.format('rules', 'instance of the ModelABTestRules')}"

    if aggregation_level:
        assert isinstance(aggregation_level, list), f"{REQUIRED_ARG_V2.format('aggregation_level', 'str')}"

    if type == "labelled":
        assert isinstance(gt, str) and gt, f"{REQUIRED_ARG_V2.format('gt', 'str')}"

    if type == "unlabelled" and isinstance(gt, str) and gt:
        raise ValueError("gt is not required on unlabelled type.")
    
    return dataset_id

def failure_mode_analysis(test_session:TestSession, 
                          dataset_name:str, 
                          test_name:str, 
                          model:str, 
                          gt:str,
                          rules:FMARules,
                          output_type:str,
                          type:str,
                          clustering:Optional[dict]={},
                          aggregation_level:Optional[list]=[],
                          object_detection_model:Optional[str]="",
                          object_detection_gt:Optional[str]="",
                          embedding_col_name:Optional[str]="",
                          level:Optional[str]="",
                          ):
    
    dataset_id = failure_mode_analysis_validation(test_session=test_session, dataset_name=dataset_name, test_name=test_name, model=model, gt=gt, type=type, rules=rules, output_type=output_type, aggregation_level=aggregation_level, clustering=clustering)
    response = {
            "datasetId": dataset_id,
            "experimentId": test_session.experiment_id,
            "name": test_name,
            "model": model,
            "gt": gt,
            "type": type,
            "rules": rules.get(),
            "test_type":"cluster",
            "filter":"",
            "outputType":output_type,
            "aggregationLevels":aggregation_level,
            "level":level,
        }
    if output_type == "event_detection":
        response['objectDetectionModel'] = object_detection_model
        response['objectDetectionGT'] = object_detection_gt

    if output_type == "instance_segmentation" or output_type == "keypoint_detections":
        response['embeddingColName'] = embedding_col_name

    if clustering:
        response['clusterId'] = clustering
    return response


def ab_test(test_session: TestSession,
            dataset_name: str,
            test_name: str,
            modelAColumnName: str,
            modelBColumnName: str,
            rules: MCTRules,
            type: str,
            gtColumnName: str,
            outputType: str,
            subType: Optional[str]=None,
            clustering:Optional[dict]={},
            aggregation_levels: Optional[list] = [],
            embeddingColumnName: Optional[str] = None,
            labelMapping: Optional[dict] = None
            ):

    dataset_id = ab_labelled_test_validation(test_session=test_session, dataset_name=dataset_name, test_name=test_name,
                                             modelAColumnName=modelAColumnName, modelBColumnName=modelBColumnName, type=type,
                                             rules=rules, gtColumnName=gtColumnName,
                                             aggregation_levels=aggregation_levels)

    response = {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "modelAColumnName": modelAColumnName,
        "modelBColumnName": modelBColumnName,
        "subType": subType,
        "test_type":"ab",
        "type": type,
        "rules": rules.get(),
        "aggregationLevels": aggregation_levels,
        'gtColumnName': gtColumnName,
        'embeddingColumnName': embeddingColumnName,
        'outputType': outputType,
        'labelMapping':labelMapping
    }
    if clustering:
        response['clusterId'] = clustering
    return response

def failure_mode_analysis_geospatial(test_session: TestSession,
            dataset_name: str,
            test_name: str,
            modelColumnName: str,
            rules: FMARules,
            type: str,
            gtColumnName: str,
            outputType: str,
            subType: Optional[str]=None,
            clustering:Optional[dict]={},
            embeddingColumnName: Optional[str] = None,
            labelMapping: Optional[dict] = None,
            aggregation_levels: Optional[list] = [],
            primary_metadata: Optional[str]=None
            ):

    dataset_id = failure_mode_analysis_geospatial_validation(test_session=test_session, dataset_name=dataset_name, test_name=test_name,
                                             modelColumnName=modelColumnName, type=type,
                                             rules=rules, gtColumnName=gtColumnName)

    response = {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "modelColumnName": modelColumnName,
        "subType": subType,
        "test_type":"fma_semantic_geospatial",
        "type": type,
        "rules": rules.get(),
        'gtColumnName': gtColumnName,
        'embeddingColumnName': embeddingColumnName,
        'outputType': outputType,
        'labelMapping':labelMapping,
        "primaryMetaData":primary_metadata,
        "aggregationLevels": aggregation_levels,
    }
    if clustering:
        response['clusterId'] = clustering
    return response

def failure_mode_analysis_validation(test_session:TestSession, dataset_name:str, test_name:str, model:str, gt:str, rules:FMARules, output_type:str, type:str, aggregation_level:Optional[list]=[], clustering:Optional[dict]=None):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)
    
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(model, str) and model, f"{REQUIRED_ARG_V2.format('model', 'str')}"
    assert isinstance(gt, str) and gt, f"{REQUIRED_ARG_V2.format('gt', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(rules, FMARules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'instance of the FMARules')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"

    if output_type == "object_detection":
         if type == "embedding" and not clustering:
              raise ValueError(f"{REQUIRED_ARG_V2.format('clustering', 'clustering function')}")
         if type == "metadata":
            assert isinstance(aggregation_level, list) and aggregation_level, f"{REQUIRED_ARG_V2.format('aggregation_level', 'list')}"
    return dataset_id


def clustering(test_session: TestSession, dataset_name: str, method: str, embedding_col: str, level: str, args: dict,
               interpolation: bool = False, force: Optional[bool] = False, odd: Optional[bool] = False):
    from raga.constants import REQUIRED_ARG_V2

    assert isinstance(method, str) and method, f"{REQUIRED_ARG_V2.format('method', 'str')}"
    assert isinstance(embedding_col, str) and embedding_col, f"{REQUIRED_ARG_V2.format('embedding_col', 'str')}"
    assert isinstance(level, str) and level, f"{REQUIRED_ARG_V2.format('level', 'str')}"
    cluster = {
        "method": method,
        "embeddingCol": embedding_col,
        "level": level,
        "args": args,
        "interpolation": interpolation
    }
    if test_session is None and dataset_name is None:
        return cluster
    else:
        dataset_id = clustering_validation(test_session, dataset_name, odd)
        api_end_point = 'api/experiment/test/cluster'
        payload = {
            "datasetId": dataset_id,
            "forceRecreate": force,
            "clustering": cluster
        }
        from raga.constants import INVALID_RESPONSE
        from raga.utils import wait_for_status
        res_data = test_session.http_client.post(api_end_point, data=payload, headers={"Authorization": f'Bearer {test_session.token}'})
        data = res_data.get('data')
        job_id = data.get('jobId')
        if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)
        if job_id is not None:
            wait_for_status(test_session, job_id=job_id, spin=True)
        return data.get('clusterId')


def clustering_validation(test_session: TestSession, dataset_name: str, odd: Optional[bool] = False):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA
    if odd:
        res_Data = test_session.http_client.get(f"api/odds/getByName/{dataset_name}",
                                            headers={"Authorization": f'Bearer {test_session.token}'})
        dataset_name = res_Data.get("data", {}).get("oddDatasetName")

    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}",
                                            headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    return dataset_id

def labelling_quality_test(test_session:TestSession, 
                           dataset_name:str, 
                           test_name:str, 
                           type:str, 
                           output_type: str, 
                           rules:LQRules,
                           gt:Optional[str] = "",
                           model:Optional[str] = "",
                           mistake_score_col_name: Optional[str]="",
                           train_model_column_name: Optional[str]="",
                           field_model_column_name: Optional[str]="",
                           embedding_train_col_name: Optional[str]="",
                           embedding_field_col_name: Optional[str]="",
                           embedding_col_name:Optional[str]="",
                           level:Optional[str]=""):
    
    dataset_id = labelling_quality_test_validation(test_session, dataset_name, test_name, type, output_type, rules)
    payload = {
            "experimentId": test_session.experiment_id,
            "name": test_name,
            "type": type,
            "outputType": output_type,
            "rules": rules.get(),
            "filter":"",
        }
    
    if output_type == "instance_segmentation":
        payload["gt"] = gt
    
    if output_type == "object_detection":
        payload["model"] = model

    if output_type=="keypoint_detection":
        payload["gt"]=gt
        payload["model"] = model
        payload["level"]=level
        payload["mistakeScoreColName"]=mistake_score_col_name
        payload["embeddingColName"]=embedding_col_name
        payload["testName"]=test_name
        
    if train_model_column_name is not None and train_model_column_name != "" and embedding_field_col_name is not None and embedding_field_col_name != "":
        payload["trainDatasetId"]= dataset_id
        payload["fieldDatasetId"]= dataset_id
        payload["trainModelColumnName"] = train_model_column_name
        payload["fieldModelColumnName"] = field_model_column_name
        payload["embeddingTrainColName"] = embedding_train_col_name
        payload["embeddingFieldColName"] = embedding_field_col_name
        payload["test_type"] = "labelling_consistency"
    else:
        payload["datasetId"] = dataset_id
        payload["mistakeScoreColName"] = mistake_score_col_name
        payload["embeddingColName"] = embedding_col_name
        payload["test_type"] = "labelling_quality"
    
    return payload


def labelling_quality_test_validation(test_session:TestSession, dataset_name:str, test_name:str, type:str, output_type:str,  rules:LQRules):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    
    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(rules, LQRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'str')}"
    return dataset_id

def ocr_missing_test_analysis(test_session:TestSession,
                      dataset_name:str,
                      test_name:str,
                      model:str,
                      type:str,
                      output_type: str,
                      rules:OcrRules):

    dataset_id = ocr_missing_test_analysis_validation(test_session, dataset_name, test_name, model, type, output_type, rules)
    return {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "model":model,
        "type": type,
        "outputType": output_type,
        "rules": rules.get(),
        "test_type":"ocr_test"
    }

def ocr_missing_test_analysis_validation(test_session:TestSession, dataset_name:str, test_name:str, model:str, type:str, output_type:str, rules:OcrRules):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)

    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(model, str) and model, f"{REQUIRED_ARG_V2.format('model', 'str')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(rules, OcrRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'str')}"
    return dataset_id

def ocr_anomaly_test_analysis(test_session:TestSession,
                              dataset_name:str,
                              test_name:str,
                              model:str,
                              type:str,
                              output_type: str,
                              rules:OcrRules):

    dataset_id = ocr_anomaly_test_analysis_validation(test_session, dataset_name, test_name, model, type, output_type, rules)
    return {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "model":model,
        "type": type,
        "outputType": output_type,
        "rules": rules.get(),
        "test_type":"ocr_test"
    }

def ocr_anomaly_test_analysis_validation(test_session:TestSession, dataset_name:str, test_name:str, model:str, type:str, output_type:str, rules:OcrAnomalyRules):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)

    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(model, str) and model, f"{REQUIRED_ARG_V2.format('model', 'str')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(rules, OcrAnomalyRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'str')}"
    return dataset_id

def outlier_detection(test_session: TestSession,
                      dataset_name: str,
                      test_name: str,
                      type: str,
                      output_type: str,
                      embedding: str,
                      rules: OutlierDetectionRules):
    dataset_id = outlier_detection_test_analysis_validation(test_session, dataset_name, test_name, type, output_type,
                                                            embedding=embedding, rules=rules)
    return {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "type": type,
        "outputType": output_type,
        "rules": rules.get(),
        "embeddingColName": embedding,
        "test_type": "outlier_detection"
    }


def outlier_detection_test_analysis_validation(test_session: TestSession, dataset_name: str, test_name: str,
                                               type: str, output_type: str, embedding: str, rules: OutlierDetectionRules):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session,
                      TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}",
                                            headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)

    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(rules, OutlierDetectionRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'str')}"
    assert isinstance(embedding, str) and output_type, f"{REQUIRED_ARG_V2.format('embedding', 'str')}"
    return dataset_id

def active_learning(test_session:TestSession,
                    dataset_name:str,
                    test_name:str,
                    type:str,
                    output_type: str,
                    embed_col_name: str,
                    budget: int):

    dataset_id = active_learning_validation(test_session, dataset_name, test_name, type, output_type, embed_col_name, budget)
    return {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "type": type,
        "outputType": output_type,
        "embeddingColName": embed_col_name,
        "budget": budget,
        "test_type":"active_learning"
    }

def active_learning_validation(test_session:TestSession, dataset_name:str, test_name:str, type:str, output_type:str, embed_col_name:str, budget:int):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)

    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(budget, int) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(embed_col_name, str) and embed_col_name, f"{REQUIRED_ARG_V2.format('embed_col_name', 'str')}"
    return dataset_id

def semantic_similarity(test_session:TestSession,
                        dataset_name: str,
                        test_name: str,
                        type: str,
                        output_type: str,
                        embed_col_name: str,
                        rules: LQRules,
                        generated_embed_col_name: Optional[str] = "",
                        level: Optional[str] = ""):

    dataset_id = semantic_similarity_validation(test_session, dataset_name, test_name, type, output_type, embed_col_name, rules, generated_embed_col_name)
    payload =  {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "type": type,
        "outputType": output_type,
        "embeddingColName": embed_col_name,
        "rules": rules.get(),
    }
    if generated_embed_col_name is not None and generated_embed_col_name!="":
        payload["generatedEmbeddingColName"] = generated_embed_col_name
        payload["test_type"] = "semantic_similarity"
    else:
        payload["test_type"] = "nearest-neighbour"
    if output_type == "keypoint_detections":
        payload["level"] = level
        payload["testName"] = test_name
    return payload
def semantic_similarity_validation(test_session:TestSession, dataset_name:str, test_name:str, type:str, output_type:str, embed_col_name:str, rules: LQRules, generated_embed_col_name: Optional[str] = ""):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)

    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(embed_col_name, str) and embed_col_name, f"{REQUIRED_ARG_V2.format('embed_col_name', 'str')}"
    assert isinstance(rules, LQRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'str')}"
    return dataset_id

def nearest_duplicate(test_session:TestSession,
                      dataset_name:str,
                      test_name:str,
                      type:str,
                      output_type: str,
                      embed_col_name: str,
                      rules: LQRules,
                      generated_embed_col_name: Optional[str] = "",
                      level: Optional[str] = ""):
    return semantic_similarity(test_session, dataset_name, test_name, type, output_type, embed_col_name, rules, generated_embed_col_name, level)


def data_leakage_test(test_session:TestSession,
                      dataset_name:str,
                      test_name:str,
                      type:str,
                      output_type: str,
                      rules: LQRules,
                      sub_type:Optional[str] = "",
                      train_dataset_name: Optional[str] = "",
                      train_embed_col_name: Optional[str] = "",
                      embed_col_name: Optional[str] = ""):

    dataset_id = data_leakage_test_validation(test_session, dataset_name, test_name, type, output_type)
    payload =  {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "type": type,
        "outputType": output_type,
        "rules": rules.get()
    }

    if train_dataset_name is not None and train_dataset_name!="" and train_embed_col_name is not None and train_embed_col_name!="" and embed_col_name is not None and embed_col_name!="":
        trainDataset_id = data_leakage_test_validation(test_session, train_dataset_name, test_name, type, output_type)
        payload["trainDatasetId"] = trainDataset_id
        payload["embeddingColName"] = embed_col_name
        payload["trainEmbeddingColName"] = train_embed_col_name
        payload["test_type"] = "data_leakage"
    else:
        payload["subType"] = sub_type
        payload["test_type"] = "data_augmentation"

    return payload

def data_leakage_test_validation(test_session:TestSession, dataset_name:str, test_name:str, type:str, output_type:str):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2
    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)
    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)

    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    return dataset_id

def data_augmentation_test(test_session:TestSession,
                      dataset_name:str,
                      test_name:str,
                      type:str,
                      sub_type:str,
                      output_type: str,
                      rules: DARules,):
    return data_leakage_test(test_session, dataset_name, test_name, type, output_type, rules, sub_type)


def label_drift_test(test_session: TestSession,
                     referenceDataset: str,
                     evalDataset: str,
                     test_name: str,
                     type: str,
                     output_type: str,
                     gt: str,
                     rules: LDTRules):

    ref_res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={referenceDataset}", headers={"Authorization": f'Bearer {test_session.token}'})
    ref_dataset_id = ref_res_data.get("data", {}).get("id")

    eval_res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={evalDataset}", headers={"Authorization": f'Bearer {test_session.token}'})
    eval_dataset_id = eval_res_data.get("data", {}).get("id")

    response = {
        "referenceDatasetId" : ref_dataset_id,
        "evalDatasetId": eval_dataset_id,
        "name": test_name,
        "gt": gt,
        "type": type,
        "test_type": "label-drift-detection",
        "outputType": output_type,
        "rules": rules.get(),
    }

    return response


def llm_guardrail_test(test_session: TestSession,
                       dataset: str,
                       test_name: str,
                       type: str,
                       test_type: str,
                       output_type: str,
                       prompt_col_name: str,
                       response_col_name: str,
                       rules: LlmGuardrailTestRules):
    dataset = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset}",
                                           headers={"Authorization": f'Bearer {test_session.token}'})
    dataset_id = dataset.get("data", {}).get("id")

    response = {
        "datasetId": dataset_id,
        "testName": test_name,
        "type": type,
        "test_type": test_type,
        "outputType": output_type,
        "promptColName": prompt_col_name,
        "responseColName": response_col_name,
        "guardrailRequestRules": rules.get(),
    }

    return response


def fma_structured_data(test_session: TestSession,
                        dataset_name: str,
                        test_name: str,
                        model: str,
                        gt: str,
                        rules: LQRules,
                        output_type: str,
                        type: str,
                        embedding: str,
                        clustering: Optional[dict] = {},
                        aggregation_levels: Optional[list] = [],
                        sub_type: Optional[str] = None):
    dataset_id = fma_structured_data_validation(test_session=test_session, dataset_name=dataset_name,
                                                test_name=test_name, model=model, gt=gt, type=type, rules=rules,
                                                output_type=output_type,
                                                embedding=embedding, clustering=clustering,
                                                aggregation_levels=aggregation_levels
                                                )
    response = {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "model": model,
        "gt": gt,
        "type": type,
        "rules": rules.get(),
        "test_type": "fma_sd",
        "filter": "",
        "embeddingColName":embedding,
        "outputType": output_type,
        "aggregationLevels": aggregation_levels,
        "subType": sub_type
    }

    if clustering:
        response['clusterId'] = clustering
    return response

def fma_structured_data_validation(test_session: TestSession, dataset_name: str, test_name: str, model: str, gt: str,
                                   rules: LQRules, output_type: str, type: str, embedding: str,
                                   clustering: Optional[dict] = None, aggregation_levels: Optional[list]=[]):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    if aggregation_levels:
        assert isinstance(aggregation_levels, list), f"{REQUIRED_ARG_V2.format('aggregation_levels', 'list')}"

    assert isinstance(test_session,
                      TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}",
                                            headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)

    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(model, str) and model, f"{REQUIRED_ARG_V2.format('model', 'str')}"
    assert isinstance(gt, str) and gt, f"{REQUIRED_ARG_V2.format('gt', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(rules,LQRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'instance of the LQRules')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(embedding, str) and output_type, f"{REQUIRED_ARG_V2.format('embedding', 'str')}"

    return dataset_id

def scenario_imbalance(test_session: TestSession,
                       dataset_name: str,
                       test_name: str,
                       rules: SBRules,
                       output_type: str,
                       type: str,
                       embedding: Optional[str] = None,
                       clustering: Optional[dict] = {},
                       aggregationLevels: Optional[list] = [],
                       level: Optional[str] = "",
                       binning_parameters: Optional[dict] = None,
                       ):
    dataset_id = scenario_imbalance_validation(test_session=test_session, dataset_name=dataset_name,
                                               test_name=test_name, type=type, rules=rules,
                                               output_type=output_type,
                                               clustering=clustering, embedding=embedding,
                                               aggregationLevels=aggregationLevels)
    response = {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "type": type,
        "rules": rules.get(),
        "test_type": "scenario_imbalance",
        "embeddingColName":embedding,
        "outputType": output_type,
        "aggregationLevels": aggregationLevels,
        "binningParameters": binning_parameters
    }

    if clustering:
        response['clusterId'] = clustering

    if output_type == "keypoint_detections":
        response['level'] = level
        response['testName'] = test_name
    return response


def scenario_imbalance_ref_dataset(test_session: TestSession,
                                   dataset_name: [],
                                   test_name: str,
                                   rules: SBRules,
                                   output_type: str,
                                   type: str,
                                   embedding: Optional[str] = None,
                                   clustering: Optional[dict] = {},
                                   aggregation_levels: Optional[list] = [],
                                   ref_cluster: Optional[dict] = None,
                                   odd: Optional[str] = None,
                                   binning_parameters: Optional[dict] = None,
                                   filter: Optional[str] = "",
                                   Reference_dataset: Optional[str] = None,
                                   ):
    dataset_ids = []
    for dataset in dataset_name:
        dataset_id = scenario_imbalance_validation(test_session=test_session, dataset_name=dataset,
                                                   test_name=test_name, type=type, rules=rules,
                                                   output_type=output_type,
                                                   clustering=clustering, embedding=embedding,
                                                   aggregationLevels=aggregation_levels)
        dataset_ids.append(dataset_id)

    ref_dataset_id = None
    if Reference_dataset is not None:
        ref_dataset_id = scenario_imbalance_validation(test_session=test_session, dataset_name=Reference_dataset,
                                                   test_name=test_name, type=type, rules=rules,
                                                   output_type=output_type,
                                                   clustering=clustering, embedding=embedding,
                                                   aggregationLevels=aggregation_levels)
        

    response = {
        "datasetIds": dataset_ids,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "type": type,
        "rules": rules.get(),
        "test_type": "scenario_imbalance",
        "embeddingColName": embedding,
        "outputType": output_type,
        "aggregationLevels": aggregation_levels,
        "referenceDatasetId": ref_dataset_id,
        "binningParameters": binning_parameters,
        "filter": filter,
        "odd": odd
    }

    if clustering:
        response['clusterId'] = clustering
        if ref_cluster is not None: 
            response['refClusterId'] = ref_cluster
    return response


def scenario_imbalance_validation(test_session: TestSession, dataset_name: str, test_name: str, type: str,
                                  rules: SBRules, output_type: str, embedding: Optional[str] = None,
                                  clustering: Optional[dict] = None,
                                  aggregationLevels: Optional[list] = None):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session,
                      TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}",
                                            headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)

    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(rules, SBRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'instance of the SBRules')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    return dataset_id


def entropy_analysis_test(test_session: TestSession,
                          test_name: str,
                          rules: list,
                          output_type: str,
                          type: str,
                          embedding: Optional[str] = None,
                          clustering: Optional[dict] = None,
                          aggregation_levels: Optional[list] = None,
                          bin_params: Optional[dict] = None,
                          odd_dataset_name: Optional[str] = None,
                          dataset_name: Optional[str] = None
                          ) :

    if dataset_name is not None:
        res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}",
                                                headers={"Authorization": f'Bearer {test_session.token}'})
        from raga.constants import INVALID_RESPONSE
        if not isinstance(res_data, dict):
            raise ValueError(INVALID_RESPONSE)
        dataset_id = res_data.get("data", {}).get("id")
    else:
        dataset_id = 90  #random long number

    response = {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "type": type,
        "rules": rules.get(),
        "test_type": "entropy-analysis",
        "embeddingColName":embedding,
        "outputType": output_type,
        "aggregationLevels": aggregation_levels,
        "binParams": bin_params
    }

    if clustering:
        response['clusterId'] = clustering

    if odd_dataset_name is not None:
        response["oddDatasetName"] = odd_dataset_name
        response["isOdd"] = 1
    else:
        response["isOdd"] = 0

    return response


def failure_mode_analysis_llm(test_session:TestSession,
                              dataset_name:str,
                              test_name:str,
                              model:str,
                              gt:str,
                              rules:FMA_LLMRules,
                              type:str,
                              output_type:str,
                              prompt_col_name: str,
                              model_column: str,
                              gt_column: str,
                              embedding_col_name: str,
                              model_embedding_column: str,
                              gt_embedding_column: str,
                              clustering:Optional[dict]={},
                              ):

    dataset_id = failure_mode_analysis_llm_validation(test_session=test_session, dataset_name=dataset_name, test_name=test_name, model=model, gt=gt, rules=rules, output_type=output_type, model_column= model_column, gt_column = gt_column, model_embedding_column = model_embedding_column, gt_embedding_column =  gt_embedding_column, clustering=clustering)
    testRules = rules.get()

    metricList = {}
    for rulesDict in testRules:
        if(rulesDict["evalMetric"] == "BLEU"):
            metricList["BLEU"] = "bleu_score"
        elif(rulesDict["evalMetric"] == "ROUGE"):
            metricList["ROUGE"] = "rouge_score"
        elif(rulesDict["evalMetric"] == "METEOR"):
            metricList["METEOR"] = "meteor_score"
        elif(rulesDict["evalMetric"] == "CosineSimilarity"):
            metricList["CosineSimilarity"] = "cosine_score"
        elif(rulesDict["evalMetric"] == "user_feedback"):
            metricList["user_feedback"] = "user_feedback"

    response = {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "model": model,
        "gt": gt,
        "rules": rules.get(),
        "promptColName": prompt_col_name,
        "modelColName" : model_column,
        "gtColName" : gt_column,
        "embeddingColName": embedding_col_name,
        "modelEmbeddingColName" : model_embedding_column,
        "gtEmbeddingColName": gt_embedding_column,
        "test_type":"fma-llm",
        "type": type,
        "metricList": metricList,
        "outputType":output_type
    }

    if clustering:
        response['clusterId'] = clustering
    return response

def failure_mode_analysis_llm_validation(test_session:TestSession, dataset_name:str, test_name:str, model:str, gt:str, rules:FMA_LLMRules, output_type:str, model_column:str, gt_column:str, model_embedding_column:str, gt_embedding_column:str, clustering:Optional[dict]=None):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)

    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(model, str) and model, f"{REQUIRED_ARG_V2.format('model', 'str')}"
    assert isinstance(gt, str) and gt, f"{REQUIRED_ARG_V2.format('gt', 'str')}"
    assert isinstance(model_column, str) and model_column, f"{REQUIRED_ARG_V2.format('model_column', 'str')}"
    assert isinstance(gt_column, str) and gt_column, f"{REQUIRED_ARG_V2.format('gt_column', 'str')}"
    assert isinstance(model_embedding_column, str) and model_embedding_column, f"{REQUIRED_ARG_V2.format('model_embedding_column', 'str')}"
    assert isinstance(gt_embedding_column, str) and gt_embedding_column, f"{REQUIRED_ARG_V2.format('gt_embedding_column', 'str')}"
    assert isinstance(rules, FMA_LLMRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'instance of the FMARules')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"

    return dataset_id


def class_imbalance_test(test_session: TestSession,
                         dataset_name: str,
                         test_name: str,
                         type: str,
                         output_type: str,
                         annotation_column_name: str,
                         rules: ClassImbalanceRules):

    dataset_id = class_imbalance_test_validation(test_session=test_session, dataset_name=dataset_name, test_name=test_name, type=type, output_type=output_type, annotation_column_name=annotation_column_name, rules=rules)

    return {
        "datasetId": dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "test_type": "class-imbalance",
        "type": type,
        "outputType": output_type,
        "annotationColumnName": annotation_column_name,
        "rules": rules.get(),
    }

def class_imbalance_test_validation(test_session: TestSession,
                                    dataset_name: str,
                                    test_name: str,
                                    type: str,
                                    output_type: str,
                                    annotation_column_name: str,
                                    rules: ClassImbalanceRules):

    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2
    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})

    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)

    dataset_id = res_data.get("data", {}).get("id")
    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)

    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(annotation_column_name, str) and annotation_column_name, f"{REQUIRED_ARG_V2.format('annotation_column_name', 'str')}"
    assert isinstance(rules, ClassImbalanceRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'instance of the ClassImbalanceRules')}"
    return dataset_id


def stress_test(test_session: TestSession, test_name: str,
                original_dataset: str,
                augment_dataset: str,
                stage: str,
                output_type: str,
                gt: str,
                model: str,
                rules: STRules,
                augment_config: dict = {}):

    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2
    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(original_dataset, str) and original_dataset, f"{REQUIRED_ARG_V2.format('original_dataset', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={original_dataset}", 
                                            headers={"Authorization": f'Bearer {test_session.token}'})
    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)

    dataset_id = res_data.get("data", {}).get("id")
    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)

    if stage not in ["augment", "stress_test"]:
        raise ValueError("stage must be augment or stress_test")

    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(stage, str) and stage, f"{REQUIRED_ARG_V2.format('stage', 'str')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"
    assert isinstance(rules, STRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'instance of the STRules')}"
    assert isinstance(gt, str) and gt, f"{REQUIRED_ARG_V2.format('gt', 'str')}"
    assert isinstance(model, str) and model, f"{REQUIRED_ARG_V2.format('model', 'str')}"

    parsed_augment_config = {}
    if stage == "augment":
        assert isinstance(augment_config, dict) and augment_config, f"{REQUIRED_ARG_V2.format('augment_config', 'dict')}"
        parsed_augment_config = stress_test_validate_augmente_config(augment_config)

    return {
        "datasetId": dataset_id,
        "augmentDataset": augment_dataset,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "test_type": "stress_test",
        "stage": stage,
        "outputType": output_type,
        "gt": gt,
        "model": model,
        "augmentConfig": parsed_augment_config,
        "rules": rules.get()
    }


def stress_test_validate_augmente_config(augment_config: dict):
    from raga.constants import REQUIRED_ARG_V2
    parsed_augment_config = {}
    for key in augment_config.keys():
        if key.startswith("scenario_"):
            scenario = augment_config[key]
            assert isinstance(scenario, dict) and scenario, f"{REQUIRED_ARG_V2.format(key, 'dict')}"

            parsed_augment_config[key] = {}
            for sub_key in scenario:
                if sub_key == "type" or sub_key == "technique" or sub_key == "default":
                    assert isinstance(scenario[sub_key], str) and scenario[sub_key], f"{REQUIRED_ARG_V2.format(sub_key, 'str')}"
                else:
                    assert isinstance(scenario[sub_key], list) and scenario[sub_key], f"{REQUIRED_ARG_V2.format(sub_key, 'list')}"
        elif "properties" == key:
            parsed_augment_config[key] = augment_config[key]
        else:
            raise KeyError(f"Invalid key in augment config : {key}")

    return json.loads(json.dumps(augment_config))


def image_property_drift(test_session: TestSession,
                         reference_dataset_name: str,
                         eval_dataset_name: str,
                         rules: IPDRules,
                         test_name: str,
                         type: str,
                         output_type: str,
                         ):
    reference_dataset_id = image_property_drift_data_validation(test_session=test_session,
                                                                dataset_name=reference_dataset_name,
                                                                test_name=test_name, rules=rules,
                                                                output_type=output_type, type=type)
    eval_dataset_id = image_property_drift_data_validation(test_session=test_session,
                                                           dataset_name=eval_dataset_name,
                                                           test_name=test_name, rules=rules,
                                                           output_type=output_type, type=type)

    response = {
        "datasetId": reference_dataset_id,
        "evalDatasetId": eval_dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "type": type,
        "rules": rules.get(),
        "test_type": "image-property-drift",
        "outputType": output_type
    }

    return response

def image_property_drift_data_validation(test_session: TestSession, dataset_name: str, test_name: str,
                                   rules: IPDRules, output_type: str, type: str):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session,
                      TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}",
                                            headers={"Authorization": f'Bearer {test_session.token}'})


    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)

    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(rules,IPDRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'instance of the IPDRules')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"

    return dataset_id


def llm_drift_test(test_session:TestSession,
                         train_dataset_name: str,
                         field_dataset_name: str,
                         test_name: str,
                         train_embed_col_name: str,
                         field_embed_col_name: str,
                         train_prompt_col_name: str,
                         field_prompt_col_name:  str,
                         train_response_col_name: str,
                         field_response_col_name: str,
                         model: str,
                         level: str="prompt",
                         train_gt_col_name: Optional[str] = None,
                         field_gt_col_name: Optional[str] = None,
                         train_context_col_name : Optional[str] = None,
                         field_context_col_name : Optional[str] = None,
                         rules:list=[],
                         aggregation_level:  Optional[list] = [],
                         filter: Optional[str] = ""):


    train_res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={train_dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})
    train_dataset_id = train_res_data.get("data", {}).get("id")
    field_res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={field_dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})
    field_dataset_id = field_res_data.get("data", {}).get("id")

    response = {
        "datasetId": field_dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "aggregationLevels": aggregation_level,
        "filter":filter,
        "trainDatasetId":train_dataset_id,
        "level": level,
        "outputType":"llm-drift",
        "trainPromptColName" : train_prompt_col_name,
        "trainResponseColName" : train_response_col_name,
        "trainGtColName" : train_gt_col_name,
        "fieldPromptColName" : field_prompt_col_name,
        "fieldResponseColName" : field_response_col_name,
        "fieldGtColName" : field_gt_col_name,
        "trainEmbedColName": train_embed_col_name,
        "fieldEmbedColName": field_embed_col_name,
        "trainContextColName": train_context_col_name,
        "fieldContextColName": field_context_col_name,
        "model": model,
        "rules": rules.get(),
        'test_type':'llm-drift'
    }
    return response

def llm_performance_test(test_session:TestSession,
                              dataset_name:str,
                              model:str,
                              prompt_col_name: str,
                              context_col_name:str,
                              response_col_name:str,
                              type: str,
                              output_type: str,
                              open_ai_api_key: str,
                              rules:LLMRules,
                              test_name: str,
                              prompt_embedding_col: Optional[str] =None,
                              response_embedding_col: Optional[str] =None,
                              gt_embedding_col: Optional[str] =None,
                              gt_col_name: Optional[str] =None
                              ):

    dataset_id = llm_performance_validation(test_session=test_session,  dataset_name=dataset_name, model= model, prompt_col_name= prompt_col_name, context_col_name= context_col_name, response_col_name = response_col_name, type= type, output_type = output_type, open_ai_api_key = open_ai_api_key, rules = rules)

    response = {
        "type": type,
        "datasetId": dataset_id,
        "outputType": output_type,
        "model": model,
        "name": test_name,
        "responseColumnName": response_col_name,
        "groundTruthColumnName": gt_col_name,
        "contextColumnName": context_col_name,
        "promptColumnName": prompt_col_name,
        "openAIAPIKey": open_ai_api_key,
        "rules": rules.get(),
        "promptEmbeddingColName": prompt_embedding_col,
        "gtEmbeddingColumnName": gt_embedding_col,
        "responseEmbeddingColumn": response_embedding_col,
        "experimentId": test_session.experiment_id,
        "test_type":"llm-performance"
    }

    return response


def llm_performance_validation(test_session:TestSession, dataset_name:str, model:str, prompt_col_name: str, context_col_name:str, response_col_name:str, type: str, output_type: str, open_ai_api_key: str, rules:LLMRules):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session,
                      TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={dataset_name}",
                                            headers={"Authorization": f'Bearer {test_session.token}'})


    if not isinstance(res_data, dict):
        raise ValueError(INVALID_RESPONSE)

    dataset_id = res_data.get("data", {}).get("id")

    if not dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    assert isinstance(dataset_name, str) and dataset_name, f"{REQUIRED_ARG_V2.format('dataset_name', 'str')}"
    assert isinstance(prompt_col_name, str) and prompt_col_name, f"{REQUIRED_ARG_V2.format('prompt_col_name', 'str')}"
    assert isinstance(context_col_name, str) and context_col_name, f"{REQUIRED_ARG_V2.format('context_col_name', 'str')}"
    assert isinstance(response_col_name, str) and response_col_name, f"{REQUIRED_ARG_V2.format('response_col_name', 'str')}"
    assert isinstance(open_ai_api_key, str) and open_ai_api_key, f"{REQUIRED_ARG_V2.format('open_ai_api_key', 'str')}"
    assert isinstance(model, str) and model, f"{REQUIRED_ARG_V2.format('model', 'str')}"
    assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
    assert isinstance(rules, LLMRules) and rules, f"{REQUIRED_ARG_V2.format('rules', 'instance of the LLMRules')}"
    assert isinstance(output_type, str) and output_type, f"{REQUIRED_ARG_V2.format('output_type', 'str')}"

    return dataset_id

def spatio_temporal_drift_test(test_session:TestSession,
                               train_dataset_name: str,
                               field_dataset_name: str,
                               test_name: str,
                               train_embed_col_name: str,
                               field_embed_col_name: str,
                               model: str,
                               primary_metadata: str,
                               primary_metadata_type : str,
                               type : str,
                               level: str="",
                               rules:list=[],
                               aggregation_level:  Optional[list] = [],
                               filter: Optional[str] = ""):


    train_res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={train_dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})
    train_dataset_id = train_res_data.get("data", {}).get("id")
    field_res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={field_dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})
    field_dataset_id = field_res_data.get("data", {}).get("id")

    response = {
        "datasetId": field_dataset_id,
        "experimentId": test_session.experiment_id,
        "name": test_name,
        "aggregationLevels": aggregation_level,
        "filter":filter,
        "trainDatasetId":train_dataset_id,
        "level": level,
        "outputType":"spatio-drift",
        "trainEmbedColName": train_embed_col_name,
        "fieldEmbedColName": field_embed_col_name,
        "model": model,
        "primaryMetadata": primary_metadata,
        "primaryMetadataType": primary_metadata_type,
        "type": type,
        "rules": rules.get(),
        'test_type':'spatio-drift'
    }
    return response

