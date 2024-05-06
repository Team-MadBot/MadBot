from enum import IntEnum


class BoticordException(Exception):
    pass


class InternalException(BoticordException):
    def __init__(self, response):
        super().__init__(response)


class HTTPException(BoticordException):
    def __init__(self, response):
        self.response = response

        super().__init__(
            f"{HTTPErrors(self.response['error'].name)} (Status code: {StatusCodes(self.response['status'].name)})"
        )


class StatusCodes(IntEnum):
    """Status codes of response"""

    SERVER_ERROR = 500
    """Server Error (>500)"""

    TOO_MANY_REQUESTS = 429
    """Too Many Requests"""

    NOT_FOUND = 404
    """Requested resource was not found"""

    FORBIDDEN = 403
    """You don't have access to this resource"""

    UNAUTHORIZED = 401
    """Authorization is required to access this resource"""

    BAD_REQUEST = 400
    """Bad Request"""


class HTTPErrors(IntEnum):
    """Errors which BotiCord may return"""

    UNKNOWN_ERROR = 0
    """Unknown error"""

    INTERNAL_SERVER_ERROR = 1
    """Server error (>500)"""

    RATE_LIMITED = 2
    """Too many requests"""

    NOT_FOUND = 3
    """Not found"""

    FORBIDDEN = 4
    """Access denied"""

    BAD_REQUEST = 5
    """Bad request"""

    UNAUTHORIZED = 6
    """Unauthorized. Authorization required"""

    RPC_ERROR = 7
    """Server error (RPC)"""

    WS_ERROR = 8
    """Server error (WS)"""

    THIRD_PARTY_FAIL = 9
    """Third-party service error"""

    UNKNOWN_USER = 10
    """Unknown user"""

    SHORT_DOMAIN_TAKEN = 11
    """Short link already taken"""

    UNKNOWN_SHORT_DOMAIN = 12
    """Unknown short link"""

    UNKNOWN_LIBRARY = 13
    """Unknown library"""

    TOKEN_INVALID = 14
    """Invalid token"""

    UNKNOWN_RESOURCE = 15
    """Unknown resource"""

    UNKNOWN_TAG = 16
    """Unknown tag"""

    PERMISSION_DENIED = 17
    """Insufficient permissions"""

    UNKNOWN_COMMENT = 18
    """Unknown comment"""

    UNKNOWN_BOT = 19
    """Unknown bot"""

    UNKNOWN_SERVER = 20
    """Unknown server"""

    UNKNOWN_BADGE = 21
    """Unknown badge"""

    USER_ALREADY_HAS_A_BADGE = 22
    """User already has a badge"""

    INVALID_INVITE_CODE = 23
    """Invalid invite code"""

    SERVER_ALREADY_EXISTS = 24
    """Server already exists"""

    BOT_NOT_PRESENT_ON_QUEUE_SERVER = 25
    """Bot not present on queue server"""

    UNKNOWN_UP = 26
    """Unknown up"""

    TOO_MANY_UPS = 27
    """Too many ups"""

    INVALID_STATUS = 28
    """Invalid resource status"""

    UNKNOWN_REPORT = 29
    """Unknown report"""

    UNSUPPORTED_MEDIA_TYPE = 30
    """Unsupported media type. Should be one of"""

    UNKNOWN_APPLICATION = 31
    """Unknown application"""

    AUTOMATED_REQUESTS_NOT_ALLOWED = 32
    """Please confirm that you are not a robot by refreshing the page"""
