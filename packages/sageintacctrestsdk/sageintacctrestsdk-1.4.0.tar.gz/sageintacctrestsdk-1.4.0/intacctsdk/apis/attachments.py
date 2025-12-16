from intacctsdk.apis.api_base import ApiBase


class Attachments(ApiBase):
    """
    Intacct Attachments API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Attachments API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/company-config/attachment')
