class HeaptreeException(Exception):
    """Base exception raised for errors in the Heaptree API."""
    
    def __init__(self, message: str, raw_response: dict = None):
        super().__init__(message)
        self.raw_response = raw_response


# Node Creation Exceptions
class NodeCreationException(HeaptreeException):
    """Exception raised when node creation fails."""
    pass
class UsageLimitsExceededException(NodeCreationException):
    """Exception raised when usage limits are exceeded during node creation."""
    pass
class InvalidRequestParametersException(HeaptreeException):
    """Exception raised when request parameters are invalid."""
    pass


# Node Cleanup Exceptions
class NodeCleanupException(HeaptreeException):
    """Exception raised when node cleanup fails."""
    pass
class NodeNotFoundException(NodeCleanupException):
    """Exception raised when the specified node is not found."""
    pass
class AccessDeniedException(NodeCleanupException):
    """Exception raised when access to the node is denied."""
    pass
class InvalidNodeStateException(NodeCleanupException):
    """Exception raised when the node is in an invalid state for the operation."""
    pass


# File Transfer Exceptions
class FileTransferException(HeaptreeException):
    """Exception raised when file transfer operations fail."""
    pass
class InstanceNotReadyException(FileTransferException):
    """Exception raised when the instance is not ready for file operations."""
    pass
class InvalidDestinationPathException(FileTransferException):
    """Exception raised when the destination path is invalid."""
    pass
class TransferFailedException(FileTransferException):
    """Exception raised when the file transfer operation fails."""
    pass

# Download File Exceptions
class DownloadFileException(HeaptreeException):
    """Exception raised when the file download operation fails."""
    pass
class FileToDownloadNotFoundException(DownloadFileException):
    """Exception raised when the file to download is not found."""
    pass


# Upload URL Exceptions
class UploadUrlException(HeaptreeException):
    """Exception raised when getting upload URL fails."""
    pass


# Authentication Exceptions
class AuthenticationException(HeaptreeException):
    """Exception raised for authentication errors."""
    pass
class MissingCredentialsException(AuthenticationException):
    """Exception raised when authentication credentials are missing."""
    pass
class InvalidApiKeyException(AuthenticationException):
    """Exception raised when the API key is invalid."""
    pass
class ApiKeyDisabledException(AuthenticationException):
    """Exception raised when the API key has been disabled."""
    pass


# Internal Server Error
class InternalServerErrorException(HeaptreeException):
    """Exception raised for internal server errors."""
    pass


# Status Code to Exception Mapping
STATUS_CODE_TO_EXCEPTION = {
    # Node Creation
    "FORBIDDEN_BY_USAGE_LIMITS": UsageLimitsExceededException,
    "INVALID_REQUEST_PARAMETERS": InvalidRequestParametersException,
    
    # Node Cleanup
    "NODE_NOT_FOUND": NodeNotFoundException,
    "ACCESS_DENIED": AccessDeniedException,
    "INVALID_NODE_STATE": InvalidNodeStateException,
    
    # File Transfer
    "INSTANCE_NOT_READY": InstanceNotReadyException,
    "INVALID_DESTINATION_PATH": InvalidDestinationPathException,
    "TRANSFER_FAILED": TransferFailedException,
    
    # Download File
    "FILE_TO_DOWNLOAD_NOT_FOUND": FileToDownloadNotFoundException,
    
    # General
    "INTERNAL_SERVER_ERROR": InternalServerErrorException,
}

# Auth Error Code to Exception Mapping
AUTH_ERROR_CODE_TO_EXCEPTION = {
    "MISSING_CREDENTIALS": MissingCredentialsException,
    "INVALID_API_KEY": InvalidApiKeyException,
    "API_KEY_DISABLED": ApiKeyDisabledException,
}


def raise_for_status(raw_response: dict, context: str = "API request"):
    """
    Raise appropriate exception based on response status.
    
    Args:
        raw_response: The raw API response
        context: Context description for error messages
        
    Raises:
        Appropriate HeaptreeException subclass based on status code
    """
    status = raw_response.get("status")
    if status == "SUCCESS":
        return  # No error
    
    details = raw_response.get("details", "No details provided")
    
    # Look up the appropriate exception class
    exception_class = STATUS_CODE_TO_EXCEPTION.get(status, HeaptreeException)
    
    # Create error message with context
    error_message = f"{context} failed with status {status}: {details}"
    
    # Raise the specific exception
    raise exception_class(error_message, raw_response)


def raise_for_auth_error(response_json: dict, context: str = "Authentication"):
    """
    Raise appropriate authentication exception based on error code.
    
    Args:
        response_json: The raw API response
        context: Context description for error messages
        
    Raises:
        Appropriate AuthenticationException subclass based on error code
    """
    error_code = response_json.get("detail", {}).get("error") if isinstance(response_json.get("detail"), dict) else None
    message = response_json.get("detail", {}).get("message") if isinstance(response_json.get("detail"), dict) else str(response_json.get("detail", "Authentication failed"))
    
    # Look up the appropriate exception class
    exception_class = AUTH_ERROR_CODE_TO_EXCEPTION.get(error_code, HeaptreeException)
    
    # Create error message with context
    error_message = f"{context} error: {message}"
    
    # Raise the specific exception
    raise exception_class(error_message, response_json)