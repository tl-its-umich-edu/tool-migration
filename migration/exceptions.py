class BaseException(Exception):
    """
    Base class for exceptions for the project
    """


class InvalidToolIdsException(BaseException):
    """
    Exception raised when one or more tool ID that are referenced are not
    found in an account or course context
    """


class ConfigException(BaseException):
    """
    Exception raised when an environment variable value is invalid
    """