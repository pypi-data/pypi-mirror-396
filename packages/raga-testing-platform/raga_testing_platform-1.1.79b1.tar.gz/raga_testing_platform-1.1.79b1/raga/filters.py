from abc import ABC
from typing import Optional

class CoreFilter(ABC):
    def __init__(self):
        pass

class Filter():
    def __init__(self):
        self.filters = {}
    
    def add(self, filter:CoreFilter):
        self.filters.update(filter.__dict__)
        return self.filters
    
    def get(self):
        return self.filters
    
class TimestampFilter(CoreFilter):
    def __init__(self, gte:Optional[str]="", lte:Optional[str]=""):
        super().__init__()
        self.timestamp = {
            "gte": gte,
            "lte":lte   
        }
