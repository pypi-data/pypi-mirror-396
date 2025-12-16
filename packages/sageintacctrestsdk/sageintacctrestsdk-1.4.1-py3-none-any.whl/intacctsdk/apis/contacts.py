from intacctsdk.apis.api_base import ApiBase


class Contacts(ApiBase):
    """
    Intacct Contacts API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Contacts API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/company-config/contact')
