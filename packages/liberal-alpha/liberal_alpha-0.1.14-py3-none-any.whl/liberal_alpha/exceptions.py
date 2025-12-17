class LiberalAlphaError(Exception):
    """Base exception for Liberal Alpha SDK errors"""
    pass


class ConnectionError(LiberalAlphaError):
    """Exception raised when the gRPC client fails to connect to the runner"""

    def __init__(self, message="Failed to connect to the gRPC server", details=None):
        self.message = message
        self.details = details
        super().__init__(self.__str__())

    def __str__(self):
        error_str = f"ConnectionError: {self.message}"
        if self.details:
            error_str += f"\nDetails: {self.details}"
        return error_str


class RequestError(LiberalAlphaError):
    """Exception raised when sending a request to the gRPC server fails"""

    def __init__(self, message="Request to gRPC server failed", code=None, details=None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.__str__())

    def __str__(self):
        error_str = f"RequestError: {self.message}"
        if self.code:
            error_str += f" (code: {self.code})"
        if self.details:
            error_str += f"\nDetails: {self.details}"
        return error_str


class ConfigurationError(LiberalAlphaError):
    """Exception raised when the client is misconfigured"""

    def __init__(self, message="Client is misconfigured"):
        self.message = message
        super().__init__(self.__str__())

    def __str__(self):
        return f"ConfigurationError: {self.message}"


class SubscriptionError(LiberalAlphaError):
    """Exception raised when there is an error with the subscription process"""

    def __init__(self, message="Error in subscription process", details=None):
        self.message = message
        self.details = details
        super().__init__(self.__str__())

    def __str__(self):
        error_str = f"SubscriptionError: {self.message}"
        if self.details:
            error_str += f"\nDetails: {self.details}"
        return error_str


class DecryptionError(LiberalAlphaError):
    """Exception raised when decryption of subscription data fails"""

    def __init__(self, message="Failed to decrypt subscription data", details=None):
        self.message = message
        self.details = details
        super().__init__(self.__str__())

    def __str__(self):
        error_str = f"DecryptionError: {self.message}"
        if self.details:
            error_str += f"\nDetails: {self.details}"
        return error_str