from intacctsdk.apis.api_base import ApiBase


class CostTypes(ApiBase):
    """
    Intacct Cost Types API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Cost Types API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/construction/cost-type')
