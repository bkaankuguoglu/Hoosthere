""" MS Cognitive Speach - Speaker Identification """

from __future__ import absolute_import
from requests import codes as status
from .apiclient import ApiClient

_IDENTIFICATION_PROFILES_URI = '/spid/v1.0/identificationProfiles'
_IDENTIFICATION_URI = '/spid/v1.0/identify'


def json_response(response):
    """ converts the requests response into json if not already """
    if isinstance(response, dict):
        return response
    else:
        return response.json()


class SpeechIdentification(object):
    """ handles all interaction with the Identification service """
    def __init__(self, subscription_key, config=None):
        config = config or {}
        self._api_client = ApiClient(subscription_key, config)
        self._profiles_uri = config.get('identification_profiles_uri',
                                        _IDENTIFICATION_PROFILES_URI)
        self._ident_uri = config.get('identification_uri',
                                     _IDENTIFICATION_URI)

    def create_profile(self, locale='en-us'):
        """ creates a user profile using the regional locale """
        message = {'locale': locale}
        response = self._api_client.post(self._profiles_uri, data=message)

        return json_response(response).get('identificationProfileId', None)

    def delete_profile(self, profile_id):
        """ deletes a user profile """
        request_url = '%s/%s' % (self._profiles_uri, profile_id)
        response = self._api_client.delete(request_url)

        return response.status_code in [status.ok, status.no_content]

    def enroll_profile(self, profile_id, wav_data, short_audio=False):
        """ uses wav format data to enroll/train a users profile """
        request_url = '%s/%s/enroll' % (self._profiles_uri, profile_id)
        params = {'shortAudio': short_audio}
        response = self._api_client.post(request_url,
                                         params=params, data=wav_data)

        return json_response(response)

    def get_profile(self, profile_id):
        """ returns details of a user profile """
        request_url = '%s/%s' % (self._profiles_uri, profile_id)
        response = self._api_client.get(request_url)

        return json_response(response)

    def identify_profile(self, profile_ids, wav_data, short_audio=False):
        """ identifies the audio wav data to one of the profile ids """
        params = {'identificationProfileIds': ','.join(profile_ids),
                  'shortAudio': short_audio}
        response = self._api_client.post(self._ident_uri,
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
