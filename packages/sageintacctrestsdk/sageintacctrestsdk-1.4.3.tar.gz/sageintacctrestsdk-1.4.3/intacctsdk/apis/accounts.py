from intacctsdk.apis.api_base import ApiBase


class Accounts(ApiBase):
    """
    Intacct Accounts API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Accounts API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/general-ledger/account')
