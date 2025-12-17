A fast, lightweight Python client for the **Jolt** in-memory messaging broker.

This is a Python port of the [jolt-java-api](https://github.com/Jolt-Database/jolt-java-api), providing identical functionality with a Pythonic interface.

* Plain TCP + NDJSON (newline-delimited JSON)
* No external dependencies (standard library only)
* Supports:
  + `auth` - Authentication
  + `sub` / `unsub` - Subscribe/Unsubscribe to topics
  + `pub` - Publish messages
  + `ping` - Keep-alive
* Designed for low latency and high throughput

---

## 1. Requirements

* Python 3.7 or newer
* A running Jolt server (the Go broker):
  + Example: `./broker -config=config.json`
  + Default port: `8080` (unless changed in `config.json`)

---

## 2. Installation

### From source:

```bash
git clone https://github.com/DevArqf/jolt-python-api.git
cd jolt-python-api
pip install -e .
```

### Using pip:

```bash
pip install jolt-python-api
```

---

## 3. Project Structure

```
jolt-python-api/
├── src/
│   └── jolt/
│       ├── __init__.py
│       ├── client.py          # Main JoltClient class
│       ├── config.py          # JoltConfig and builder
│       ├── handler.py         # JoltMessageHandler abstract class
│       ├── request.py         # JoltRequestBuilder
│       ├── response.py        # Response parsers and models
│       └── exceptions.py      # JoltException
├── examples/
│   └── simple_example.py
├── tests/
├── setup.py
├── README.md
└── requirements.txt
```

---

## 4. Quick Start

### 4.1 Basic Usage

```python
from jolt import JoltClient, JoltConfig, JoltMessageHandler
from jolt import JoltErrorResponse, JoltTopicMessage
from typing import Optional

# 1. Configure connection
config = JoltConfig.new_builder() \
    .host("127.0.0.1") \
    .port(8080) \
    .build()

# 2. Define message handler
class MyHandler(JoltMessageHandler):
    def on_ok(self, raw_line: str):
        print(f"[OK] {raw_line}")
    
    def on_error(self, error: JoltErrorResponse, raw_line: str):
        print(f"[ERROR] {error.get_error()}")
    
    def on_topic_message(self, msg: JoltTopicMessage, raw_line: str):
        print(f"[MSG] {msg.get_topic()} -> {msg.get_data()}")
    
    def on_disconnected(self, cause: Optional[Exception]):
        print(f"[DISCONNECTED] {cause if cause else 'closed'}")

# 3. Create and connect client
handler = MyHandler()
client = JoltClient(config, handler)
client.connect()

# 4. Authenticate (if server requires it)
client.auth("username", "password")

# 5. Subscribe and publish
client.subscribe("chat.room1")
client.publish("chat.room1", "Hello from Python!")

# 6. Ping server
client.ping()

# 7. Clean shutdown
client.close()
```

### 4.2 Complete Example

```python
import time
from jolt import JoltClient, JoltConfig, JoltMessageHandler
from jolt import JoltErrorResponse, JoltTopicMessage
from typing import Optional

class ChatHandler(JoltMessageHandler):
    def on_ok(self, raw_line: str):
        print(f"✓ Operation successful")
    
    def on_error(self, error: JoltErrorResponse, raw_line: str):
        print(f"✗ Error: {error.get_error()}")
    
    def on_topic_message(self, msg: JoltTopicMessage, raw_line: str):
        print(f"📩 [{msg.get_topic()}] {msg.get_data()}")
    
    def on_disconnected(self, cause: Optional[Exception]):
        if cause:
            print(f"⚠ Disconnected: {cause}")
        else:
            print("👋 Connection closed")

def main():
    # Setup
    config = JoltConfig.new_builder() \
        .host("127.0.0.1") \
        .port(8080) \
        .build()
    
    handler = ChatHandler()
    client = JoltClient(config, handler)
    
    try:
        # Connect
        print("🔌 Connecting to Jolt server...")
        client.connect()
        print("✓ Connected!")
        
        # Auth (if needed)
        # client.auth("jolt-chat", "password123")
        
        # Subscribe to topics
        client.subscribe("chat.general")
        client.subscribe("notifications")
        
        # Publish some messages
        client.publish("chat.general", "Hello, everyone!")
        client.publish("chat.general", "This is from Python!")
        
        # Keep running to receive messages
        print("\n📡 Listening for messages (Ctrl+C to exit)...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    finally:
        client.close()

if __name__ == "__main__":
    main()
```

---

## 5. API Reference

### JoltConfig

Configuration object for the Jolt client.

```python
# Using builder pattern
config = JoltConfig.new_builder() \
    .host("127.0.0.1") \
    .port(8080) \
    .build()

# Direct instantiation
config = JoltConfig(host="127.0.0.1", port=8080)
```

**Methods:**
- `get_host()` → `str`: Get the server host
- `get_port()` → `int`: Get the server port

### JoltClient

Main client for interacting with the Jolt broker.

**Constructor:**
```python
client = JoltClient(config: JoltConfig, handler: JoltMessageHandler)
```

**Methods:**
- `connect()`: Connect to the Jolt server
- `auth(username: str, password: str)`: Authenticate with the server
- `subscribe(topic: str)`: Subscribe to a topic
- `unsubscribe(topic: str)`: Unsubscribe from a topic
- `publish(topic: str, data: str)`: Publish a message to a topic
- `ping()`: Send a ping to the server
- `close()`: Close the connection
- `is_connected()` → `bool`: Check connection status

### JoltMessageHandler

Abstract base class for handling server messages. Implement all methods:

```python
class MyHandler(JoltMessageHandler):
    def on_ok(self, raw_line: str):
        """Called when receiving an OK response"""
        pass
    
    def on_error(self, error: JoltErrorResponse, raw_line: str):
        """Called when receiving an error response"""
        pass
    
    def on_topic_message(self, msg: JoltTopicMessage, raw_line: str):
        """Called when receiving a message on a subscribed topic"""
        pass
    
    def on_disconnected(self, cause: Optional[Exception]):
        """Called when disconnected from the server"""
        pass
```

### JoltTopicMessage

Represents a message received on a subscribed topic.

**Methods:**
- `get_topic()` → `str`: Get the topic name
- `get_data()` → `str`: Get the message data

### JoltErrorResponse

Represents an error response from the server.

**Methods:**
- `get_error()` → `str`: Get the error message

### JoltException

Exception raised for Jolt client errors.

---

## 6. Comparison with Java API

This Python implementation maintains feature parity with the Java API:

| Feature | Java API | Python API |
|---------|----------|------------|
| TCP Connection | ✅ | ✅ |
| NDJSON Protocol | ✅ | ✅ |
| Auth | ✅ | ✅ |
| Subscribe/Unsubscribe | ✅ | ✅ |
| Publish | ✅ | ✅ |
| Ping | ✅ | ✅ |
| Message Handler | ✅ | ✅ |
| Thread-safe Writing | ✅ | ✅ |
| Background Reader | ✅ | ✅ |
| No Dependencies | ✅ | ✅ |

**API Naming Conventions:**

The Python API follows Pythonic naming while maintaining similar structure:

- Java: `JoltConfig.newBuilder()` → Python: `JoltConfig.new_builder()`
- Java: `error.getError()` → Python: `error.get_error()`
- Java: `msg.getTopic()` → Python: `msg.get_topic()`

---

## 7. Advanced Usage

### Multiple Topics

```python
topics = ["news", "sports", "weather"]
for topic in topics:
    client.subscribe(topic)

# Publish to different topics
client.publish("news", "Breaking: Python API released!")
client.publish("sports", "Game score: 3-2")
```

### Topic-Specific Handlers

```python
class SmartHandler(JoltMessageHandler):
    def on_topic_message(self, msg: JoltTopicMessage, raw_line: str):
        topic = msg.get_topic()
        data = msg.get_data()
        
        if topic.startswith("alert."):
            print(f"🚨 ALERT: {data}")
        elif topic.startswith("chat."):
            print(f"💬 Chat: {data}")
        else:
            print(f"📨 {topic}: {data}")
```

### Reconnection Logic

```python
import time

class ReconnectingHandler(JoltMessageHandler):
    def __init__(self, client):
        self.client = client
        self.should_reconnect = True
    
    def on_disconnected(self, cause: Optional[Exception]):
        print(f"Disconnected: {cause}")
        if self.should_reconnect:
            print("Attempting to reconnect...")
            time.sleep(5)
            try:
                self.client.connect()
                print("Reconnected!")
            except Exception as e:
                print(f"Reconnection failed: {e}")
```

---

## 8. Notes

* This API does **not** provide TLS. To secure transport:
  + Run Jolt behind a TLS-terminating proxy (e.g. Nginx, HAProxy), or
  + Use OS-level tunnels (SSH, VPN)
* All JSON is handled using Python's built-in `json` module
* The client uses a single background thread for reading and a thread-safe writer
* Messages are automatically framed with newlines (NDJSON format)

---

## 9. Testing

Run tests (when implemented):

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=jolt tests/
```

---

## 10. Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 11. License

MIT License

Copyright (c) 2025 DevArqf

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 12. Credits

This is a Python port of the [jolt-java-api](https://github.com/Jolt-Database/jolt-java-api) created for the [Jolt Database](https://github.com/Jolt-Database) project.

---

## 13. Support

For issues, questions, or contributions:
- Open an issue
- Contact the Jolt Database team