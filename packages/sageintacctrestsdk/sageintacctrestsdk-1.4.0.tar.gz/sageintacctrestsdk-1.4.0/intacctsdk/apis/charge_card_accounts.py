from intacctsdk.apis.api_base import ApiBase


class ChargeCardAccounts(ApiBase):
    """
    Intacct Charge Card Accounts API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Charge Card Accounts API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/cash-management/credit-card-account')
