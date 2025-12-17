from intacctsdk.apis.api_base import ApiBase


class TaxDetails(ApiBase):
    """
    Intacct Tax Details API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Tax Details API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/tax/tax-detail')
