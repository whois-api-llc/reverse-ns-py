from json import loads, JSONDecodeError
import re

from .net.http import ApiRequester
from .models.response import Response
from .exceptions.error import ParameterError, EmptyApiKeyError, \
    UnparsableApiResponseError


class Client:
    __default_url = "https://reverse-ns.whoisxmlapi.com/api/v1"
    _api_requester: ApiRequester or None
    _api_key: str
    _last_result: Response or None
    _name_server: str or None

    _re_api_key = re.compile(r'^at_[a-z0-9]{29}$', re.IGNORECASE)
    _re_domain_name = re.compile(
        r'^(?:[0-9a-z_](?:[0-9a-z-_]{0,62}(?<=[0-9a-z-_])[0-9a-z_])?\.)+'
        + r'[0-9a-z][0-9a-z-]{0,62}[a-z0-9]$', re.IGNORECASE)

    _PARSABLE_FORMAT = 'json'

    JSON_FORMAT = 'json'
    XML_FORMAT = 'xml'

    def __init__(self, api_key: str, **kwargs):
        """
        :param api_key: str: Your API key.
        :key base_url: str: (optional) API endpoint URL.
        :key timeout: float: (optional) API call timeout in seconds
        """

        self._api_key = ''

        self.api_key = api_key

        self._last_result = None
        self._name_server = ''

        if 'base_url' not in kwargs:
            kwargs['base_url'] = Client.__default_url

        self.api_requester = ApiRequester(**kwargs)

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = Client._validate_api_key(value)

    @property
    def api_requester(self) -> ApiRequester or None:
        return self._api_requester

    @api_requester.setter
    def api_requester(self, value: ApiRequester):
        self._api_requester = value

    @property
    def base_url(self) -> str:
        return self._api_requester.base_url

    @base_url.setter
    def base_url(self, value: str or None):
        if value is None:
            self._api_requester.base_url = Client.__default_url
        else:
            self._api_requester.base_url = value

    @property
    def last_result(self) -> Response or None:
        return self._last_result

    @last_result.setter
    def last_result(self, value: Response or None):
        if value is None:
            self._last_result = value
        elif isinstance(value, Response):
            self._last_result = value
        else:
            raise ValueError(
                "Values should be an instance of reversens.Response or None")

    @property
    def name_server(self) -> str:
        return self._name_server

    @name_server.setter
    def name_server(self, ns: str):
        try:
            self._name_server = Client._validate_domain_name(ns)
        except ParameterError as err:
            raise ValueError(err.message)

    @property
    def timeout(self) -> float:
        return self._api_requester.timeout

    @timeout.setter
    def timeout(self, value: float):
        self._api_requester.timeout = value

    def __iter__(self):
        if not self._name_server:
            raise ValueError('You need to specify a NS first. '
                             'Use the `name_server` instance`s property')

        self._last_result = None
        return self

    def __next__(self):
        if not self._name_server:
            raise ValueError('You need to specify a NS first. '
                             'Use the `name_server` instance`s property')
        if self._last_result:
            if not self._last_result.has_next():
                self._name_server = ''
                raise StopIteration
            return self.get(ns=self._name_server,
                            search_from=self._last_result.result[-1].name)
        else:
            return self.get(self._name_server)

    def get(self, ns: str,
            search_from: str = None) -> Response:
        """
        Get parsed API response as a `Response` instance.

        :param ns: Domain name of the name server, string
        :param search_from: The last record of the current page to get
            records after it, string
        :return: `Response` instance
        :raises ConnectionError:
        :raises ReverseNsApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter's value
        """

        output_format = Client._PARSABLE_FORMAT

        response = self.get_raw(ns, search_from, output_format)
        try:
            parsed = loads(str(response))
            if 'result' in parsed:
                self.last_result = Response(parsed)
                self.name_server = ns
                return self.last_result
            raise UnparsableApiResponseError(
                "Could not find the correct root element.", None)
        except JSONDecodeError as error:
            raise UnparsableApiResponseError("Could not parse API response", error)

    def get_raw(self, ns: str, search_from: str = None,
                output_format: str or None = None) -> str:
        """
        Get raw API response.

        :param ns: Domain name of the name server, string
        :param search_from: The last record of the current page to get
            records after it, string
        :param output_format: Use Client.JSON_FORMAT and Client.XML_FORMAT
            constants
        :return: str
        :raises ConnectionError:
        :raises ReverseNsApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter's value
        """

        if self.api_key == '':
            raise EmptyApiKeyError('')

        _ns = Client._validate_domain_name(ns)
        _from = Client._validate_search_from(search_from) \
            if search_from is not None else None
        _output_format = Client._validate_output_format(output_format) \
            if output_format is not None else None

        return self._api_requester.get(self._build_payload(
            self.api_key,
            _ns,
            _from,
            _output_format
        ))

    @staticmethod
    def _validate_api_key(api_key) -> str:
        if Client._re_api_key.search(str(api_key)):
            return str(api_key)
        else:
            raise ParameterError("Invalid API key format.")

    @staticmethod
    def _validate_domain_name(value) -> str:
        if Client._re_domain_name.search(str(value)):
            return str(value)

        raise ParameterError("Invalid ns name")

    @staticmethod
    def _validate_output_format(value: str):
        if str(value).lower() in {Client.JSON_FORMAT, Client.XML_FORMAT}:
            return str(value).lower()

        raise ParameterError(
            f"Response format must be {Client.JSON_FORMAT} "
            f"or {Client.XML_FORMAT}")

    @staticmethod
    def _validate_search_from(value) -> str:
        if value and str(value):
            return str(value)

        raise ParameterError("search_from should be a string")

    @staticmethod
    def _build_payload(
            api_key,
            ns,
            search_from,
            output_format
    ) -> dict:
        tmp = {
            'apiKey': api_key,
            'ns': ns,
            'from': search_from,
            'outputFormat': output_format
        }

        return {k: v for (k, v) in tmp.items() if v is not None}
