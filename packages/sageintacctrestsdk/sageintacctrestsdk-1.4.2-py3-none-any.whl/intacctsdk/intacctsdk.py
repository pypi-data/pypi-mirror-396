import os

from intacctsdk.constants import BASE_URL
from intacctsdk.enums import RESTMethodEnum
from intacctsdk.apis import (
    Bills,
    Items,
    Tasks,
    Classes,
    Vendors,
    ApiBase,
    Accounts,
    Contacts,
    Sessions,
    CostTypes,
    Projects,
    Customers,
    Employees,
    Locations,
    TaxDetails,
    Dimensions,
    Departments,
    APPayments,
    Attachments,
    Allocations,
    ExpenseTypes,
    ExpenseReports,
    JournalEntries,
    SavingsAccounts,
    LocationEntities,
    CheckingAccounts,
    AttachmentFolders,
    ChargeCardAccounts,
    ExpensePaymentTypes,
    ChargeCardTransactions
)


class IntacctRESTSDK:
    """
    Intacct REST SDK
    """
    def __init__(
        self,
        username: str = None,
        refresh_token: str = None,
        access_token: str = None,
        client_id: str = None,
        client_secret: str = None,
        entity_id: str = None,
        use_client_credentials_auth: bool = True
    ) -> None:
        """
        Initialize connection to Intacct
        :param username: Intacct username
        :param refresh_token: Intacct refresh_token
        :param access_token: Intacct access_token
        :param client_id: Intacct client_id
        :param client_secret: Intacct client_secret
        :param entity_id: Intacct entity_id
        :param use_client_credentials_auth: Use client credentials authentication
        :return: None
        """
        self.__entity_id = entity_id
        self.__username = username
        self.__use_client_credentials_auth = use_client_credentials_auth
        self.__refresh_token = refresh_token
        self.__access_token = access_token
        self.__client_id = client_id or os.getenv('INTACCT_CLIENT_ID')
        self.__client_secret = client_secret or os.getenv('INTACCT_CLIENT_SECRET')

        self._api_instances = []

        # Initialize all API modules
        self.bills = Bills(self)
        self.tasks = Tasks(self)
        self.items = Items(self)
        self.classes = Classes(self)
        self.vendors = Vendors(self)
        self.sessions = Sessions(self)
        self.accounts = Accounts(self)
        self.contacts = Contacts(self)
        self.projects = Projects(self)
        self.customers = Customers(self)
        self.employees = Employees(self)
        self.locations = Locations(self)
        self.cost_types = CostTypes(self)
        self.dimensions = Dimensions(self)
        self.tax_details = TaxDetails(self)
        self.ap_payments = APPayments(self)
        self.departments = Departments(self)
        self.allocations = Allocations(self)
        self.attachments = Attachments(self)
        self.expense_types = ExpenseTypes(self)
        self.expense_reports = ExpenseReports(self)
        self.journal_entries = JournalEntries(self)
        self.savings_accounts = SavingsAccounts(self)
        self.location_entities = LocationEntities(self)
        self.checking_accounts = CheckingAccounts(self)
        self.attachment_folders = AttachmentFolders(self)
        self.charge_card_accounts = ChargeCardAccounts(self)
        self.expense_payment_types = ExpensePaymentTypes(self)
        self.charge_card_transactions = ChargeCardTransactions(self)
        self.api_base = ApiBase(self, object_path='/oauth2/token')

        self.__update_entity_id()

        if not self.__access_token:
            if self.__use_client_credentials_auth:
                self.__generate_access_token_from_client_credentials()
            else:
                self.__generate_access_token_from_refresh_token()

        self.__update_access_token()

    def __generate_access_token_from_refresh_token(self):
        """
        Generate the access token using the refresh token.
        """
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.__client_id,
            'client_secret': self.__client_secret,
            'refresh_token': self.__refresh_token
        }

        response = self.api_base._make_request(
            url=f'{BASE_URL}/oauth2/token',
            method=RESTMethodEnum.POST,
            data=payload,
            use_api_headers=False
        )

        self.__access_token = response['access_token']
        self.__refresh_token = response['refresh_token']
        self.__access_token_expires_in = response['expires_in']

    def __generate_access_token_from_client_credentials(self):
        """
        Generate the access token using the client credentials.
        """
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.__client_id,
            'client_secret': self.__client_secret,
            'username': self.__username
        }

        response = self.api_base._make_request(
            url=f'{BASE_URL}/oauth2/token',
            method=RESTMethodEnum.POST,
            data=payload,
            use_api_headers=False
        )

        self.__access_token = response['access_token']
        self.__refresh_token = response['refresh_token']
        self.__access_token_expires_in = response['expires_in']

    def __update_access_token(self):
        """
        Update the access token and change it in all registered API objects.
        """
        for api_instance in self._api_instances:
            api_instance.update_access_token(self.__access_token)

    def __update_entity_id(self):
        """
        Update the entity id and change it in all registered API objects.
        """
        for api_instance in self._api_instances:
            api_instance.update_entity_id(self.__entity_id)

    def _register_api_instance(self, api_instance: ApiBase) -> None:
        """
        Register an API instance for bulk configuration updates.
        :param api_instance: API instance to register
        :return: None
        """
        self._api_instances.append(api_instance)

    @property
    def refresh_token(self) -> str:
        """
        Get the refresh token
        :return: refresh token
        """
        return self.__refresh_token

    @property
    def access_token(self) -> str:
        """
        Get the access token
        :return: access token
        """
        return self.__access_token

    @property
    def access_token_expires_in(self) -> int:
        """
        Get the access token expires in
        :return: access token expires in
        """
        return self.__access_token_expires_in
