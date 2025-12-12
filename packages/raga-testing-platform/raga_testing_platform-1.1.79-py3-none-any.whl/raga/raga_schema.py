from abc import ABC
from typing import Any, Dict, List, Optional
from datetime import datetime

class RagaSchemaElement(ABC):
    def __init__(self):
        self.type = ""
        self.model = ""
        self.ref_col_name = ""
        self.label_mapping = {}
        self.channel_mapping = {}
        self.skeleton_mapping = {}
        self.schema = ""

class PredictionSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "imageName"

class GeneratedImageNameSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "generatedImageName"

class TextSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "non_indexed_text"

class FrameSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "frameNumber"

class ParentSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "parentId"

class ImageUriSchemaElement(RagaSchemaElement):
    def __init__(self, channel_mapping:Optional[dict]=None):
        super().__init__()
        self.type = "imageUri"
        self.channel_mapping = channel_mapping

class TraceUriSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "traceUri"

class GeneratedImageUriSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "generatedImageUri"

class MaskUriSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "maskUri"

class TimeOfCaptureSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "timestamp"

class FeatureSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "feature"

class CategoricalFeatureSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "categoricalFeature"

class NumericalFeatureSchemaElement(RagaSchemaElement):
    def __init__(self, model:str = None, label_mapping: Optional[dict] = {}):
        super().__init__()
        self.type = "numericalFeature"
        self.label_mapping = label_mapping
        self.model = model

class NonIndexableNumericalFeatureSchemaElement(NumericalFeatureSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "non_indexed_numeric"

class AttributeSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "attribute"

class BooleanAttributeSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "booleanAttribute"

class InferenceSchemaElement(RagaSchemaElement):
    def __init__(self, model:str, label_mapping:Optional[dict]=None, skeleton_mapping:Optional[dict]=None):
        super().__init__()
        from raga.constants import REQUIRED_ARG_V2

        if not isinstance(model, str) or not model:
            raise ValueError(f"{REQUIRED_ARG_V2.format('model', 'str')}")
        self.type = "inference"
        self.model = model
        self.label_mapping = label_mapping
        self.skeleton_mapping = skeleton_mapping

class ObjectRecognitionSchemaElement(RagaSchemaElement):
    def __init__(self, model: str, label_mapping:dict):
        super().__init__()
        self.type = "recognition"
        self.model = model
        self.label_mapping = label_mapping

class VideoInferenceSchemaElement(RagaSchemaElement):
    def __init__(self, model:str, label_mapping:Optional[dict]=None, skeleton_mapping:Optional[dict]=None):
        super().__init__()
        from raga.constants import REQUIRED_ARG_V2

        if not isinstance(model, str) or not model:
            raise ValueError(f"{REQUIRED_ARG_V2.format('model', 'str')}")
        self.type = "videoInference"
        self.label_mapping=label_mapping
        self.skeleton_mapping=skeleton_mapping
        self.model = model
        self.label_mapping = label_mapping
        self.skeleton_mapping = skeleton_mapping

class EventInferenceSchemaElement(RagaSchemaElement):
    def __init__(self, model:str):
        super().__init__()
        from raga.constants import REQUIRED_ARG_V2

        if not isinstance(model, str) or not model: 
            raise ValueError(f"{REQUIRED_ARG_V2.format('model', 'str')}")
        self.type = "eventInference"
        self.model = model

class ImageEmbeddingSchemaElement(RagaSchemaElement):
    def __init__(self, model:str="", ref_col_name:str=""):
        super().__init__()
        self.type = "imageEmbedding"
        self.model = model
        self.ref_col_name = ref_col_name

class TargetSchemaElement(RagaSchemaElement):
    def __init__(self, model:str, label_mapping: Optional[dict] = {}):
        super().__init__()
        self.type = "target"
        self.model = model
        self.label_mapping = label_mapping

class ImageClassificationSchemaElement(RagaSchemaElement):
    def __init__(self, model:str, ref_col_name:str="", label_mapping: Optional[dict] = {}):
        super().__init__()
        from raga.constants import REQUIRED_ARG_V2
        if not isinstance(model, str) or not model: 
            raise ValueError(f"{REQUIRED_ARG_V2.format('model', 'str')}")
        self.type = "classification"
        self.model = model
        self.ref_col_name = ref_col_name
        self.label_mapping = label_mapping

class TIFFSchemaElement(RagaSchemaElement):
     def __init__(self, label_mapping:dict, schema:str="", model:str=""):
        super().__init__()
        from raga.constants import REQUIRED_ARG_V2
        if not isinstance(label_mapping, dict) or not label_mapping: 
            raise ValueError(f"{REQUIRED_ARG_V2.format('label_mapping', 'dist')}")
        # Check that the label_mapping keys are integers and values are strings
        for key, value in label_mapping.items():
            if not isinstance(key, int) or not isinstance(value, str):
                raise ValueError(f"{REQUIRED_ARG_V2.format('label_mapping', 'str')}")
        self.type = "blob"
        self.label_mapping = label_mapping
        self.schema = schema
        self.model = model

class InferenceCountSchemaElement(RagaSchemaElement):
    def __init__(self, model: str):
        super().__init__()
        from raga.constants import REQUIRED_ARG_V2
        self.type = "inferenceCount"
        self.model = model


class BlobSchemaElement(RagaSchemaElement):
     def __init__(self):
        super().__init__()
        self.type = "blob"

class SemanticSegmentationSchemaElement(RagaSchemaElement):
     def __init__(self):
        super().__init__()
        self.type = "imageSegmentation"

class RoiEmbeddingSchemaElement(RagaSchemaElement):
    def __init__(self, model:str, ref_col_name:str=""):
        super().__init__()
        from raga.constants import REQUIRED_ARG_V2
        if not isinstance(model, str) or not model: 
            raise ValueError(f"{REQUIRED_ARG_V2.format('model', 'str')}")
        self.type = "roiEmbedding"
        self.model = model
        self.ref_col_name = ref_col_name

class MistakeScoreSchemaElement(RagaSchemaElement):
    def __init__(self, ref_col_name:str=""):
        super().__init__()
        self.type = "mistakeScores"
        self.ref_col_name = ref_col_name



class RagaSchema():
    def __init__(self):
        self.columns = list()

    def validation(self, column_name: str, ragaSchemaElement:RagaSchemaElement):
        from raga import REQUIRED_ARG_V2
        if not isinstance(column_name, str) or not column_name: 
            raise ValueError(f"{REQUIRED_ARG_V2.format('column_name', 'str')}")
        if not isinstance(ragaSchemaElement, RagaSchemaElement): 
            raise ValueError(f"{REQUIRED_ARG_V2.format('ragaSchemaElement', 'instance of the RagaSchemaElement')}")
        return True
     
    def add(self, column_name: str, ragaSchemaElement:RagaSchemaElement):
        for column in self.columns:
            if column.get("customerColumnName") == column_name :
                raise ValueError(f"Duplicate column is present in schema : {column_name}")
        self.validation(column_name, ragaSchemaElement)
        self.columns.append({
            "customerColumnName": column_name,
            "type": ragaSchemaElement.type,
            "modelName": ragaSchemaElement.model,
            "refColName": ragaSchemaElement.ref_col_name,
            "columnArgs":{
                "labelMapping": ragaSchemaElement.label_mapping,
                "channelMapping": ragaSchemaElement.channel_mapping,
                "skeletonMapping": ragaSchemaElement.skeleton_mapping,
                "schema": ragaSchemaElement.schema,
            }
        })

class LDTRules():
    def __init__(self):
        self.rules = []

    def add(self, metric: str, label:list = None, metric_threshold:float = None):
        from raga import REQUIRED_ARG_V2
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        rules = {"metric": metric}
        if metric_threshold:
            rules["metricThreshold"] = metric_threshold
        if label:
            rules["clazz"] = label
        self.rules.append(rules.copy())

    def get(self):
        return self.rules
 
class StringElement():
    def __init__(self, value:str):
        self.value = value

    def get(self):
        return self.value
    
class FloatElement():
    def __init__(self, value:float):
        self.value = value

    def get(self):
        return self.value

class BooleanElement:
    def __init__(self, value: bool):
        self.value = value

    def get(self):
        return self.value

class TimeStampElement():
    def __init__(self, date_time:datetime):
        self.date_time = date_time
    
    def get(self):
        return self.date_time
    
class AggregationLevelElement():
    def __init__(self):
        self.levels = []

    def add(self, level:str):
        assert isinstance(level, str) and level, "level is required and must be str."
        self.levels.append(level)

    def get(self):
        return self.levels
    
class ModelABTestTypeElement():
    def __init__(self, type:str):
        self.type = type
        if self.type not in ["labelled", "unlabelled"]:
            raise ValueError("Invalid value for 'type'. Must be one of: ['labelled', 'unlabelled'].")

    def get(self):
        return self.type    

       
class ModelABTestRules():
    def __init__(self):
        self.rules = []

    def add(self, metric:str, IoU:float, _class:str, threshold:float, conf_threshold:Optional[float]=None):
        from raga import REQUIRED_ARG_V2

        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        assert isinstance(_class, str) and _class,f"{REQUIRED_ARG_V2.format('_class', 'str')}"
        assert isinstance(IoU, float) and IoU, f"{REQUIRED_ARG_V2.format('IoU', 'float')}"
        assert isinstance(threshold, float) and threshold, f"{REQUIRED_ARG_V2.format('threshold', 'float')}"

        self.rules.append({ "metric" : metric, "iou": IoU,  "class": _class, "threshold":threshold, "confidenceThreshold": conf_threshold})

    def get(self):
        return self.rules
    
class EventABTestRules(ModelABTestRules):
    def __init__(self):
        super().__init__()

    def add(self, metric:str, IoU:float, _class:str, threshold:float, conf_threshold:Optional[float]=None):
        from raga import REQUIRED_ARG_V2

        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        assert isinstance(_class, str) and _class,f"{REQUIRED_ARG_V2.format('_class', 'str')}"
        assert isinstance(IoU, float) and IoU, f"{REQUIRED_ARG_V2.format('IoU', 'float')}"
        assert isinstance(threshold, float) and threshold, f"{REQUIRED_ARG_V2.format('threshold', 'float')}"
        self.rules.append({ "metric" : metric, "iou": IoU,  "clazz": [_class], "threshold":threshold, "confThreshold":conf_threshold })
    
class FMARules():
    def __init__(self):
        self.rules = []

    def add(self, 
            metric:str, 
            metric_threshold:Optional[float]=None, 
            label:Optional[str]=None, 
            conf_threshold:Optional[float]=None, 
            iou_threshold:Optional[float]=None,
            frame_overlap_threshold:Optional[float]=None,
            weights:Optional[dict]=None,
            type:Optional[str]=None,
            background_label:Optional[str]=None,
            include_background:Optional[bool]=False,
            clazz:Optional[list[str]]=None,
            level:Optional[str]=None,
            ) -> None:
        """
        Add a rule to the FMA rules list.

        Args:
            metric (str): The metric name.
            metric_threshold (float, optional): The metric threshold value.
            label (str, optional): The label associated with the rule.
            conf_threshold (float, optional): The confidence threshold.
            iou_threshold (float, optional): The intersection-over-union threshold.
            weights (dict, optional): Weights for the rule.
            type_ (str, optional): The type of the rule.
            background_label (str, optional): The background label.
            include_background (bool, optional): Whether to include background.
            
        Returns:
            None
        """
        from raga import REQUIRED_ARG_V2

        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        assert isinstance(metric_threshold, float) and metric_threshold, f"{REQUIRED_ARG_V2.format('metric_threshold', 'float')}"
        rules = {"metric" : metric, "threshold": metric_threshold}
        if iou_threshold: rules.update({"iou":iou_threshold })
        if conf_threshold: rules.update({"confThreshold":conf_threshold })
        if label: rules.update({"clazz":[label] })
        if weights: 
            if any(value < 0 for value in weights.values()):
                raise ValueError("Weights cannot contain negative values.")
            rules.update({"weights": weights, "clazz":["ALL"]})
        if type: rules.update({"type":type })
        if background_label: rules.update({"backgroundClass":background_label })
        if include_background: rules.update({"includeBackground":include_background })
        if frame_overlap_threshold: rules.update({"iou":frame_overlap_threshold})
        if clazz: rules.update({"class": clazz})
        if level: rules.update({"level": level})
        self.rules.append(rules)
            

    def get(self) -> List[Dict[str, Any]]:
        """
        Get the list of rules.

        Returns:
            List[Dict[str, Any]]: The list of rules.
        """
        return self.rules

class MCTRules():
    def __init__(self):
        self.rules = []

    def add(self,
            metric:str,
            metric_threshold:Optional[float]=None,
            label:Optional[str]=None,
            conf_threshold:Optional[float]=None,
            iou_threshold:Optional[float]=None,
            frame_overlap_threshold:Optional[float]=None,
            weights:Optional[dict]=None,
            type:Optional[str]=None,
            background_label:Optional[str]=None,
            include_background:Optional[bool]=False,
            differenceThreshold:Optional[float]=None,
            clazz:Optional[list[str]]=None,
            backgroundClass:Optional[str]=None,
            includeBackground:Optional[bool]=None
            ) -> None:
        """
        Add a rule to the FMA rules list.

        Args:
            metric (str): The metric name.
            metric_threshold (float, optional): The metric threshold value.
            label (str, optional): The label associated with the rule.
            conf_threshold (float, optional): The confidence threshold.
            iou_threshold (float, optional): The intersection-over-union threshold.
            weights (dict, optional): Weights for the rule.
            type_ (str, optional): The type of the rule.
            background_label (str, optional): The background label.
            include_background (bool, optional): Whether to include background.

        Returns:
            None
        """
        from raga import REQUIRED_ARG_V2

        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        assert isinstance(metric_threshold, float) and metric_threshold, f"{REQUIRED_ARG_V2.format('metric_threshold', 'float')}"
        rules = {"metric" : metric, "threshold": metric_threshold}
        if iou_threshold: rules.update({"iouThreshold":iou_threshold })
        if conf_threshold: rules.update({"confidenceThreshold":conf_threshold })
        if label: rules.update({"class":[label] })
        if differenceThreshold: rules.update({"differenceThreshold":differenceThreshold })
        if weights:
            if any(value < 0 for value in weights.values()):
                raise ValueError("Weights cannot contain negative values.")
            rules.update({"weights": weights, "clazz":["ALL"]})
        if type: rules.update({"type":type })
        if background_label: rules.update({"backgroundClass":background_label })
        if background_label: rules.update({"includeBackground":include_background })
        if frame_overlap_threshold: rules.update({"iou":frame_overlap_threshold})
        if clazz: rules.update({"class": clazz})
        if backgroundClass: rules.update({"backgroundClass": backgroundClass})
        if includeBackground: rules.update({"includeBackground": includeBackground})
        self.rules.append(rules)


    def get(self) -> List[Dict[str, Any]]:
        """
        Get the list of rules.

        Returns:
            List[Dict[str, Any]]: The list of rules.
        """
        return self.rules

class LQRules():
    def __init__(self):
        self.rules = []

    def add(self, metric: str, label: list = None, level: Optional[str] = "", metric_threshold: float = None):
        from raga import REQUIRED_ARG_V2
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        rules = {"metric": metric}
        if metric_threshold:
            rules["threshold"] = metric_threshold
        if label:
            rules["clazz"] = label
        if level:
            rules["level"] = level
        self.rules.append(rules.copy())

    def get(self):
        return self.rules

class SSRules(LQRules):
    pass

class TDRules(LQRules):
    pass

class DLRules(LQRules):
    pass

class NDRules(LQRules):
    pass


class IPDRules():
    def __init__(self):
        self.rules = []

    def add(self, metric: str):
        from raga import REQUIRED_ARG_V2
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        rule = {"metric": metric}
        self.rules.append(rule)

    def get(self):
        return self.rules

class SBRules():
    def __init__(self):
        self.rules = []

    def add(self, metric:str, ideal_distribution:str = None, metric_threshold:float = None, level: Optional[str] = "", min_value: Optional[int]= None):

        from raga import REQUIRED_ARG_V2
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        rules = {"metric": metric}
        if metric_threshold:
            rules["threshold"] = metric_threshold
        if ideal_distribution:
            rules["ideal_distribution"] = ideal_distribution
        if level:
            rules["idealDistribution"] = ideal_distribution
            rules["level"] = level
        if min_value:
            rules["min_value"] = min_value
        self.rules.append(rules.copy())

    def get(self):
        return self.rules

class EntropyRules(SBRules):
    pass

class FMA_LLMRules():
    def __init__(self):
        self.rules = []

    def add(self, metric:str, metric_threshold:float, eval_metric:str, threshold:float):
        from raga import REQUIRED_ARG_V2
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        assert isinstance(metric_threshold, float) and metric_threshold, f"{REQUIRED_ARG_V2.format('metric_threshold', 'float')}"
        assert isinstance(threshold, float) and threshold, f"{REQUIRED_ARG_V2.format('threshold', 'float')}"
        assert isinstance(eval_metric, str) and eval_metric, f"{REQUIRED_ARG_V2.format('eval_metric', 'str')}"
        self.rules.append({"metric":metric, "threshold":metric_threshold, "evalMetric":eval_metric, "evalThreshold":threshold})
    def get(self):
        return self.rules

class ClassImbalanceRules():
    def __init__(self):
        self.rules = []

    def add(self, metric: str, metric_threshold: float, ideal_distribution: str, label: str):
        from raga import REQUIRED_ARG_V2
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        assert isinstance(metric_threshold, float) and metric_threshold, f"{REQUIRED_ARG_V2.format('metric_threshold', 'float')}"
        assert isinstance(ideal_distribution, str) and ideal_distribution, f"{REQUIRED_ARG_V2.format('ideal_distribution', 'str')}"
        if label is None:
            label = "ALL"
        rule = {
            "metric": metric,
            "metricThreshold": metric_threshold,
            "idealDistribution": ideal_distribution,
            "clazz": [label],
        }
        self.rules.append(rule)

    def get(self):
        return self.rules

    
class STRules():
    def __init__(self):
        self.rules = []

    def add(self, metric: str, difference_percentage: float):
        from raga import REQUIRED_ARG_V2
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        assert isinstance(difference_percentage, float) and difference_percentage, f"{REQUIRED_ARG_V2.format('difference_percentage', 'float')}"
        rule = {
            "metric": metric,
            "differencePercentage": difference_percentage,
        }
        self.rules.append(rule)
    
    def get(self):
        return self.rules


class DARules():
    def __init__(self):
        self.rules = []

    def add(self, **kwargs):

        rules = {}
        for key, value in kwargs.items():
            rules[key] = value

        self.rules.append(rules.copy())

    def get(self):
        return self.rules


class OcrRules():
    def __init__(self):
        self.rules = []

    def add(self, expected_detection:dict):
        from raga import REQUIRED_ARG_V2
        assert isinstance(expected_detection, dict) and expected_detection, f"{REQUIRED_ARG_V2.format('expected_detection', 'dict')}"
        self.rules.append({ "expected_detection" : expected_detection})
    def get(self):
        return self.rules
    
class OcrAnomalyRules():
    def __init__(self):
        self.rules = []
    def add(self, type:str, dist_metric:str, threshold:float):
        from raga import REQUIRED_ARG_V2
        assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
        assert isinstance(dist_metric, str) and dist_metric, f"{REQUIRED_ARG_V2.format('dist_metric', 'str')}"
        assert isinstance(threshold, float) and threshold, f"{REQUIRED_ARG_V2.format('threshold', 'float')}"
        self.rules.append({ "type" : type, "dist_metric": dist_metric,  "threshold": threshold})
    def get(self):
        return self.rules

class OutlierDetectionRules():
    def __init__(self):
        self.rules = []
    def add(self, type: str, metric:str, threshold:float):
        from raga import REQUIRED_ARG_V2
        assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('dist_metric', 'str')}"
        assert isinstance(threshold, float) and threshold, f"{REQUIRED_ARG_V2.format('threshold', 'float')}"
        self.rules.append({ "type": type, "dist_metric": metric,  "threshold": threshold})
    def get(self):
        return self.rules

class DriftDetectionRules():
    def __init__(self):
        self.rules = []

    def add(self, type:str, dist_metric:str, threshold:Optional[float]=9999, _class:Optional[str]="ALL"):
        from raga import REQUIRED_ARG_V2
        
        assert isinstance(dist_metric, str) and dist_metric, f"{REQUIRED_ARG_V2.format('dist_metric', 'str')}"
        assert isinstance(type, str) and type, f"{REQUIRED_ARG_V2.format('type', 'str')}"
        rules = {"dist_metric" : dist_metric, "class": _class, "type": type}
        
        if threshold: rules.update({"threshold":threshold })
        self.rules.append(rules)

    def get(self):
        return self.rules

class Drift_LLMRules():
    def __init__(self):
        self.rules = []

    def add(self, metric:str, threshold:float):
        from raga import REQUIRED_ARG_V2
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        assert isinstance(threshold, float) and threshold, f"{REQUIRED_ARG_V2.format('threshold', 'float')}"
        self.rules.append({"dist_metric":metric, "threshold":threshold})

    def get(self):
        return self.rules

class LLMRules():
    def __init__(self):
        self.rules = []

    def add(self, metric:str, test_name:str, threshold:float = None):
        from raga import REQUIRED_ARG_V2
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        rules = {"metric": metric}
        if threshold:
            rules["threshold"] = threshold
        if test_name:
            rules["testName"] = test_name
        self.rules.append(rules.copy())

    def get(self):
        return self.rules

class SemanticSegmentation:
    def __init__(self, 
                 Id:Optional[str], 
                 Format:Optional[str], 
                 Confidence:Optional[float], 
                 LabelId:Optional[str] = None, 
                 LabelName:Optional[str]=None, 
                 Segmentation:Optional[list]=None):
        self.Id = Id
        self.LabelId = LabelId
        self.LabelName = LabelName
        self.Segmentation = Segmentation
        self.Format = Format
        self.Confidence = Confidence

class SemanticSegmentationObject():
    def __init__(self):
        self.segmentations = list()
    
    def add(self, segmentations:SemanticSegmentation):
        self.segmentations.append(segmentations.__dict__)
    
    def get(self):
        return self.__dict__
    
class MistakeScore:
    def __init__(self):
        self.mistake_scores = dict()
        self.pixel_areas = dict()
        self.distance_score = dict()
    
    def add(self, key:(str, int), value:(float, int, str), area:(float, int, str)):
        from raga import REQUIRED_ARG_V2
        assert isinstance(key, (str, int)) and key is not None, f"{REQUIRED_ARG_V2.format('key', 'str or int')}"
        assert isinstance(value, (float, int, str)) and value is not None, f"{REQUIRED_ARG_V2.format('value', 'float or int or str')}"
        assert isinstance(area, (float, int, str)) and area is not None, f"{REQUIRED_ARG_V2.format('area', 'float or int or str')}"
        self.mistake_scores[key]=value
        self.pixel_areas[key]=area


    def get(self):
        return self.__dict__


class DistanceScoreSchemaElement(RagaSchemaElement):
    def __init__(self, model:str, label_mapping:dict):
        super().__init__()
        from raga.constants import REQUIRED_ARG_V2
        if not isinstance(model, str) or not model:
            raise ValueError(f"{REQUIRED_ARG_V2.format('model', 'str')}")
        if not isinstance(label_mapping, dict) or not label_mapping:
            raise ValueError(f"{REQUIRED_ARG_V2.format('label_mapping', 'dist')}")
        # Check that the label_mapping keys are integers and values are strings
        for key, value in label_mapping.items():
            if not isinstance(key, int) or not isinstance(value, str):
                raise ValueError(f"{REQUIRED_ARG_V2.format('label_mapping', 'str')}")
        self.label_mapping = label_mapping
        self.model = model
        self.type = "distanceScores"

class DistanceScore:
    def __init__(self):
        self.distance_score = dict()

    def add(self, key: (str, int), value: (float, int, str)):
        from raga import REQUIRED_ARG_V2
        assert isinstance(key, (str, int)) and key is not None, f"{REQUIRED_ARG_V2.format('key', 'str or int')}"
        assert isinstance(value, (float, int, str)) and value is not None, f"{REQUIRED_ARG_V2.format('value', 'float or int or str')}"
        self.distance_score[key] = value

    def get(self):
        return self.__dict__

class InferenceCount:
    def __init__(self):
        self.inference_counts = dict()

    def add(self, key:(int, str), value:(int, str)):
        from raga import REQUIRED_ARG_V2
        assert isinstance(key, (int, str)) and key is not None, f"{REQUIRED_ARG_V2.format('key', 'int or str' )}"
        assert isinstance(value, (int, str)) and value is not None, f"{REQUIRED_ARG_V2.format('value', 'int or str')}"
        val = dict()
        self.inference_counts[key] = val
        val["count"] = value

    def get(self):
        return self.__dict__
    
class ObjectDetection:
    def __init__(self, Id:Optional[str], Format:Optional[str], Confidence:Optional[float], ClassId:Optional[str] = None, ClassName:Optional[str]=None, BBox=None):
        self.Id = Id
        self.ClassId = ClassId
        self.ClassName = ClassName
        self.BBox = BBox
        self.Format = Format
        self.Confidence = Confidence

class ObjectRecognition:
    def __init__(self, Id:Optional[str], Confidence:Optional[float], ClassId:Optional[str] = None, ClassName:Optional[str]=None, OcrText:Optional[str]=None):
        self.Id = Id
        self.ClassId = ClassId
        self.ClassName = ClassName
        self.OcrText = OcrText
        self.Confidence = Confidence

class EventDetection:
    def __init__(self, Id:Optional[str], EventType:Optional[str], StartFrame:Optional[int], EndFrame:Optional[str] = None, Confidence:Optional[str]=None):
        self.Id = Id
        self.EventType = EventType
        self.StartFrame = StartFrame
        self.EndFrame = EndFrame
        self.Confidence = Confidence

class VideoFrame:
    def __init__(self, frameId:Optional[str], timeOffsetMs:Optional[float], detections:ObjectDetection):
        self.frameId = frameId
        self.timeOffsetMs = timeOffsetMs
        self.detections = detections.__dict__.get('detections')

class ImageDetectionObject():
    def __init__(self):
        self.detections = list()
    
    def add(self, object_detection:(ObjectDetection, ObjectRecognition)):
        self.detections.append(object_detection.__dict__)

    def get(self):
        return self.__dict__
class ImageDetectionObjectV2():
    def __init__(self):
        self.detections = list()
    def add(self, frame_number: str, object_detection:(ObjectDetection, ObjectRecognition)):
        self.detections.append(object_detection.__dict__)
        self.frame = frame_number
    def get(self):
        return self.__dict__
class EventDetectionObject():
    def __init__(self):
        self.detections = list()
    
    def add(self, object_detection:EventDetection):
        self.detections.append(object_detection.__dict__)
    
    def get(self):
        return self.__dict__
    
class VideoDetectionObject():
    def __init__(self):
        self.frames = list()
    
    def add(self, video_frame:VideoFrame):
        self.frames.append(video_frame.__dict__)
    
    def get(self):
        return self.__dict__

class VideoDetectionObjectV2():
    def __init__(self):
        self.frames = list()

    def add(self, video_frame: ImageDetectionObjectV2()):
        self.frames.append(video_frame.get())

    def get(self):
        return self.__dict__
    
class ImageClassificationElement():
    def __init__(self):
        self.confidence = dict()
    
    def add(self, key:(str, int), value:(float, int, str)):
        from raga import REQUIRED_ARG_V2
        assert isinstance(key, (str, int)) and key, f"{REQUIRED_ARG_V2.format('key', 'str or int')}"
        assert isinstance(value, (float, int, str)) and value is not None, f"{REQUIRED_ARG_V2.format('value', 'float or int or str')}"
        self.confidence[key]=value
    
    def get(self):
        return self.__dict__

class Embedding:
    def __init__(self, embedding_val: float):
        from raga import REQUIRED_ARG_V2
        assert isinstance(embedding_val, (float, int)), f"{REQUIRED_ARG_V2.format('embedding', 'float')}"
        self.embedding = embedding_val

class ImageEmbedding:
    def __init__(self):
         self.embeddings = []

    def add(self, embedding_values: Optional[Embedding]):
        from raga import REQUIRED_ARG_V2
        if isinstance(embedding_values, Embedding):
            self.embeddings.append(embedding_values.embedding)
        else:
            assert isinstance(embedding_values, (float, int)), f"{REQUIRED_ARG_V2.format('embedding', 'float')}"
            self.embeddings.append(embedding_values)

    def get(self):
        return self.__dict__

class ROIEmbedding:
    def __init__(self):
         self.embeddings = dict()

    def add(self, id,  embedding_values: list):
        self.embeddings[id] = embedding_values

    def get(self):
        return self.__dict__


class LlmGuardrailTestRules:
    def __init__(self):
        self.rules = []

    def add(self, metric: str, label: list = None, metric_threshold: float = None):
        from raga import REQUIRED_ARG_V2
        assert isinstance(metric, str) and metric, f"{REQUIRED_ARG_V2.format('metric', 'str')}"
        rules = {"metric": metric}
        if metric_threshold:
            rules["threshold"] = metric_threshold
        if label:
            self.rules["clazz"] = label
        self.rules.append(rules.copy()) 

    def get(self):
        return self.rules
