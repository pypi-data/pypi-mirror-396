class ReportSDKException(Exception):
    """Base exception for the SDK."""
    pass

class AuthenticationError(ReportSDKException):
    """Raised when authentication fails."""
    pass

class RequestError(ReportSDKException):
    """Raised for errors during the request."""
    pass
