""" generic API handler for MS Cognitive Services """

import json
import time
import requests
from requests import codes as status

_BASE_URI = 'https://api.projectoxford.ai'

_CONTENT_TYPE_HEADER = 'Content-Type'
_OPERATION_LOCATION_HEADER = 'Operation-Location'
_SUBSCRIPTION_KEY_HEADER = 'Ocp-Apim-Subscription-Key'

_JSON_CONTENT_HEADER_VALUE = 'application/json'
_STREAM_CONTENT_HEADER_VALUE = 'application/octet-stream'


def get_polling_url(response):
    """ checks the response to see if it includes a pollable url """
    if _OPERATION_LOCATION_HEADER in response.headers:
        return response.headers[_OPERATION_LOCATION_HEADER]

    return None


def is_pollable(response):
    """ determines if the response needs to be polled to get final result """
    if response.status_code != status.accepted:
        return False

    if not get_polling_url(response):
        return False

    return True


class ApiClient(object):
    """ slightly convention based class to help wrap API requests """
    def __init__(self, subscription_key, config=None):
        config = config or {}
        self._subscription_key = subscription_key
        self._config = {
            'polling_delay_secs': float(config.get('polling_delay_secs', 4)),
            'base_uri': config.get('base_uri', _BASE_URI)
        }

    def _exec_request(self, request, url_path, params=None, data=None):
        content_type = _JSON_CONTENT_HEADER_VALUE

        if data and isinstance(data, dict):
            data = json.dumps(data)
        elif data and len(data) > 0:
            content_type = _STREAM_CONTENT_HEADER_VALUE

        headers = {_CONTENT_TYPE_HEADER: content_type,
                   _SUBSCRIPTION_KEY_HEADER: self._subscription_key}

        if not url_path.startswith('http'):
            url_path = self._config['base_uri'] + url_path

        response = request(url_path, params=params, headers=headers, data=data)

        if is_pollable(response):
            json_response = self._poll_for_final_response(response)
            return json_response

        return response

    def _poll_for_final_response(self, response):
        url = get_polling_url(response)

        while True:
            response = self.get(url)

            if response.status_code != status.ok:
                raise Exception('Operation Error: %s -> %s' %
                                (response.headers, response.text))

            response_json = response.json()

            if response_json['status'] == 'succeeded':
                return response_json['processingResult']
            elif response_json['status'] == 'failed':
                raise Exception('Operation Error: ' + response_json['message'])
            else:
                time.sleep(self._config['polling_delay_secs'])

    def get(self, url_path, params=None):
        """ performs a get request against using the supplied args """
        response = self._exec_request(requests.get, url_path, params=params)

        return response

    def post(self, url_path, params=None, data=None):
        """ performs a post request against using the supplied args """
        response = self._exec_request(requests.post, url_path,
                                      params=params, data=data)

        return response

    def put(self, url_path, params=None, data=None):
        """ performs a put request against using the supplied args """
        response = self._exec_request(requests.put, url_path,
                                      params=params, data=data)

        return response

    def delete(self, url_path, params=None):
        """ performs a delete request against using the supplied args """
        response = self._exec_request(requests.delete, url_path, params=params)

        return response
