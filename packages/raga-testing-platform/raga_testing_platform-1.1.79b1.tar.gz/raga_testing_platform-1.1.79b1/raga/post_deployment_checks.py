from typing import Optional
from raga import TestSession, DriftDetectionRules

def data_drift_detection(test_session:TestSession, 
                         dataset_name: str="", 
                         embed_col_name: str="", 
                         train_dataset_name: str="", 
                         field_dataset_name: str="", 
                         test_name: str="",
                         train_embed_col_name: str="",
                         field_embed_col_name: str="",
                         level: str="image", 
                         rules:DriftDetectionRules=[],
                         output_type:str="",
                         aggregation_level:  Optional[list] = [],
                         filter: Optional[str] = ""):
    if output_type == "super_resolution" or output_type == "outlier_detection" or output_type == "multi_class_anamoly_detection":
         train_dataset_name = dataset_name
         field_dataset_name = dataset_name
         train_embed_col_name = embed_col_name
         field_embed_col_name = embed_col_name
         level = "image"
    if level == "roi":
        level = "image"
         
    train_dataset_id, field_dataset_id = data_drift_detection_validation(test_session, train_dataset_name, field_dataset_name, test_name, train_embed_col_name, field_embed_col_name, level, rules, aggregation_level)

    return {
            "datasetId": field_dataset_id,
            "experimentId": test_session.experiment_id,
            "name": test_name,
            "aggregationLevels": aggregation_level,
            "filter":filter,
            "trainDatasetId":train_dataset_id,
            "trainEmbedColName": train_embed_col_name,
            "fieldEmbedColName": field_embed_col_name,
            "level": level,
            "outputType":output_type,
            "rules": rules.get(),
            'test_type':'drift_test'
        }

def data_drift_detection_validation(test_session:TestSession, 
                                    train_dataset_name: str, 
                                    field_dataset_name: str,
                                    test_name: str,
                                    train_embed_col_name: str,
                                    field_embed_col_name: str,
                                    level: str, 
                                    rules=DriftDetectionRules,
                                    aggregation_level:Optional[list] = []):
    from raga.constants import INVALID_RESPONSE, INVALID_RESPONSE_DATA, REQUIRED_ARG_V2

    assert isinstance(test_session, TestSession), f"{REQUIRED_ARG_V2.format('test_session', 'instance of the TestSession')}"
    assert isinstance(train_dataset_name, str) and train_dataset_name, f"{REQUIRED_ARG_V2.format('train_dataset_name', 'str')}"
    assert isinstance(field_dataset_name, str) and field_dataset_name, f"{REQUIRED_ARG_V2.format('field_dataset_name', 'str')}"
    
    train_res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={train_dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})
    if not isinstance(train_res_data, dict):
            raise ValueError(INVALID_RESPONSE)
    train_dataset_id = train_res_data.get("data", {}).get("id")
    if not train_dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    
    field_res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={field_dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})
    if not isinstance(field_res_data, dict):
            raise ValueError(INVALID_RESPONSE)
    field_dataset_id = field_res_data.get("data", {}).get("id")
    if not field_dataset_id:
        raise KeyError(INVALID_RESPONSE_DATA)
    
    assert isinstance(test_name, str) and test_name, f"{REQUIRED_ARG_V2.format('test_name', 'str')}"
    assert isinstance(train_embed_col_name, str) and train_embed_col_name, f"{REQUIRED_ARG_V2.format('train_embed_col_name', 'str')}"
    assert isinstance(field_embed_col_name, str) and field_embed_col_name, f"{REQUIRED_ARG_V2.format('field_embed_col_name', 'str')}"
    assert isinstance(level, str) and level, f"{REQUIRED_ARG_V2.format('level', 'str')}"
    assert isinstance(rules, DriftDetectionRules) and rules.get(), f"{REQUIRED_ARG_V2.format('rules', 'instance of the DriftDetectionRules')}"

    if aggregation_level:
        assert isinstance(aggregation_level, list), f"{REQUIRED_ARG_V2.format('aggregation_level', 'list')}"

    return train_dataset_id, field_dataset_id
