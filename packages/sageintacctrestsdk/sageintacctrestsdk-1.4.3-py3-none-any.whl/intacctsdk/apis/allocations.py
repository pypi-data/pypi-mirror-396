from intacctsdk.apis.api_base import ApiBase


class Allocations(ApiBase):
    """
    Intacct Allocations API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Allocations API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/general-ledger/txn-allocation-template')
