from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ParamSpace:
    headers: Dict[str, List[str]]
    query: Dict[str, List[str]]
    body: Dict[str, List[str]]

@dataclass
class Endpoint:
    apiName: str
    endpointName: str
    method: str
    path: str
    param_space: ParamSpace
