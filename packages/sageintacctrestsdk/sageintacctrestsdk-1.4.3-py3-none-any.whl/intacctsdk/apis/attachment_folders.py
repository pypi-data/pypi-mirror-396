from intacctsdk.apis.api_base import ApiBase


class AttachmentFolders(ApiBase):
    """
    Intacct Attachment Folders API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Attachment Folders API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/company-config/folder')
