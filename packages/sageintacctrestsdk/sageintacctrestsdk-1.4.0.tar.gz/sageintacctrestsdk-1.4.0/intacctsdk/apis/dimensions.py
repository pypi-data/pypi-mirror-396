from typing import Dict, List

from intacctsdk.apis.api_base import ApiBase


class Dimensions(ApiBase):
    """
    Intacct Dimensions API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Dimensions API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/services/company-config/dimensions/list')

    def list(self) -> List[Dict]:
        """
        List the dimensions
        :return: list of dimensions
        """
        return self._get_request().get('ia::result')
