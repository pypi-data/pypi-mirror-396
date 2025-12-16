from intacctsdk.apis.api_base import ApiBase


class Items(ApiBase):
    """
    Intacct Items API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Items API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/inventory-control/item')
