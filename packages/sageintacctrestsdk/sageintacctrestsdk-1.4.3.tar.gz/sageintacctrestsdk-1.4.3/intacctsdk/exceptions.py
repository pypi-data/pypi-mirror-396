class IntacctRESTSDKError(Exception):
    """
    The base exception class for Intacct REST SDK
    :param msg: Short description of the error
    :param response: Error response from the API call
    :return: None
    """
    def __init__(self, msg: str, response: dict = None) -> None:
        """
        Initialize the exception
        :param msg: Short description of the error
        :param response: Error response from the API call
        :return: None
        """
        super(IntacctRESTSDKError, self).__init__(msg)
        self.message = msg
        self.response = response

    def __str__(self) -> str:
        """
        Return the string representation of the exception
        :return: String representation of the exception
        """
        return repr(self.message)


class InvalidTokenError(IntacctRESTSDKError):
    """
    Wrong/expired/non-existing access token
    """


class BadRequestError(IntacctRESTSDKError):
    """
    Some of the parameters (HTTP params or request body) are wrong, 4xx error
    """


class InternalServerError(IntacctRESTSDKError):
    """
    Anything 5xx
    """
