from intacctsdk.apis.api_base import ApiBase


class ExpensePaymentTypes(ApiBase):
    """
    Intacct Expense Payment Types API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Expense Payment Types API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/expenses/employee-expense-payment-type')
