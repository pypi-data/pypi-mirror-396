from intacctsdk.apis.api_base import ApiBase


class Sessions(ApiBase):
    """
    Intacct Session API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Session API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/services/core/session/id')

    def get_session_id(self) -> str:
        """
        Retrieve the current session ID
        :return: Session ID as a string
        """
        response = self._get_request()['ia::result']
        return response
