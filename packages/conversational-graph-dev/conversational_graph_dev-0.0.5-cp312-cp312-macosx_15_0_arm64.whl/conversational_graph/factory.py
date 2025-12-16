from abc import ABC
from typing import Literal
from pydantic import BaseModel
from ._internal.factory import ConversationGraphEngine
from ._internal.tools import PreDefinedToolEngine,DataModel,AuthDetails

class ConversationGraph(ABC):
    """
    Public interface for the Conversation Graph.
    """
    
    def __new__(cls, name: str, DataModel: BaseModel = None, off_topic_threshold: int = 5, graph_type: Literal["STRICT"] = "STRICT"):
        return ConversationGraphEngine(name, DataModel, off_topic_threshold, graph_type)


class PreDefinedTool(ABC):
    """
    Public interface for PreDefined Tools in the Conversation Graph.
    """
    
    def __new__(cls):
        return PreDefinedToolEngine()

class ToolAuthDetails(ABC):
    """
    Public interface for Auth Details in the Conversation Graph.
    """
    
    def __new__(cls, enabled: bool, type: Literal["bearer","basic"] = "bearer", token: str = ""):
        return AuthDetails(enabled=enabled, type=type, token=token)

class ConversationDataModel(ABC):
    """
    Public interface for Data Models in the Conversation Graph.
    """
    
    def __new__(cls, **data):
        return DataModel(**data)
