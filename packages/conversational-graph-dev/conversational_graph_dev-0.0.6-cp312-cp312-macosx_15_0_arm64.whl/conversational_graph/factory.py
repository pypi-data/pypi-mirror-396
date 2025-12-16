from abc import ABC
from typing import Literal
from pydantic import BaseModel
from ._internal.factory import ConversationalGraphEngine
from ._internal.tools import PreDefinedToolEngine,DataModel,AuthDetails, HttpRequestTool

class ConversationalGraph(ABC):
    """
    Public interface for the Conversational Graph.
    """
    
    def __new__(cls, name: str, DataModel: BaseModel = None, off_topic_threshold: int = 5, graph_type: Literal["STRICT"] = "STRICT"):
        return ConversationalGraphEngine(name, DataModel, off_topic_threshold, graph_type)


class PreDefinedTool(ABC):
    """
    Public interface for PreDefined Tools in the Conversational Graph.
    """
    
    def __new__(cls):
        return PreDefinedToolEngine()

class HTTPRequestTool(ABC):
    """
    Public interface for HTTP Tools Request in the Conversational Graph.
    """
    
    def __new__(cls, name:str, description:str, url:str, method:Literal["GET","POST"] = "GET", auth:AuthDetails = None, params:dict = None,payload:dict = None):
        return HttpRequestTool(name=name, description=description, url=url, method=method, auth=auth, params=params, payload=payload)

class ToolAuthDetails(ABC):
    """
    Public interface for Auth Details for HTTP Tools in the Conversational Graph.
    """
    
    def __new__(cls, enabled: bool, auth_type: Optional[Literal["bearer","basic"]] = None, token: Optional[str] = None):
        return AuthDetails(enabled=enabled, auth_type=auth_type, token=token)

class ConversationDataModel(ABC):
    """
    Public interface for Data Models for the Conversational Graph.
    """
    
    def __new__(cls, **data):
        return DataModel(**data)
