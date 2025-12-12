from intacctsdk.apis.api_base import ApiBase


class Vendors(ApiBase):
    """
    Intacct Vendors API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Vendors API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/accounts-payable/vendor')
