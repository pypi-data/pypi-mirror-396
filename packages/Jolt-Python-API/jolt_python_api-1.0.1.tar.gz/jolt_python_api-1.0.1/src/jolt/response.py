import json
from typing import Dict, Any
from .exceptions import JoltException

class JoltErrorResponse:
    
    def __init__(self, error: str):
        self._error = error
    
    def get_error(self) -> str:
        return self._error
    
    def __str__(self) -> str:
        return f"JoltErrorResponse(error={self._error})"
    
    def __repr__(self) -> str:
        return self.__str__()


class JoltTopicMessage:
    
    def __init__(self, topic: str, data: str):
        self._topic = topic
        self._data = data
    
    def get_topic(self) -> str:
        return self._topic
    
    def get_data(self) -> str:
        return self._data
    
    def __str__(self) -> str:
        return f"JoltTopicMessage(topic={self._topic}, data={self._data})"
    
    def __repr__(self) -> str:
        return self.__str__()


class JoltResponseParser:
    
    @staticmethod
    def parse(raw_line: str) -> Dict[str, Any]:
        try:
            return json.loads(raw_line)
        except json.JSONDecodeError as e:
            raise JoltException(f"Failed to parse JSON: {e}")
    
    @staticmethod
    def parse_error_response(data: Dict[str, Any]) -> JoltErrorResponse:
        error_msg = data.get("error", "Unknown error")
        return JoltErrorResponse(error_msg)
    
    @staticmethod
    def parse_topic_message(data: Dict[str, Any]) -> JoltTopicMessage:
        topic = data.get("topic", "")
        msg_data = data.get("data", "")
        return JoltTopicMessage(topic, msg_data)