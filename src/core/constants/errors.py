"""
Error definition module

Contains unified definitions of all error codes, error messages, and translations
"""

from enum import Enum
from typing import Dict


class ErrorStatus(Enum):
    """Error status enumeration

    Defines all possible error statuses in the system, facilitating error classification and handling.
    Each error status has a clear meaning and corresponding handling method.
    """

    OK = "ok"
    FAILED = "failed"


class ErrorCode(Enum):
    """Error code enumeration

    Defines all possible error codes in the system, facilitating error classification and handling.
    Each error code has a clear meaning and corresponding handling method.
    """

    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_INVALID = "RESOURCE_INVALID"
    TYPE_ERROR = "TYPE_ERROR"
    OPERATION_FAILED = "OPERATION_FAILED"

    # Authentication related errors
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    TOKEN_INVALID = "TOKEN_INVALID"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    PERMISSION_INSUFFICIENT = "PERMISSION_INSUFFICIENT"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_INVALID = "USER_INVALID"

    # Agent related errors
    AGENT_INITIALIZATION_ERROR = "AGENT_INITIALIZATION_ERROR"
    AGENT_EXECUTION_ERROR = "AGENT_EXECUTION_ERROR"
    AGENT_STATE_ERROR = "AGENT_STATE_ERROR"
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    AGENT_CANCELLED = "AGENT_CANCELLED"
    AGENT_MEMORY_ERROR = "AGENT_MEMORY_ERROR"

    # Database related errors
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    DATABASE_TRANSACTION_ERROR = "DATABASE_TRANSACTION_ERROR"
    DATABASE_CONSTRAINT_ERROR = "DATABASE_CONSTRAINT_ERROR"
    DATABASE_TIMEOUT = "DATABASE_TIMEOUT"

    # File related errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_READ_ERROR = "FILE_READ_ERROR"
    FILE_WRITE_ERROR = "FILE_WRITE_ERROR"
    FILE_PERMISSION_ERROR = "FILE_PERMISSION_ERROR"
    FILE_FORMAT_ERROR = "FILE_FORMAT_ERROR"
    FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    FILE_DOWNLOAD_FAILED = "FILE_DOWNLOAD_FAILED"
    FILE_PARSE_ERROR = "FILE_PARSE_ERROR"

    # Network related errors
    NETWORK_ERROR = "NETWORK_ERROR"
    HTTP_REQUEST_ERROR = "HTTP_REQUEST_ERROR"
    HTTP_TIMEOUT = "HTTP_TIMEOUT"
    URL_INVALID = "URL_INVALID"
    URL_SHORTENING_FAILED = "URL_SHORTENING_FAILED"

    # External service errors
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    EXTERNAL_SERVICE_TIMEOUT = "EXTERNAL_SERVICE_TIMEOUT"
    EXTERNAL_SERVICE_UNAVAILABLE = "EXTERNAL_SERVICE_UNAVAILABLE"
    API_RATE_LIMIT_EXCEEDED = "API_RATE_LIMIT_EXCEEDED"
    API_KEY_INVALID = "API_KEY_INVALID"

    # Configuration related errors
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    CONFIGURATION_INVALID = "CONFIGURATION_INVALID"
    CONFIGURATION_MISSING = "CONFIGURATION_MISSING"
    ENVIRONMENT_VARIABLE_MISSING = "ENVIRONMENT_VARIABLE_MISSING"

    # Generation related errors
    GENERATION_ERROR = "GENERATION_ERROR"
    GENERATION_TIMEOUT = "GENERATION_TIMEOUT"
    GENERATION_CANCELLED = "GENERATION_CANCELLED"
    GENERATION_IN_PROGRESS = "GENERATION_IN_PROGRESS"
    GENERATION_QUEUE_FULL = "GENERATION_QUEUE_FULL"

    # Conversation related errors
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    CONVERSATION_INVALID = "CONVERSATION_INVALID"
    CONVERSATION_TYPE_INVALID = "CONVERSATION_TYPE_INVALID"
    CONVERSATION_LIMIT_EXCEEDED = "CONVERSATION_LIMIT_EXCEEDED"
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"

    # Content related errors
    CONTENT_EMPTY = "CONTENT_EMPTY"
    CONTENT_TOO_LONG = "CONTENT_TOO_LONG"
    CONTENT_INVALID_FORMAT = "CONTENT_INVALID_FORMAT"
    CONTENT_PROCESSING_ERROR = "CONTENT_PROCESSING_ERROR"

    # Resource related errors
    RESOURCE_PROCESSING_FAILED = "RESOURCE_PROCESSING_FAILED"
    RESOURCE_EXTRACTION_FAILED = "RESOURCE_EXTRACTION_FAILED"
    RESOURCE_IMPORT_FAILED = "RESOURCE_IMPORT_FAILED"
    RESOURCE_URI_MISSING = "RESOURCE_URI_MISSING"

    # System errors
    SYSTEM_ERROR = "SYSTEM_ERROR"
    INITIALIZATION_FAILED = "INITIALIZATION_FAILED"
    SERVICE_STARTUP_FAILED = "SERVICE_STARTUP_FAILED"
    SERVICE_SHUTDOWN_FAILED = "SERVICE_SHUTDOWN_FAILED"

    # Context and session errors
    CONTEXT_NOT_SET = "CONTEXT_NOT_SET"
    SESSION_NOT_INITIALIZED = "SESSION_NOT_INITIALIZED"
    MIDDLEWARE_ERROR = "MIDDLEWARE_ERROR"

    # Workflow stage related error codes
    REQUIREMENT_EXTRACTION_NOT_COMPLETED = "REQUIREMENT_EXTRACTION_NOT_COMPLETED"
    OUTLINE_GENERATION_NOT_COMPLETED = "OUTLINE_GENERATION_NOT_COMPLETED"
    OUTLINE_ID_NOT_FOUND = "OUTLINE_ID_NOT_FOUND"
    FULLTEXT_ID_NOT_FOUND = "FULLTEXT_ID_NOT_FOUND"
    DOCUMENT_SLICE_NOT_FOUND = "DOCUMENT_SLICE_NOT_FOUND"

    # Task related error codes
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    NO_GENERATION_IN_PROGRESS = "NO_GENERATION_IN_PROGRESS"

    # Editor related error codes
    UNSUPPORTED_EDITOR_TYPE = "UNSUPPORTED_EDITOR_TYPE"

    # Agent specific error codes
    LLM_OUTPUT_PARSING_ERROR = "LLM_OUTPUT_PARSING_ERROR"
    LLM_CALL_FAILED = "LLM_CALL_FAILED"
    LLM_RETRY_EXHAUSTED = "LLM_RETRY_EXHAUSTED"

    # Quota related error codes
    QUOTA_INSUFFICIENT = "QUOTA_INSUFFICIENT"


class ErrorMessage(Enum):
    """Error message key enumeration

    Defines all error message keys in the system, used for frontend internationalization translation.
    Each message key corresponds to a specific error description.
    """

    # General error messages
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_INVALID = "RESOURCE_INVALID"
    TYPE_ERROR = "TYPE_ERROR"
    OPERATION_FAILED = "OPERATION_FAILED"

    # Authentication related error messages
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    TOKEN_INVALID = "TOKEN_INVALID"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    PERMISSION_INSUFFICIENT = "PERMISSION_INSUFFICIENT"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_INVALID = "USER_INVALID"

    # Agent related error messages
    AGENT_INITIALIZATION_ERROR = "AGENT_INITIALIZATION_ERROR"
    AGENT_EXECUTION_ERROR = "AGENT_EXECUTION_ERROR"
    AGENT_STATE_ERROR = "AGENT_STATE_ERROR"
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    AGENT_CANCELLED = "AGENT_CANCELLED"
    AGENT_MEMORY_ERROR = "AGENT_MEMORY_ERROR"

    # Database related error messages
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    DATABASE_TRANSACTION_ERROR = "DATABASE_TRANSACTION_ERROR"
    DATABASE_CONSTRAINT_ERROR = "DATABASE_CONSTRAINT_ERROR"
    DATABASE_TIMEOUT = "DATABASE_TIMEOUT"

    # File related error messages
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_READ_ERROR = "FILE_READ_ERROR"
    FILE_WRITE_ERROR = "FILE_WRITE_ERROR"
    FILE_PERMISSION_ERROR = "FILE_PERMISSION_ERROR"
    FILE_FORMAT_ERROR = "FILE_FORMAT_ERROR"
    FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    FILE_DOWNLOAD_FAILED = "FILE_DOWNLOAD_FAILED"
    FILE_PARSE_ERROR = "FILE_PARSE_ERROR"

    # Network related error messages
    NETWORK_ERROR = "NETWORK_ERROR"
    HTTP_REQUEST_ERROR = "HTTP_REQUEST_ERROR"
    HTTP_TIMEOUT = "HTTP_TIMEOUT"
    URL_INVALID = "URL_INVALID"
    URL_SHORTENING_FAILED = "URL_SHORTENING_FAILED"

    # External service error messages
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    EXTERNAL_SERVICE_TIMEOUT = "EXTERNAL_SERVICE_TIMEOUT"
    EXTERNAL_SERVICE_UNAVAILABLE = "EXTERNAL_SERVICE_UNAVAILABLE"
    API_RATE_LIMIT_EXCEEDED = "API_RATE_LIMIT_EXCEEDED"
    API_KEY_INVALID = "API_KEY_INVALID"

    # Configuration related error messages
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    CONFIGURATION_INVALID = "CONFIGURATION_INVALID"
    CONFIGURATION_MISSING = "CONFIGURATION_MISSING"
    ENVIRONMENT_VARIABLE_MISSING = "ENVIRONMENT_VARIABLE_MISSING"

    # Generation related error messages
    GENERATION_ERROR = "GENERATION_ERROR"
    GENERATION_TIMEOUT = "GENERATION_TIMEOUT"
    GENERATION_CANCELLED = "GENERATION_CANCELLED"
    GENERATION_IN_PROGRESS = "GENERATION_IN_PROGRESS"
    GENERATION_QUEUE_FULL = "GENERATION_QUEUE_FULL"
    NO_GENERATION_IN_PROGRESS = "NO_GENERATION_IN_PROGRESS"

    # Conversation related error messages
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    CONVERSATION_INVALID = "CONVERSATION_INVALID"
    CONVERSATION_TYPE_INVALID = "CONVERSATION_TYPE_INVALID"
    CONVERSATION_LIMIT_EXCEEDED = "CONVERSATION_LIMIT_EXCEEDED"
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
    CONVERSATION_ACCESS_DENIED = "CONVERSATION_ACCESS_DENIED"
    CONVERSATION_GET_FAILED = "CONVERSATION_GET_FAILED"
    CONVERSATION_DELETE_FAILED = "CONVERSATION_DELETE_FAILED"
    CONVERSATION_LIST_GET_FAILED = "CONVERSATION_LIST_GET_FAILED"

    # Content related error messages
    CONTENT_EMPTY = "CONTENT_EMPTY"
    CONTENT_TOO_LONG = "CONTENT_TOO_LONG"
    CONTENT_INVALID_FORMAT = "CONTENT_INVALID_FORMAT"
    CONTENT_PROCESSING_ERROR = "CONTENT_PROCESSING_ERROR"

    # Workflow stage related error messages
    REQUIREMENT_EXTRACTION_NOT_COMPLETED = "REQUIREMENT_EXTRACTION_NOT_COMPLETED"
    OUTLINE_GENERATION_NOT_COMPLETED = "OUTLINE_GENERATION_NOT_COMPLETED"
    OUTLINE_ID_NOT_FOUND = "OUTLINE_ID_NOT_FOUND"
    FULLTEXT_ID_NOT_FOUND = "FULLTEXT_ID_NOT_FOUND"
    DOCUMENT_SLICE_NOT_FOUND = "DOCUMENT_SLICE_NOT_FOUND"

    # Editor and interface related error messages
    UNSUPPORTED_EDITOR_TYPE = "UNSUPPORTED_EDITOR_TYPE"
    BEAN_NOT_FOUND = "BEAN_NOT_FOUND"
    BEAN_OPERATION_FAILED = "BEAN_OPERATION_FAILED"

    # Filename and size related error messages
    FILENAME_EMPTY = "FILENAME_EMPTY"

    # Document version related error messages
    DOCUMENT_VERSION_NOT_FOUND = "DOCUMENT_VERSION_NOT_FOUND"
    DOCUMENT_VERSION_CREATE_FAILED = "DOCUMENT_VERSION_CREATE_FAILED"
    DOCUMENT_VERSION_UPDATE_FAILED = "DOCUMENT_VERSION_UPDATE_FAILED"
    DOCUMENT_VERSION_DELETE_FAILED = "DOCUMENT_VERSION_DELETE_FAILED"
    DOCUMENT_VERSION_GET_FAILED = "DOCUMENT_VERSION_GET_FAILED"
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"

    # Service related error messages
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    ANALYSIS_EXECUTION_FAILED = "ANALYSIS_EXECUTION_FAILED"

    # Task related error messages
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_CREATE_FAILED = "TASK_CREATE_FAILED"
    TASK_GET_FAILED = "TASK_GET_FAILED"
    TASK_LIST_GET_FAILED = "TASK_LIST_GET_FAILED"
    TASK_CANCEL_FAILED = "TASK_CANCEL_FAILED"
    TASK_DELETE_FAILED = "TASK_DELETE_FAILED"
    TASK_STATS_GET_FAILED = "TASK_STATS_GET_FAILED"
    TASK_REGISTERED_GET_FAILED = "TASK_REGISTERED_GET_FAILED"
    TASK_CANNOT_CANCEL = "TASK_CANNOT_CANCEL"
    TASK_CANNOT_DELETE_RUNNING = "TASK_CANNOT_DELETE_RUNNING"

    # Search related error messages
    SEARCH_QUERY_EMPTY = "SEARCH_QUERY_EMPTY"
    AI_SEARCH_FAILED = "AI_SEARCH_FAILED"
    QUICK_SEARCH_FAILED = "QUICK_SEARCH_FAILED"
    SEARCH_SUGGESTIONS_FAILED = "SEARCH_SUGGESTIONS_FAILED"
    SEARCH_TAGS_FAILED = "SEARCH_TAGS_FAILED"

    # Resource related error messages
    RESOURCE_PROCESSING_FAILED = "RESOURCE_PROCESSING_FAILED"
    RESOURCE_EXTRACTION_FAILED = "RESOURCE_EXTRACTION_FAILED"
    RESOURCE_IMPORT_FAILED = "RESOURCE_IMPORT_FAILED"
    RESOURCE_URI_MISSING = "RESOURCE_URI_MISSING"
    RESOURCE_UPLOAD_FAILED = "RESOURCE_UPLOAD_FAILED"
    RESOURCE_BIND_FAILED = "RESOURCE_BIND_FAILED"
    RESOURCE_LIST_GET_FAILED = "RESOURCE_LIST_GET_FAILED"
    RESOURCE_STATUS_GET_FAILED = "RESOURCE_STATUS_GET_FAILED"
    RESOURCE_CITATION_GET_FAILED = "RESOURCE_CITATION_GET_FAILED"
    RESOURCE_GET_FAILED = "RESOURCE_GET_FAILED"
    RESOURCE_NO_FILE = "RESOURCE_NO_FILE"
    RESOURCE_DOWNLOAD_FAILED = "RESOURCE_DOWNLOAD_FAILED"
    RESOURCE_DELETE_FAILED = "RESOURCE_DELETE_FAILED"
    INSPIRATION_CREATE_FAILED = "INSPIRATION_CREATE_FAILED"
    INSPIRATION_NOT_FOUND = "INSPIRATION_NOT_FOUND"
    INSPIRATION_TYPE_INVALID = "INSPIRATION_TYPE_INVALID"
    INSPIRATION_UPDATE_FAILED = "INSPIRATION_UPDATE_FAILED"
    INSPIRATION_LIST_GET_FAILED = "INSPIRATION_LIST_GET_FAILED"
    INSPIRATION_GET_FAILED = "INSPIRATION_GET_FAILED"
    RESOURCE_TYPE_GET_FAILED = "RESOURCE_TYPE_GET_FAILED"
    RESOURCE_SCOPE_GET_FAILED = "RESOURCE_SCOPE_GET_FAILED"
    RESOURCE_PROCESSING_STATUS_GET_FAILED = "RESOURCE_PROCESSING_STATUS_GET_FAILED"
    RESOURCE_SIGNED_URL_FAILED = "RESOURCE_SIGNED_URL_FAILED"

    # System error messages
    SYSTEM_ERROR = "SYSTEM_ERROR"
    INITIALIZATION_FAILED = "INITIALIZATION_FAILED"
    SERVICE_STARTUP_FAILED = "SERVICE_STARTUP_FAILED"
    SERVICE_SHUTDOWN_FAILED = "SERVICE_SHUTDOWN_FAILED"

    # Context and session error messages
    CONTEXT_NOT_SET = "CONTEXT_NOT_SET"
    SESSION_NOT_INITIALIZED = "SESSION_NOT_INITIALIZED"
    MIDDLEWARE_ERROR = "MIDDLEWARE_ERROR"

    # LLM related error messages
    LLM_OUTPUT_PARSING_ERROR = "LLM_OUTPUT_PARSING_ERROR"
    LLM_CALL_FAILED = "LLM_CALL_FAILED"
    LLM_RETRY_EXHAUSTED = "LLM_RETRY_EXHAUSTED"

    # Quota related error messages
    QUOTA_INSUFFICIENT = "QUOTA_INSUFFICIENT"


# ErrorCode translation dictionary
ERROR_CODE_TRANSLATIONS_ZH: Dict[str, str] = {
    # General errors
    ErrorCode.UNKNOWN_ERROR.value: "Unknown error",
    ErrorCode.HTTP_ERROR.value: "HTTP error",
    ErrorCode.INVALID_PARAMETER.value: "Invalid parameter",
    ErrorCode.RESOURCE_NOT_FOUND.value: "Resource not found",
    ErrorCode.PERMISSION_DENIED.value: "Permission denied",
    ErrorCode.VALIDATION_ERROR.value: "Validation failed",
    ErrorCode.RESOURCE_INVALID.value: "Invalid resource",
    ErrorCode.TYPE_ERROR.value: "Type error",
    ErrorCode.OPERATION_FAILED.value: "Operation failed",
    # Authentication related errors
    ErrorCode.AUTHENTICATION_ERROR.value: "Authentication error",
    ErrorCode.AUTHENTICATION_FAILED.value: "Authentication failed",
    ErrorCode.TOKEN_INVALID.value: "Invalid token",
    ErrorCode.TOKEN_EXPIRED.value: "Token expired",
    ErrorCode.PERMISSION_INSUFFICIENT.value: "Insufficient permissions",
    ErrorCode.USER_NOT_FOUND.value: "User not found",
    ErrorCode.USER_INVALID.value: "Invalid user information",
    # Agent related errors
    ErrorCode.AGENT_INITIALIZATION_ERROR.value: "Agent initialization error",
    ErrorCode.AGENT_EXECUTION_ERROR.value: "Agent execution error",
    ErrorCode.AGENT_STATE_ERROR.value: "Agent state error",
    ErrorCode.AGENT_TIMEOUT.value: "Agent timeout",
    ErrorCode.AGENT_CANCELLED.value: "Agent cancelled",
    ErrorCode.AGENT_MEMORY_ERROR.value: "Agent memory error",
    # Database related errors
    ErrorCode.DATABASE_ERROR.value: "Database error",
    ErrorCode.DATABASE_CONNECTION_ERROR.value: "Database connection error",
    ErrorCode.DATABASE_QUERY_ERROR.value: "Database query error",
    ErrorCode.DATABASE_TRANSACTION_ERROR.value: "Database transaction error",
    ErrorCode.DATABASE_CONSTRAINT_ERROR.value: "Database constraint error",
    ErrorCode.DATABASE_TIMEOUT.value: "Database timeout",
    # File related errors
    ErrorCode.FILE_NOT_FOUND.value: "File not found",
    ErrorCode.FILE_READ_ERROR.value: "File read error",
    ErrorCode.FILE_WRITE_ERROR.value: "File write error",
    ErrorCode.FILE_PERMISSION_ERROR.value: "File permission error",
    ErrorCode.FILE_FORMAT_ERROR.value: "File format error",
    ErrorCode.FILE_SIZE_EXCEEDED.value: "File size exceeded",
    ErrorCode.FILE_UPLOAD_FAILED.value: "File upload failed",
    ErrorCode.FILE_DOWNLOAD_FAILED.value: "File download failed",
    ErrorCode.FILE_PARSE_ERROR.value: "File parse error",
    # Network related errors
    ErrorCode.NETWORK_ERROR.value: "Network error",
    ErrorCode.HTTP_REQUEST_ERROR.value: "HTTP request error",
    ErrorCode.HTTP_TIMEOUT.value: "HTTP timeout",
    ErrorCode.URL_INVALID.value: "Invalid URL",
    ErrorCode.URL_SHORTENING_FAILED.value: "URL shortening failed",
    # External service errors
    ErrorCode.EXTERNAL_SERVICE_ERROR.value: "External service error",
    ErrorCode.EXTERNAL_SERVICE_TIMEOUT.value: "External service timeout",
    ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE.value: "External service unavailable",
    ErrorCode.API_RATE_LIMIT_EXCEEDED.value: "API rate limit exceeded",
    ErrorCode.API_KEY_INVALID.value: "Invalid API key",
    # Configuration related errors
    ErrorCode.CONFIGURATION_ERROR.value: "Configuration error",
    ErrorCode.CONFIGURATION_INVALID.value: "Invalid configuration",
    ErrorCode.CONFIGURATION_MISSING.value: "Configuration missing",
    ErrorCode.ENVIRONMENT_VARIABLE_MISSING.value: "Environment variable missing",
    # Generation related errors
    ErrorCode.GENERATION_ERROR.value: "Generation error",
    ErrorCode.GENERATION_TIMEOUT.value: "Generation timeout",
    ErrorCode.GENERATION_CANCELLED.value: "Generation cancelled",
    ErrorCode.GENERATION_IN_PROGRESS.value: "Generation in progress",
    ErrorCode.GENERATION_QUEUE_FULL.value: "Generation queue full",
    # Conversation related errors
    ErrorCode.CONVERSATION_NOT_FOUND.value: "Conversation not found",
    ErrorCode.CONVERSATION_INVALID.value: "Invalid conversation",
    ErrorCode.CONVERSATION_LIMIT_EXCEEDED.value: "Conversation limit exceeded",
    ErrorCode.MESSAGE_TOO_LONG.value: "Message too long",
    # Content related errors
    ErrorCode.CONTENT_EMPTY.value: "Content empty",
    ErrorCode.CONTENT_TOO_LONG.value: "Content too long",
    ErrorCode.CONTENT_INVALID_FORMAT.value: "Invalid content format",
    ErrorCode.CONTENT_PROCESSING_ERROR.value: "Content processing error",
    # Resource related errors
    ErrorCode.RESOURCE_PROCESSING_FAILED.value: "Resource processing failed",
    ErrorCode.RESOURCE_EXTRACTION_FAILED.value: "Resource extraction failed",
    ErrorCode.RESOURCE_IMPORT_FAILED.value: "Resource import failed",
    ErrorCode.RESOURCE_URI_MISSING.value: "Resource URI missing",
    # System errors
    ErrorCode.SYSTEM_ERROR.value: "System error",
    ErrorCode.INITIALIZATION_FAILED.value: "Initialization failed",
    ErrorCode.SERVICE_STARTUP_FAILED.value: "Service startup failed",
    ErrorCode.SERVICE_SHUTDOWN_FAILED.value: "Service shutdown failed",
    # Context and session errors
    ErrorCode.CONTEXT_NOT_SET.value: "Context not set",
    ErrorCode.SESSION_NOT_INITIALIZED.value: "Session not initialized",
    ErrorCode.MIDDLEWARE_ERROR.value: "Middleware error",
    # Workflow stage related error codes
    ErrorCode.CONVERSATION_TYPE_INVALID.value: "Invalid conversation type",
    ErrorCode.REQUIREMENT_EXTRACTION_NOT_COMPLETED.value: "Requirement extraction not completed",
    ErrorCode.OUTLINE_GENERATION_NOT_COMPLETED.value: "Outline generation not completed",
    ErrorCode.OUTLINE_ID_NOT_FOUND.value: "Outline ID not found",
    ErrorCode.FULLTEXT_ID_NOT_FOUND.value: "Fulltext ID not found",
    ErrorCode.DOCUMENT_SLICE_NOT_FOUND.value: "Document slice not found",
    # Task related error codes
    ErrorCode.TASK_NOT_FOUND.value: "Task not found",
    ErrorCode.NO_GENERATION_IN_PROGRESS.value: "No generation in progress",
    # Editor related error codes
    ErrorCode.UNSUPPORTED_EDITOR_TYPE.value: "Unsupported editor type",
    # Agent specific error codes
    ErrorCode.LLM_OUTPUT_PARSING_ERROR.value: "LLM output parsing failed",
    ErrorCode.LLM_CALL_FAILED.value: "LLM call failed",
    ErrorCode.LLM_RETRY_EXHAUSTED.value: "LLM retry attempts exhausted",
    # Quota related error codes
    ErrorCode.QUOTA_INSUFFICIENT.value: "Quota insufficient",
}

ERROR_CODE_TRANSLATIONS_EN: Dict[str, str] = {
    # General errors
    ErrorCode.UNKNOWN_ERROR.value: "Unknown error",
    ErrorCode.HTTP_ERROR.value: "HTTP error",
    ErrorCode.INVALID_PARAMETER.value: "Invalid parameter",
    ErrorCode.RESOURCE_NOT_FOUND.value: "Resource not found",
    ErrorCode.PERMISSION_DENIED.value: "Permission denied",
    ErrorCode.VALIDATION_ERROR.value: "Validation failed",
    ErrorCode.RESOURCE_INVALID.value: "Invalid resource",
    ErrorCode.TYPE_ERROR.value: "Type error",
    ErrorCode.OPERATION_FAILED.value: "Operation failed",
    # Authentication related errors
    ErrorCode.AUTHENTICATION_ERROR.value: "Authentication error",
    ErrorCode.AUTHENTICATION_FAILED.value: "Authentication failed",
    ErrorCode.TOKEN_INVALID.value: "Invalid token",
    ErrorCode.TOKEN_EXPIRED.value: "Token expired",
    ErrorCode.PERMISSION_INSUFFICIENT.value: "Insufficient permissions",
    ErrorCode.USER_NOT_FOUND.value: "User not found",
    ErrorCode.USER_INVALID.value: "Invalid user information",
    # Agent related errors
    ErrorCode.AGENT_INITIALIZATION_ERROR.value: "Agent initialization error",
    ErrorCode.AGENT_EXECUTION_ERROR.value: "Agent execution error",
    ErrorCode.AGENT_STATE_ERROR.value: "Agent state error",
    ErrorCode.AGENT_TIMEOUT.value: "Agent timeout",
    ErrorCode.AGENT_CANCELLED.value: "Agent cancelled",
    ErrorCode.AGENT_MEMORY_ERROR.value: "Agent memory error",
    # Database related errors
    ErrorCode.DATABASE_ERROR.value: "Database error",
    ErrorCode.DATABASE_CONNECTION_ERROR.value: "Database connection error",
    ErrorCode.DATABASE_QUERY_ERROR.value: "Database query error",
    ErrorCode.DATABASE_TRANSACTION_ERROR.value: "Database transaction error",
    ErrorCode.DATABASE_CONSTRAINT_ERROR.value: "Database constraint error",
    ErrorCode.DATABASE_TIMEOUT.value: "Database timeout",
    # File related errors
    ErrorCode.FILE_NOT_FOUND.value: "File not found",
    ErrorCode.FILE_READ_ERROR.value: "File read error",
    ErrorCode.FILE_WRITE_ERROR.value: "File write error",
    ErrorCode.FILE_PERMISSION_ERROR.value: "File permission error",
    ErrorCode.FILE_FORMAT_ERROR.value: "File format error",
    ErrorCode.FILE_SIZE_EXCEEDED.value: "File size exceeded",
    ErrorCode.FILE_UPLOAD_FAILED.value: "File upload failed",
    ErrorCode.FILE_DOWNLOAD_FAILED.value: "File download failed",
    ErrorCode.FILE_PARSE_ERROR.value: "File parse error",
    # Network related errors
    ErrorCode.NETWORK_ERROR.value: "Network error",
    ErrorCode.HTTP_REQUEST_ERROR.value: "HTTP request error",
    ErrorCode.HTTP_TIMEOUT.value: "HTTP timeout",
    ErrorCode.URL_INVALID.value: "Invalid URL",
    ErrorCode.URL_SHORTENING_FAILED.value: "URL shortening failed",
    # External service errors
    ErrorCode.EXTERNAL_SERVICE_ERROR.value: "External service error",
    ErrorCode.EXTERNAL_SERVICE_TIMEOUT.value: "External service timeout",
    ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE.value: "External service unavailable",
    ErrorCode.API_RATE_LIMIT_EXCEEDED.value: "API rate limit exceeded",
    ErrorCode.API_KEY_INVALID.value: "Invalid API key",
    # Configuration related errors
    ErrorCode.CONFIGURATION_ERROR.value: "Configuration error",
    ErrorCode.CONFIGURATION_INVALID.value: "Invalid configuration",
    ErrorCode.CONFIGURATION_MISSING.value: "Configuration missing",
    ErrorCode.ENVIRONMENT_VARIABLE_MISSING.value: "Environment variable missing",
    # Generation related errors
    ErrorCode.GENERATION_ERROR.value: "Generation error",
    ErrorCode.GENERATION_TIMEOUT.value: "Generation timeout",
    ErrorCode.GENERATION_CANCELLED.value: "Generation cancelled",
    ErrorCode.GENERATION_IN_PROGRESS.value: "Generation in progress",
    ErrorCode.GENERATION_QUEUE_FULL.value: "Generation queue full",
    # Conversation related errors
    ErrorCode.CONVERSATION_NOT_FOUND.value: "Conversation not found",
    ErrorCode.CONVERSATION_INVALID.value: "Invalid conversation",
    ErrorCode.CONVERSATION_LIMIT_EXCEEDED.value: "Conversation limit exceeded",
    ErrorCode.MESSAGE_TOO_LONG.value: "Message too long",
    # Content related errors
    ErrorCode.CONTENT_EMPTY.value: "Content empty",
    ErrorCode.CONTENT_TOO_LONG.value: "Content too long",
    ErrorCode.CONTENT_INVALID_FORMAT.value: "Invalid content format",
    ErrorCode.CONTENT_PROCESSING_ERROR.value: "Content processing error",
    # Resource related errors
    ErrorCode.RESOURCE_PROCESSING_FAILED.value: "Resource processing failed",
    ErrorCode.RESOURCE_EXTRACTION_FAILED.value: "Resource extraction failed",
    ErrorCode.RESOURCE_IMPORT_FAILED.value: "Resource import failed",
    ErrorCode.RESOURCE_URI_MISSING.value: "Resource URI missing",
    # System errors
    ErrorCode.SYSTEM_ERROR.value: "System error",
    ErrorCode.INITIALIZATION_FAILED.value: "Initialization failed",
    ErrorCode.SERVICE_STARTUP_FAILED.value: "Service startup failed",
    ErrorCode.SERVICE_SHUTDOWN_FAILED.value: "Service shutdown failed",
    # Context and session errors
    ErrorCode.CONTEXT_NOT_SET.value: "Context not set",
    ErrorCode.SESSION_NOT_INITIALIZED.value: "Session not initialized",
    ErrorCode.MIDDLEWARE_ERROR.value: "Middleware error",
    # Workflow stage related error codes
    ErrorCode.CONVERSATION_TYPE_INVALID.value: "Invalid conversation type",
    ErrorCode.REQUIREMENT_EXTRACTION_NOT_COMPLETED.value: "Requirement extraction not completed",
    ErrorCode.OUTLINE_GENERATION_NOT_COMPLETED.value: "Outline generation not completed",
    ErrorCode.OUTLINE_ID_NOT_FOUND.value: "Outline ID not found",
    ErrorCode.FULLTEXT_ID_NOT_FOUND.value: "Fulltext ID not found",
    ErrorCode.DOCUMENT_SLICE_NOT_FOUND.value: "Document slice not found",
    # Task related error codes
    ErrorCode.TASK_NOT_FOUND.value: "Task not found",
    ErrorCode.NO_GENERATION_IN_PROGRESS.value: "No generation in progress",
    # Editor related error codes
    ErrorCode.UNSUPPORTED_EDITOR_TYPE.value: "Unsupported editor type",
    # Agent specific error codes
    ErrorCode.LLM_OUTPUT_PARSING_ERROR.value: "LLM output parsing failed",
    ErrorCode.LLM_CALL_FAILED.value: "LLM call failed",
    ErrorCode.LLM_RETRY_EXHAUSTED.value: "LLM retry attempts exhausted",
    # Quota related error codes
    ErrorCode.QUOTA_INSUFFICIENT.value: "Quota insufficient",
}


# ErrorMessage translation dictionary
ERROR_MESSAGES_ZH: Dict[str, str] = {
    # General errors
    ErrorMessage.UNKNOWN_ERROR.value: "An unknown error occurred",
    ErrorMessage.HTTP_ERROR.value: "HTTP error",
    ErrorMessage.INVALID_PARAMETER.value: "Invalid parameter provided",
    ErrorMessage.RESOURCE_NOT_FOUND.value: "Resource not found",
    ErrorMessage.PERMISSION_DENIED.value: "Permission denied",
    ErrorMessage.VALIDATION_ERROR.value: "Data validation failed",
    ErrorMessage.RESOURCE_INVALID.value: "Invalid resource",
    ErrorMessage.TYPE_ERROR.value: "Type error occurred",
    ErrorMessage.OPERATION_FAILED.value: "Operation failed",
    # Authentication related errors
    ErrorMessage.AUTHENTICATION_ERROR.value: "Authentication error",
    ErrorMessage.AUTHENTICATION_FAILED.value: "Authentication failed",
    ErrorMessage.TOKEN_INVALID.value: "Invalid token",
    ErrorMessage.TOKEN_EXPIRED.value: "Token has expired",
    ErrorMessage.PERMISSION_INSUFFICIENT.value: "Insufficient permissions",
    ErrorMessage.USER_NOT_FOUND.value: "User not found",
    ErrorMessage.USER_INVALID.value: "Invalid user information",
    # Agent related errors
    ErrorMessage.AGENT_INITIALIZATION_ERROR.value: "Agent initialization failed",
    ErrorMessage.AGENT_EXECUTION_ERROR.value: "Agent execution failed",
    ErrorMessage.AGENT_STATE_ERROR.value: "Agent state error",
    ErrorMessage.AGENT_TIMEOUT.value: "Agent execution timeout",
    ErrorMessage.AGENT_CANCELLED.value: "Agent execution cancelled",
    ErrorMessage.AGENT_MEMORY_ERROR.value: "Agent memory insufficient",
    # Database related errors
    ErrorMessage.DATABASE_ERROR.value: "Database error",
    ErrorMessage.DATABASE_CONNECTION_ERROR.value: "Database connection failed",
    ErrorMessage.DATABASE_QUERY_ERROR.value: "Database query failed",
    ErrorMessage.DATABASE_TRANSACTION_ERROR.value: "Database transaction failed",
    ErrorMessage.DATABASE_CONSTRAINT_ERROR.value: "Database constraint violation",
    ErrorMessage.DATABASE_TIMEOUT.value: "Database operation timeout",
    # File related errors
    ErrorMessage.FILE_NOT_FOUND.value: "File not found",
    ErrorMessage.FILE_READ_ERROR.value: "File read error",
    ErrorMessage.FILE_WRITE_ERROR.value: "File write error",
    ErrorMessage.FILE_PERMISSION_ERROR.value: "File permission denied",
    ErrorMessage.FILE_FORMAT_ERROR.value: "Invalid file format",
    ErrorMessage.FILE_SIZE_EXCEEDED.value: "File size limit exceeded",
    ErrorMessage.FILE_UPLOAD_FAILED.value: "File upload failed",
    ErrorMessage.FILE_DOWNLOAD_FAILED.value: "File download failed",
    ErrorMessage.FILE_PARSE_ERROR.value: "File parsing failed",
    # Network related errors
    ErrorMessage.NETWORK_ERROR.value: "Network connection error",
    ErrorMessage.HTTP_REQUEST_ERROR.value: "HTTP request failed",
    ErrorMessage.HTTP_TIMEOUT.value: "HTTP request timeout",
    ErrorMessage.URL_INVALID.value: "Invalid URL format",
    ErrorMessage.URL_SHORTENING_FAILED.value: "URL shortening failed",
    # External service errors
    ErrorMessage.EXTERNAL_SERVICE_ERROR.value: "External service call failed",
    ErrorMessage.EXTERNAL_SERVICE_TIMEOUT.value: "External service timeout",
    ErrorMessage.EXTERNAL_SERVICE_UNAVAILABLE.value: "External service unavailable",
    ErrorMessage.API_RATE_LIMIT_EXCEEDED.value: "API rate limit exceeded",
    ErrorMessage.API_KEY_INVALID.value: "Invalid API key",
    # Configuration related errors
    ErrorMessage.CONFIGURATION_ERROR.value: "Configuration error",
    ErrorMessage.CONFIGURATION_INVALID.value: "Invalid configuration format",
    ErrorMessage.CONFIGURATION_MISSING.value: "Configuration file missing",
    ErrorMessage.ENVIRONMENT_VARIABLE_MISSING.value: "Environment variable not set",
    # Generation related errors
    ErrorMessage.GENERATION_ERROR.value: "Generation process error",
    ErrorMessage.GENERATION_TIMEOUT.value: "Generation timeout",
    ErrorMessage.GENERATION_CANCELLED.value: "Generation cancelled",
    ErrorMessage.GENERATION_IN_PROGRESS.value: "Generation in progress",
    ErrorMessage.GENERATION_QUEUE_FULL.value: "Generation queue is full",
    ErrorMessage.NO_GENERATION_IN_PROGRESS.value: "No generation in progress",
    # Conversation related errors
    ErrorMessage.CONVERSATION_NOT_FOUND.value: "Conversation not found",
    ErrorMessage.CONVERSATION_INVALID.value: "Invalid conversation state",
    ErrorMessage.CONVERSATION_TYPE_INVALID.value: "Invalid conversation type",
    ErrorMessage.CONVERSATION_LIMIT_EXCEEDED.value: "Conversation limit exceeded",
    ErrorMessage.MESSAGE_TOO_LONG.value: "Message content too long",
    ErrorMessage.CONVERSATION_ACCESS_DENIED.value: "No permission to access this conversation",
    ErrorMessage.CONVERSATION_GET_FAILED.value: "Failed to get conversation",
    ErrorMessage.CONVERSATION_DELETE_FAILED.value: "Failed to delete conversation",
    ErrorMessage.CONVERSATION_LIST_GET_FAILED.value: "Failed to get conversation list",
    # Content related errors
    ErrorMessage.CONTENT_EMPTY.value: "Content cannot be empty",
    ErrorMessage.CONTENT_TOO_LONG.value: "Content length limit exceeded",
    ErrorMessage.CONTENT_INVALID_FORMAT.value: "Invalid content format",
    ErrorMessage.CONTENT_PROCESSING_ERROR.value: "Content processing failed",
    # Workflow stage related errors
    ErrorMessage.REQUIREMENT_EXTRACTION_NOT_COMPLETED.value: "Please complete the requirement extraction stage first",
    ErrorMessage.OUTLINE_GENERATION_NOT_COMPLETED.value: "Please complete the outline generation stage first",
    ErrorMessage.OUTLINE_ID_NOT_FOUND.value: "Unable to get outline_id",
    ErrorMessage.FULLTEXT_ID_NOT_FOUND.value: "Unable to get fulltext_id",
    ErrorMessage.DOCUMENT_SLICE_NOT_FOUND.value: "Document slice not found",
    # Editor and interface related errors
    ErrorMessage.UNSUPPORTED_EDITOR_TYPE.value: "Unsupported editor type",
    ErrorMessage.BEAN_NOT_FOUND.value: "Bean component not found",
    ErrorMessage.BEAN_OPERATION_FAILED.value: "Bean operation failed",
    # Filename and size related errors
    ErrorMessage.FILENAME_EMPTY.value: "Filename cannot be empty",
    # Document version related errors
    ErrorMessage.DOCUMENT_VERSION_NOT_FOUND.value: "Document version not found",
    ErrorMessage.DOCUMENT_VERSION_CREATE_FAILED.value: "Failed to create document version",
    ErrorMessage.DOCUMENT_VERSION_UPDATE_FAILED.value: "Failed to update document version",
    ErrorMessage.DOCUMENT_VERSION_DELETE_FAILED.value: "Failed to delete document version",
    ErrorMessage.DOCUMENT_VERSION_GET_FAILED.value: "Failed to get document version",
    ErrorMessage.DOCUMENT_NOT_FOUND.value: "Document not found",
    # Service related errors
    ErrorMessage.SERVICE_UNAVAILABLE.value: "Service unavailable",
    ErrorMessage.ANALYSIS_EXECUTION_FAILED.value: "Analysis execution failed",
    # Task related errors
    ErrorMessage.TASK_NOT_FOUND.value: "Task not found",
    ErrorMessage.TASK_CREATE_FAILED.value: "Failed to create task",
    ErrorMessage.TASK_GET_FAILED.value: "Failed to get task details",
    ErrorMessage.TASK_LIST_GET_FAILED.value: "Failed to get task list",
    ErrorMessage.TASK_CANCEL_FAILED.value: "Failed to cancel task",
    ErrorMessage.TASK_DELETE_FAILED.value: "Failed to delete task record",
    ErrorMessage.TASK_STATS_GET_FAILED.value: "Failed to get task statistics",
    ErrorMessage.TASK_REGISTERED_GET_FAILED.value: "Failed to get registered tasks",
    ErrorMessage.TASK_CANNOT_CANCEL.value: "Can only cancel pending or running tasks",
    ErrorMessage.TASK_CANNOT_DELETE_RUNNING.value: "Cannot delete running tasks, please cancel first",
    # Search related errors
    ErrorMessage.SEARCH_QUERY_EMPTY.value: "Search query cannot be empty",
    ErrorMessage.AI_SEARCH_FAILED.value: "AI search failed",
    ErrorMessage.QUICK_SEARCH_FAILED.value: "Quick search failed",
    ErrorMessage.SEARCH_SUGGESTIONS_FAILED.value: "Failed to get search suggestions",
    ErrorMessage.SEARCH_TAGS_FAILED.value: "Failed to get popular tags",
    # Resource related errors
    ErrorMessage.RESOURCE_PROCESSING_FAILED.value: "Resource processing failed",
    ErrorMessage.RESOURCE_EXTRACTION_FAILED.value: "Resource extraction failed",
    ErrorMessage.RESOURCE_IMPORT_FAILED.value: "Resource import failed",
    ErrorMessage.RESOURCE_URI_MISSING.value: "Resource URI missing",
    # System errors
    ErrorMessage.SYSTEM_ERROR.value: "System internal error",
    ErrorMessage.INITIALIZATION_FAILED.value: "System initialization failed",
    ErrorMessage.SERVICE_STARTUP_FAILED.value: "Service startup failed",
    ErrorMessage.SERVICE_SHUTDOWN_FAILED.value: "Service shutdown failed",
    # Context and session errors
    ErrorMessage.CONTEXT_NOT_SET.value: "Request context not set",
    ErrorMessage.SESSION_NOT_INITIALIZED.value: "Database session not initialized",
    ErrorMessage.MIDDLEWARE_ERROR.value: "Middleware processing error",
    # Resource related error messages (additional)
    ErrorMessage.RESOURCE_UPLOAD_FAILED.value: "Resource upload failed",
    ErrorMessage.RESOURCE_BIND_FAILED.value: "Resource binding failed",
    ErrorMessage.RESOURCE_LIST_GET_FAILED.value: "Failed to get resource list",
    ErrorMessage.RESOURCE_STATUS_GET_FAILED.value: "Failed to get resource status",
    ErrorMessage.RESOURCE_CITATION_GET_FAILED.value: "Failed to get resource citation",
    ErrorMessage.RESOURCE_GET_FAILED.value: "Failed to get resource",
    ErrorMessage.RESOURCE_NO_FILE.value: "Resource file does not exist",
    ErrorMessage.RESOURCE_DOWNLOAD_FAILED.value: "Resource download failed",
    ErrorMessage.RESOURCE_DELETE_FAILED.value: "Failed to delete resource",
    # Inspiration related error messages
    ErrorMessage.INSPIRATION_CREATE_FAILED.value: "Failed to create inspiration",
    ErrorMessage.INSPIRATION_NOT_FOUND.value: "Inspiration not found",
    ErrorMessage.INSPIRATION_TYPE_INVALID.value: "Invalid inspiration type",
    ErrorMessage.INSPIRATION_UPDATE_FAILED.value: "Failed to update inspiration",
    ErrorMessage.INSPIRATION_LIST_GET_FAILED.value: "Failed to get inspiration list",
    ErrorMessage.INSPIRATION_GET_FAILED.value: "Failed to get inspiration",
    ErrorMessage.RESOURCE_TYPE_GET_FAILED.value: "Failed to get resource type",
    ErrorMessage.RESOURCE_SCOPE_GET_FAILED.value: "Failed to get resource scope",
    ErrorMessage.RESOURCE_PROCESSING_STATUS_GET_FAILED.value: "Failed to get resource processing status",
    ErrorMessage.RESOURCE_SIGNED_URL_FAILED.value: "Failed to get resource signed URL",
    # LLM related errors
    ErrorMessage.LLM_OUTPUT_PARSING_ERROR.value: "LLM output parsing failed",
    ErrorMessage.LLM_CALL_FAILED.value: "LLM call failed",
    ErrorMessage.LLM_RETRY_EXHAUSTED.value: "LLM retry attempts exhausted",
    # Quota related errors
    ErrorMessage.QUOTA_INSUFFICIENT.value: "Insufficient balance to perform this operation",
}

ERROR_MESSAGES_EN: Dict[str, str] = {
    # General errors
    ErrorMessage.UNKNOWN_ERROR.value: "An unknown error occurred",
    ErrorMessage.HTTP_ERROR.value: "HTTP error",
    ErrorMessage.INVALID_PARAMETER.value: "Invalid parameter provided",
    ErrorMessage.RESOURCE_NOT_FOUND.value: "Resource not found",
    ErrorMessage.PERMISSION_DENIED.value: "Permission denied",
    ErrorMessage.VALIDATION_ERROR.value: "Data validation failed",
    ErrorMessage.RESOURCE_INVALID.value: "Invalid resource",
    ErrorMessage.TYPE_ERROR.value: "Type error occurred",
    ErrorMessage.OPERATION_FAILED.value: "Operation failed",
    # Authentication related errors
    ErrorMessage.AUTHENTICATION_ERROR.value: "Authentication error",
    ErrorMessage.AUTHENTICATION_FAILED.value: "Authentication failed",
    ErrorMessage.TOKEN_INVALID.value: "Invalid token",
    ErrorMessage.TOKEN_EXPIRED.value: "Token has expired",
    ErrorMessage.PERMISSION_INSUFFICIENT.value: "Insufficient permissions",
    ErrorMessage.USER_NOT_FOUND.value: "User not found",
    ErrorMessage.USER_INVALID.value: "Invalid user information",
    # Agent related errors
    ErrorMessage.AGENT_INITIALIZATION_ERROR.value: "Agent initialization failed",
    ErrorMessage.AGENT_EXECUTION_ERROR.value: "Agent execution failed",
    ErrorMessage.AGENT_STATE_ERROR.value: "Agent state error",
    ErrorMessage.AGENT_TIMEOUT.value: "Agent execution timeout",
    ErrorMessage.AGENT_CANCELLED.value: "Agent execution cancelled",
    ErrorMessage.AGENT_MEMORY_ERROR.value: "Agent memory insufficient",
    # Database related errors
    ErrorMessage.DATABASE_ERROR.value: "Database error",
    ErrorMessage.DATABASE_CONNECTION_ERROR.value: "Database connection failed",
    ErrorMessage.DATABASE_QUERY_ERROR.value: "Database query failed",
    ErrorMessage.DATABASE_TRANSACTION_ERROR.value: "Database transaction failed",
    ErrorMessage.DATABASE_CONSTRAINT_ERROR.value: "Database constraint violation",
    ErrorMessage.DATABASE_TIMEOUT.value: "Database operation timeout",
    # File related errors
    ErrorMessage.FILE_NOT_FOUND.value: "File not found",
    ErrorMessage.FILE_READ_ERROR.value: "File read error",
    ErrorMessage.FILE_WRITE_ERROR.value: "File write error",
    ErrorMessage.FILE_PERMISSION_ERROR.value: "File permission denied",
    ErrorMessage.FILE_FORMAT_ERROR.value: "Invalid file format",
    ErrorMessage.FILE_SIZE_EXCEEDED.value: "File size limit exceeded",
    ErrorMessage.FILE_UPLOAD_FAILED.value: "File upload failed",
    ErrorMessage.FILE_DOWNLOAD_FAILED.value: "File download failed",
    ErrorMessage.FILE_PARSE_ERROR.value: "File parsing failed",
    # Network related errors
    ErrorMessage.NETWORK_ERROR.value: "Network connection error",
    ErrorMessage.HTTP_REQUEST_ERROR.value: "HTTP request failed",
    ErrorMessage.HTTP_TIMEOUT.value: "HTTP request timeout",
    ErrorMessage.URL_INVALID.value: "Invalid URL format",
    ErrorMessage.URL_SHORTENING_FAILED.value: "URL shortening failed",
    # External service errors
    ErrorMessage.EXTERNAL_SERVICE_ERROR.value: "External service call failed",
    ErrorMessage.EXTERNAL_SERVICE_TIMEOUT.value: "External service timeout",
    ErrorMessage.EXTERNAL_SERVICE_UNAVAILABLE.value: "External service unavailable",
    ErrorMessage.API_RATE_LIMIT_EXCEEDED.value: "API rate limit exceeded",
    ErrorMessage.API_KEY_INVALID.value: "Invalid API key",
    # Configuration related errors
    ErrorMessage.CONFIGURATION_ERROR.value: "Configuration error",
    ErrorMessage.CONFIGURATION_INVALID.value: "Invalid configuration format",
    ErrorMessage.CONFIGURATION_MISSING.value: "Configuration file missing",
    ErrorMessage.ENVIRONMENT_VARIABLE_MISSING.value: "Environment variable not set",
    # Generation related errors
    ErrorMessage.GENERATION_ERROR.value: "Generation process error",
    ErrorMessage.GENERATION_TIMEOUT.value: "Generation timeout",
    ErrorMessage.GENERATION_CANCELLED.value: "Generation cancelled",
    ErrorMessage.GENERATION_IN_PROGRESS.value: "Generation in progress",
    ErrorMessage.GENERATION_QUEUE_FULL.value: "Generation queue is full",
    ErrorMessage.NO_GENERATION_IN_PROGRESS.value: "No generation in progress",
    # Conversation related errors
    ErrorMessage.CONVERSATION_NOT_FOUND.value: "Conversation not found",
    ErrorMessage.CONVERSATION_INVALID.value: "Invalid conversation state",
    ErrorMessage.CONVERSATION_TYPE_INVALID.value: "Invalid conversation type",
    ErrorMessage.CONVERSATION_LIMIT_EXCEEDED.value: "Conversation limit exceeded",
    ErrorMessage.MESSAGE_TOO_LONG.value: "Message content too long",
    ErrorMessage.CONVERSATION_ACCESS_DENIED.value: "No permission to access this conversation",
    ErrorMessage.CONVERSATION_GET_FAILED.value: "Failed to get conversation",
    ErrorMessage.CONVERSATION_DELETE_FAILED.value: "Failed to delete conversation",
    ErrorMessage.CONVERSATION_LIST_GET_FAILED.value: "Failed to get conversation list",
    # Content related errors
    ErrorMessage.CONTENT_EMPTY.value: "Content cannot be empty",
    ErrorMessage.CONTENT_TOO_LONG.value: "Content length limit exceeded",
    ErrorMessage.CONTENT_INVALID_FORMAT.value: "Invalid content format",
    ErrorMessage.CONTENT_PROCESSING_ERROR.value: "Content processing failed",
    # Workflow stage related errors
    ErrorMessage.REQUIREMENT_EXTRACTION_NOT_COMPLETED.value: "Please complete the requirement extraction stage first",
    ErrorMessage.OUTLINE_GENERATION_NOT_COMPLETED.value: "Please complete the outline generation stage first",
    ErrorMessage.OUTLINE_ID_NOT_FOUND.value: "Unable to get outline_id",
    ErrorMessage.FULLTEXT_ID_NOT_FOUND.value: "Unable to get fulltext_id",
    ErrorMessage.DOCUMENT_SLICE_NOT_FOUND.value: "Document slice not found",
    # Editor and interface related errors
    ErrorMessage.UNSUPPORTED_EDITOR_TYPE.value: "Unsupported editor type",
    ErrorMessage.BEAN_NOT_FOUND.value: "Bean component not found",
    ErrorMessage.BEAN_OPERATION_FAILED.value: "Bean operation failed",
    # Filename and size related errors
    ErrorMessage.FILENAME_EMPTY.value: "Filename cannot be empty",
    # Document version related errors
    ErrorMessage.DOCUMENT_VERSION_NOT_FOUND.value: "Document version not found",
    ErrorMessage.DOCUMENT_VERSION_CREATE_FAILED.value: "Failed to create document version",
    ErrorMessage.DOCUMENT_VERSION_UPDATE_FAILED.value: "Failed to update document version",
    ErrorMessage.DOCUMENT_VERSION_DELETE_FAILED.value: "Failed to delete document version",
    ErrorMessage.DOCUMENT_VERSION_GET_FAILED.value: "Failed to get document version",
    ErrorMessage.DOCUMENT_NOT_FOUND.value: "Document not found",
    # Service related errors
    ErrorMessage.SERVICE_UNAVAILABLE.value: "Service unavailable",
    ErrorMessage.ANALYSIS_EXECUTION_FAILED.value: "Analysis execution failed",
    # Task related errors
    ErrorMessage.TASK_NOT_FOUND.value: "Task not found",
    ErrorMessage.TASK_CREATE_FAILED.value: "Failed to create task",
    ErrorMessage.TASK_GET_FAILED.value: "Failed to get task details",
    ErrorMessage.TASK_LIST_GET_FAILED.value: "Failed to get task list",
    ErrorMessage.TASK_CANCEL_FAILED.value: "Failed to cancel task",
    ErrorMessage.TASK_DELETE_FAILED.value: "Failed to delete task record",
    ErrorMessage.TASK_STATS_GET_FAILED.value: "Failed to get task statistics",
    ErrorMessage.TASK_REGISTERED_GET_FAILED.value: "Failed to get registered tasks",
    ErrorMessage.TASK_CANNOT_CANCEL.value: "Can only cancel pending or running tasks",
    ErrorMessage.TASK_CANNOT_DELETE_RUNNING.value: "Cannot delete running tasks, please cancel first",
    # Search related errors
    ErrorMessage.SEARCH_QUERY_EMPTY.value: "Search query cannot be empty",
    ErrorMessage.AI_SEARCH_FAILED.value: "AI search failed",
    ErrorMessage.QUICK_SEARCH_FAILED.value: "Quick search failed",
    ErrorMessage.SEARCH_SUGGESTIONS_FAILED.value: "Failed to get search suggestions",
    ErrorMessage.SEARCH_TAGS_FAILED.value: "Failed to get popular tags",
    # Resource related errors
    ErrorMessage.RESOURCE_PROCESSING_FAILED.value: "Resource processing failed",
    ErrorMessage.RESOURCE_EXTRACTION_FAILED.value: "Resource extraction failed",
    ErrorMessage.RESOURCE_IMPORT_FAILED.value: "Resource import failed",
    ErrorMessage.RESOURCE_URI_MISSING.value: "Resource URI missing",
    # System errors
    ErrorMessage.SYSTEM_ERROR.value: "System internal error",
    ErrorMessage.INITIALIZATION_FAILED.value: "System initialization failed",
    ErrorMessage.SERVICE_STARTUP_FAILED.value: "Service startup failed",
    ErrorMessage.SERVICE_SHUTDOWN_FAILED.value: "Service shutdown failed",
    # Context and session errors
    ErrorMessage.CONTEXT_NOT_SET.value: "Request context not set",
    ErrorMessage.SESSION_NOT_INITIALIZED.value: "Database session not initialized",
    ErrorMessage.MIDDLEWARE_ERROR.value: "Middleware processing error",
    # Resource related error messages (additional)
    ErrorMessage.RESOURCE_UPLOAD_FAILED.value: "Resource upload failed",
    ErrorMessage.RESOURCE_BIND_FAILED.value: "Resource binding failed",
    ErrorMessage.RESOURCE_LIST_GET_FAILED.value: "Failed to get resource list",
    ErrorMessage.RESOURCE_STATUS_GET_FAILED.value: "Failed to get resource status",
    ErrorMessage.RESOURCE_CITATION_GET_FAILED.value: "Failed to get resource citation",
    ErrorMessage.RESOURCE_GET_FAILED.value: "Failed to get resource",
    ErrorMessage.RESOURCE_NO_FILE.value: "Resource file does not exist",
    ErrorMessage.RESOURCE_DOWNLOAD_FAILED.value: "Resource download failed",
    ErrorMessage.RESOURCE_DELETE_FAILED.value: "Failed to delete resource",
    # Inspiration related error messages
    ErrorMessage.INSPIRATION_CREATE_FAILED.value: "Failed to create inspiration",
    ErrorMessage.INSPIRATION_NOT_FOUND.value: "Inspiration not found",
    ErrorMessage.INSPIRATION_TYPE_INVALID.value: "Invalid inspiration type",
    ErrorMessage.INSPIRATION_UPDATE_FAILED.value: "Failed to update inspiration",
    ErrorMessage.INSPIRATION_LIST_GET_FAILED.value: "Failed to get inspiration list",
    ErrorMessage.INSPIRATION_GET_FAILED.value: "Failed to get inspiration",
    ErrorMessage.RESOURCE_TYPE_GET_FAILED.value: "Failed to get resource type",
    ErrorMessage.RESOURCE_SCOPE_GET_FAILED.value: "Failed to get resource scope",
    ErrorMessage.RESOURCE_PROCESSING_STATUS_GET_FAILED.value: "Failed to get resource processing status",
    ErrorMessage.RESOURCE_SIGNED_URL_FAILED.value: "Failed to get resource signed URL",
    # LLM related errors
    ErrorMessage.LLM_OUTPUT_PARSING_ERROR.value: "LLM output parsing failed",
    ErrorMessage.LLM_CALL_FAILED.value: "LLM call failed",
    ErrorMessage.LLM_RETRY_EXHAUSTED.value: "LLM retry attempts exhausted",
    # Quota related errors
    ErrorMessage.QUOTA_INSUFFICIENT.value: "Insufficient balance to perform this operation",
}


def get_error_message_by_key(message_key: str, language: str = "zh") -> str:
    """
    Get error message by message key and language

    Args:
        message_key: Error message key
        language: Language code, supports "zh" (Chinese) and "en" (English)

    Returns:
        Error message in the specified language
    """
    if language == "zh":
        return ERROR_MESSAGES_ZH.get(
            message_key, ERROR_MESSAGES_ZH[ErrorMessage.UNKNOWN_ERROR.value]
        )
    elif language == "en":
        return ERROR_MESSAGES_EN.get(
            message_key, ERROR_MESSAGES_EN[ErrorMessage.UNKNOWN_ERROR.value]
        )
    else:
        # Default to Chinese
        return ERROR_MESSAGES_ZH.get(
            message_key, ERROR_MESSAGES_ZH[ErrorMessage.UNKNOWN_ERROR.value]
        )


def get_all_error_messages(language: str = "zh") -> Dict[str, str]:
    """
    Get all error messages in the specified language

    Args:
        language: Language code, supports "zh" (Chinese) and "en" (English)

    Returns:
        Dictionary mapping error codes to error messages
    """
    if language == "en":
        return ERROR_MESSAGES_EN.copy()
    else:
        return ERROR_MESSAGES_ZH.copy()


def get_error_code_translation(error_code: str, language: str = "zh") -> str:
    """
    Get error code translation by error code and language

    Args:
        error_code: Error code
        language: Language code, supports "zh" (Chinese) and "en" (English)

    Returns:
        Translation of the error code in the specified language
    """
    if language == "zh":
        return ERROR_CODE_TRANSLATIONS_ZH.get(error_code, error_code)
    elif language == "en":
        return ERROR_CODE_TRANSLATIONS_EN.get(error_code, error_code)
    else:
        # Default to Chinese
        return ERROR_CODE_TRANSLATIONS_ZH.get(error_code, error_code)


def get_all_error_code_translations(language: str = "zh") -> Dict[str, str]:
    """
    Get all error code translations in the specified language

    Args:
        language: Language code, supports "zh" (Chinese) and "en" (English)

    Returns:
        Dictionary mapping error codes to translations
    """
    if language == "en":
        return ERROR_CODE_TRANSLATIONS_EN.copy()
    else:
        return ERROR_CODE_TRANSLATIONS_ZH.copy()


def _validate_translations_completeness():
    """
    Validate translation completeness, raise exception if missing translations are found

    Automatically executed during module import, ensuring all error codes and error messages have corresponding Chinese and English translations.
    Implements the "fail-fast" principle to avoid discovering missing translations at runtime.

    Raises:
        RuntimeError: When missing translations are found
    """
    missing_translations = []

    # Check ErrorCode translation completeness
    for code in ErrorCode:
        code_value = code.value

        # Check Chinese translation
        if code_value not in ERROR_CODE_TRANSLATIONS_ZH:
            missing_translations.append(
                f"ErrorCode {code_value} missing Chinese translation"
            )

        # Check English translation
        if code_value not in ERROR_CODE_TRANSLATIONS_EN:
            missing_translations.append(
                f"ErrorCode {code_value} missing English translation"
            )

    # Check ErrorMessage translation completeness
    for message in ErrorMessage:
        message_value = message.value

        # Check Chinese translation
        if message_value not in ERROR_MESSAGES_ZH:
            missing_translations.append(
                f"ErrorMessage {message_value} missing Chinese translation"
            )

        # Check English translation
        if message_value not in ERROR_MESSAGES_EN:
            missing_translations.append(
                f"ErrorMessage {message_value} missing English translation"
            )

    # If missing translations are found, raise exception
    if missing_translations:
        error_message = (
            f"Found {len(missing_translations)} missing translations, please complete them before running:\n"
            + "\n".join(
                f"  - {msg}" for msg in missing_translations[:10]
            )  # Show only first 10
        )
        if len(missing_translations) > 10:
            error_message += f"\n  ... and {len(missing_translations) - 10} more missing translations"

        raise RuntimeError(error_message)


# Automatically execute translation completeness check when module is imported
_validate_translations_completeness()
