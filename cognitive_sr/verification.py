""" MS Cognitive Speach - Speaker Verification """

from __future__ import absolute_import
from requests import codes as status
from .apiclient import ApiClient

_VERIFICATION_PROFILES_URI = '/spid/v1.0/verificationProfiles'
_VERIFICATION_URI = '/spid/v1.0/verify'


def json_response(response):
    """ converts the requests response into json if not already """
    if isinstance(response, dict):
        return response
    else:
        return response.json()


class SpeechVerification(object):
    """ handles all interaction with the Identification service """
    def __init__(self, subscription_key, config=None):
        config = config or {}
        self._api_client = ApiClient(subscription_key, config)
        self._profiles_uri = config.get('verification_profiles_uri',
                                        _VERIFICATION_PROFILES_URI)
        self._verify_uri = config.get('verfification_uri',
                                      _VERIFICATION_URI)

    def create_profile(self, locale='en-us'):
        """ creates a user profile using the regional locale """
        message = {'locale': locale}
        response = self._api_client.post(self._profiles_uri, data=message)

        return json_response(response).get('verificationProfileId', None)

    def delete_profile(self, profile_id):
        """ deletes a user profile """
        request_url = '%s/%s' % (self._profiles_uri, profile_id)
        response = self._api_client.delete(request_url)

        return response.status_code in [status.ok, status.no_content]

    def enroll_profile(self, profile_id, wav_data):
        """ uses wav format data to enroll/train a users profile """
        request_url = '%s/%s/enroll' % (self._profiles_uri, profile_id)
        response = self._api_client.post(request_url, data=wav_data)

        return json_response(response)

    def get_profile(self, profile_id):
        """ returns details of a user profile """
        request_url = '%s/%s' % (self._profiles_uri, profile_id)
        response = self._api_client.get(request_url)

        return json_response(response)

    def verify_profile(self, profile_id, wav_data):
        """ verifies the audio wav data against the profile id """
        params = {'verificationProfileId': profile_id}
        response = self._api_client.post(self._verify_uri,
                                         params=params, data=wav_data)

        return json_response(response)

    def get_all_profiles(self):
        """ returns all the registered profiles """
        response = self._api_client.get(self._profiles_uri)

        return json_response(response)

    def reset_enrollment(self, profile_id):
        """ resets the trained enrollment data against a profile """
        request_url = '%s/%s/reset' % (self._profiles_uri, profile_id)
        response = self._api_client.post(request_url)

        return response.status_code in [status.ok, status.no_content]
