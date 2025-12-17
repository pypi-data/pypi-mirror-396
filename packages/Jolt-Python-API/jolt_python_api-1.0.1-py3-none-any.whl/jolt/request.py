import json

class JoltRequestBuilder:
    
    @staticmethod
    def auth(username: str, password: str) -> str:
        request = {
            "cmd": "auth",
            "user": username,
            "pass": password
        }
        return json.dumps(request)
    
    @staticmethod
    def subscribe(topic: str) -> str:
        request = {
            "cmd": "sub",
            "topic": topic
        }
        return json.dumps(request)
    
    @staticmethod
    def unsubscribe(topic: str) -> str:
        request = {
            "cmd": "unsub",
            "topic": topic
        }
        return json.dumps(request)
    
    @staticmethod
    def publish(topic: str, data: str) -> str:
        request = {
            "cmd": "pub",
            "topic": topic,
            "data": data
        }
        return json.dumps(request)
    
    @staticmethod
    def ping() -> str:
        request = {"cmd": "ping"}
        return json.dumps(request)