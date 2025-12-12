import json
import requests
from http import HTTPStatus
from typing import List, Dict, Optional

from intacctsdk.enums import RESTMethodEnum
from intacctsdk.constants import BASE_URL, PAGE_SIZE
from intacctsdk.exceptions import (
    BadRequestError,
    InvalidTokenError,
    InternalServerError,
    IntacctRESTSDKError
)


class ApiBase:
    """
    The base class for all API classes
    :param sdk_instance: Intacct REST SDK instance
    :param object_path: Object path
    :return: None
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None, object_path: str = None):
        """
        Initialize the API base
        :param sdk_instance: Intacct REST SDK instance
        :param object_path: Object path
        :return: None
        """
        self.__entity_id = None
        self.__access_token = None
        self._object_path = object_path
        self._sdk_instance = sdk_instance
        self.__object_name = object_path.replace('/objects/', '') if object_path else None

        if sdk_instance:
            sdk_instance._register_api_instance(self)

    def update_access_token(self, access_token: str) -> None:
        """
        Sets the access token for APIs
        :param access_token: access token (JWT)
        :return: None
        """
        self.__access_token = access_token

    def update_entity_id(self, entity_id: str) -> None:
        """
        Sets the entity id for APIs
        :param entity_id: entity id
        :return: None
        """
        self.__entity_id = entity_id

    def _make_request(
        self,
        url: str,
        method: str,
        data: dict = {},
        params: dict = {},
        use_api_headers: bool = True
    ) -> List[Dict] or Dict:
        """
        Makes a request to the API
        :param url: URL to make the request to
        :param method: HTTP method
        :param data: data to send
        :param params: parameters to send
        :param use_api_headers: whether to use API headers
        :return: response from the request
        """
        api_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(self.__access_token),
            'X-IA-API-Param-Entity': self.__entity_id if self._object_path != '/objects/company-config/entity' else None
        }

        response = requests.request(
            url=url,
            method=method,
            params=params,
            headers=api_headers if use_api_headers else {},
            data=json.dumps(data) if use_api_headers and method != RESTMethodEnum.GET else data
        )

        if response.status_code >= HTTPStatus.OK and response.status_code < HTTPStatus.MULTIPLE_CHOICES:
            if response.status_code == HTTPStatus.NO_CONTENT:
                return None
            return response.json()

        elif response.status_code >= HTTPStatus.BAD_REQUEST and response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
            if response.status_code == HTTPStatus.BAD_REQUEST and response.text and ('Invalid token' in response.text or 'The token is not valid' in response.text):
                raise InvalidTokenError('Invalid token, status code: {0}'.format(response.status_code), response.text)
            else:
                raise BadRequestError('Something wrong with the request body, status code: {0}'.format(response.status_code), response.text)

        elif response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            raise InternalServerError('Internal server error, status code: {0}'.format(response.status_code), response.text)

        else:
            raise IntacctRESTSDKError('Error: {0}, status code: {1}'.format(response.text, response.status_code), response.text)

    def _get_request(self, params: Optional[dict] = None) -> List[Dict] or Dict:
        """
        Create a HTTP GET request
        :param params: parameters to send
        :return: response from the request
        """
        url = f'{BASE_URL}{self._object_path}'

        return self._make_request(method=RESTMethodEnum.GET, url=url, params=params)

    def get_all_generator(
        self,
        fields: List[str],
        filters: List[Dict] = [],
        filter_expression: Optional[str] = None,
        filter_parameters: Dict = {},
        order_by: List[Dict] = [],
        dimension_name: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all objects from the API using user query service
        :param fields: list of fields to fetch
        :param filters: list of filters to apply
        :param filter_expression: filter expression to apply
        :param filter_parameters: filter parameters to apply
        :param order_by: list of fields to order by
        :param dimension_name: name of the dimension to fetch
        :return: generator of objects
        """
        start = 1

        if not filter_expression and filters:
            filter_expression = 'and'

        while True:
            response = self._make_request(
                method=RESTMethodEnum.POST,
                url=f'{BASE_URL}/services/core/query',
                data={
                    'object': f'platform-apps/nsp::{dimension_name}' if dimension_name else self.__object_name,
                    'fields': fields,
                    'filters': filters,
                    'filterExpression': filter_expression,
                    'filterParameters': filter_parameters,
                    'orderBy': order_by,
                    'start': start,
                    'size': PAGE_SIZE
                }
            )

            yield response['ia::result']

            if response.get('ia::meta', {}).get('next') is None:
                break

            start += PAGE_SIZE

    def count(
        self,
        filters: List[Dict] = [],
        filter_expression: Optional[str] = None,
        filter_parameters: Dict = {},
        dimension_name: Optional[str] = None
    ) -> int:
        """
        Get the count of objects matching the filters
        :param filters: list of filters to apply
        :param filter_expression: filter expression to apply
        :param filter_parameters: filter parameters to apply
        :param dimension_name: name of the dimension to fetch
        :return: count of objects
        """
        if not filter_expression and filters:
            filter_expression = 'and'

        response = self._make_request(
            method=RESTMethodEnum.POST,
            url=f'{BASE_URL}/services/core/query',
            data={
                'object': f'platform-apps/nsp::{dimension_name}' if dimension_name else self.__object_name,
                'fields': ['id'],
                'filters': filters,
                'filterExpression': filter_expression,
                'filterParameters': filter_parameters,
                'start': 1,
                'size': 1
            }
        )

        return response['ia::meta']['totalCount']

    def get_by_key(self, key: str) -> Dict:
        """
        Get an object by key
        :param key: key of the object
        :return: object
        """
        return self._make_request(
            method=RESTMethodEnum.GET,
            url=f'{BASE_URL}{self._object_path}/{key}'
        )

    def get_model(self) -> Dict:
        """
        Get the model for the object
        :return: model
        """
        return self._make_request(
            method=RESTMethodEnum.GET,
            url=f'{BASE_URL}/services/core/model',
            params={
                'name': self.__object_name
            }
        )

    def post(self, data: Dict) -> Dict:
        """
        Create an object
        :param data: data to create the object
        :return: created object
        """
        return self._make_request(
            method=RESTMethodEnum.POST,
            url=f'{BASE_URL}{self._object_path}',
            data=data
        )

    def delete(self, key: str) -> Dict:
        """
        Delete an object
        :param key: key of the object
        :return: deleted object
        """
        return self._make_request(
            method=RESTMethodEnum.DELETE,
            url=f'{BASE_URL}{self._object_path}/{key}'
        )


class TransactionApiBase(ApiBase):
    """
    The base class for all transaction-related API classes
    :param sdk_instance: Intacct REST SDK instance
    :param object_path: Object path
    :return: None
    """
    def __init__(self, sdk_instance: 'IntacctRESTSDK' = None, object_path: str = None):
        """
        Initialize the transaction API base
        :param sdk_instance: Intacct REST SDK instance
        :param object_path: Object path
        :return: None
        """
        super().__init__(sdk_instance, object_path)

    def update_attachment(self, object_id: str, attachment_id: str) -> Dict:
        """
        Update the attachment for an object
        :param object_id: id of the object
        :param attachment_id: id of the attachment
        :return: attachment
        """
        return self._make_request(
            method=RESTMethodEnum.PATCH,
            url=f'{BASE_URL}{self._object_path}/{object_id}',
            data={
                'attachment': {
                    'id': attachment_id
                }
            }
        )
