from intacctsdk.apis.api_base import ApiBase


class LocationEntities(ApiBase):
    """
    Intacct Location Entities API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Location Entities API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/company-config/entity')
