from intacctsdk.apis.api_base import TransactionApiBase


class ExpenseReports(TransactionApiBase):
    """
    Intacct Expense Reports API
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None):
        """
        Initialize the Expense Reports API
        :param sdk_instance: Intacct REST SDK instance
        :return: None
        """
        super().__init__(sdk_instance, object_path='/objects/expenses/employee-expense')
