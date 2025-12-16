# ai-common

**Production-Grade Utilities for AI/ML Applications**

`ai-common` is a comprehensive library designed to standardize logging, exception handling, and configuration management across Python AI projects. It ensures observability, consistency, and reliability.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **JSON Logging** | Structured logging output compatible with Splunk, Datadog, ELK, etc. |
| **Context Injection** | Automatically include `request_id`, `user_id` in logs via context propagation. |
| **Unified Exceptions** | Standardized `AppException` hierarchy with HTTP status codes and error codes. |
| **Config Loader** | Robust YAML configuration loader with validation and custom exceptions. |
| **Model Loader** | Generic loader for LLMs and Embeddings (Google, Groq) with API key management. |


## 🧠 Model Loader Usage

`ai-common` now includes a generic `ModelLoader` to simplify initializing Language Models and Embeddings.

```python
from ai_common.model_loader import ModelLoader

# 1. Initialize Loader
# Tries to load config from path, or uses defaults/env vars
loader = ModelLoader(config_path="config.yaml")

# 2. Get LLM (defaults to Google Gemini if not specified)
llm = loader.load_llm(provider="google", model_name="gemini-pro")

# 3. Get Embeddings
embeddings = loader.load_embeddings()
```

### Supported Providers
- **Google Generative AI**: LLM (`gemini-pro`) & Embeddings (`models/embedding-001`)
- **Groq**: LPU Inference Engine (e.g., `mixtral-8x7b-32768`)
- **Custom**: Easily extendable via `BaseProvider`.

### Extending Support (Adding Custom Providers)

You can plug in any model provider (e.g., OpenAI, Anthropic, Custom Local Models) by extending `BaseProvider`.

```python
from ai_common.model_loader import BaseProvider, ApiKeyManager

class MyCustomProvider(BaseProvider):
    def load_llm(self, api_key_mgr: ApiKeyManager, config: dict, **kwargs):
        # Initialize your custom LLM here
        return MyLLM(api_key=api_key_mgr.get("MY_KEY"))

    def load_embedding(self, api_key_mgr: ApiKeyManager, config: dict, **kwargs):
        return MyEmbeddings()

# Register it
loader = ModelLoader(config_path="config.yaml")
loader.register_provider("my_provider", MyCustomProvider())

# Use it
llm = loader.load_llm(provider="my_provider")
```

**Environment Variables:**
- `GOOGLE_API_KEY`
- `GROQ_API_KEY`
- `API_KEYS`: JSON string for loading multiple keys (optional).

---

## 📦 Installation

```bash
pip install nishkoder-ai-common
```

---

## 🛠 Quick Start

### Logging
```python
from ai_common.logger.custom_logger import logger

# Basic Info Log
logger.info("Application started", extra={"env": "production"})
```

### Configuration
```python
from ai_common.utils import load_config
from ai_common.exception.custom_exception import ConfigException

try:
    config = load_config("config.yaml")
    print(config['db_host'])
except ConfigException as e:
    logger.error(f"Config error: {e}")
```

---

## 📚 API Reference

### 1. Logging Module (`ai_common.logger`)

**Import:** `from ai_common.logger import ...`

| Component | Type | Signature | Description |
| :--- | :--- | :--- | :--- |
| `logger` | `logging.Logger` | N/A | Pre-configured JSON logger instance. Use this for general logging. |
| `get_logger` | `Function` | `(name="app") -> Logger` | Factory to create a new logger instance with JSON formatting. |
| `add_context` | `Function` | `(logger, **kwargs) -> LoggerAdapter` | Wraps a logger to inject context (e.g., `request_id`) into every log message. |

### 2. Utilities Module (`ai_common`)

**Import:** `from ai_common.utils import ...`

| Function | Signature | Description |
| :--- | :--- | :--- |
| `load_config` | `(config_path: str) -> Dict` | Loads a YAML file into a dictionary. Raises `ConfigException` if invalid. |
| `generate_session_id` | `() -> str` | Generates a unique session identifier string formatted as `session_YYYYMMDD_HHMMSS_<8-char-uuid>`. |

### 3. Exception Handling (`ai_common.exception`)

**Import:** `from ai_common.exception.custom_exception import ...`

All exceptions inherit from `AppException` and contain `code`, `message`, and `details`.

#### Base Class
| Class | Description | Method `to_dict()` |
| :--- | :--- | :--- |
| `AppException` | Base exception class for all application errors. | Returns `{"error": {"code": "...", "message": "...", "details": ...}}` |

#### Standard Exceptions
| Exception Name | HTTP Code | Error Code | Usage Scenario |
| :--- | :--- | :--- | :--- |
| `ResourceNotFoundException` | `404` | `RESOURCE_NOT_FOUND` | When a requested entity (user, file, doc) is missing. |
| `ValidationException` | `400` | `VALIDATION_ERROR` | When input data fails validation checks. |
| `AuthenticationException` | `401` | `AUTHENTICATION_FAILED` | When auth credentials are missing or invalid. |
| `PermissionDeniedException` | `403` | `PERMISSION_DENIED` | When user is authenticated but lacks permissions. |
| `DatabaseException` | `500` | `DATABASE_ERROR` | Wrapper for DB connectivity or query errors. |
| `ConfigException` | `500` | `CONFIGURATION_ERROR` | Errors related to loading or parsing configuration files. |

---

## 📝 Changelog

| Version | Date | Changes |
| :--- | :--- | :--- |
| **v0.1.4** | *Current* | • Added `generate_session_id` utility to `ai_common.utils` for unique session IDs. |
| **v0.1.3** | *Previous* | • Refactored `ModelLoader` to use `BaseProvider` pattern for extensibility. |
| **v0.1.2** | *Previous* | • Added `ai_common.model_loader`.<br>• Introduced `ModelLoader` & `ApiKeyManager`.<br>• Added `ModelException`. |
| **v0.1.1** | *Previous* | • Added `ai_common.utils` module.<br>• Added `load_config` function.<br>• Added `ConfigException`. |
| **v0.1.0** | *Initial* | • Initial release with `custom_logger` and basic `AppException` hierarchy. |

---

## License

MIT License
