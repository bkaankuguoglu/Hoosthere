import cognitive_sr.sound_recorder
import io

subscription_key = '497d4917f97345fd9b6eb8368bfcf784'
profile_id = '2d53504b-ff89-44c6-860c-d65493f999e8'
BING_KEY = "d51898fb7acd49faa9bed7669702d240"


def create_profile():
    """ creates a user profile """
    speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
    result = speech_identification.create_profile()
    print(result)


def delete_profile(profile_id):
    """ deletes a user profile """
    speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
    result = speech_identification.delete_profile(profile_id)
    print('Deleted:', result)


def enroll_profile(profile_id):
    """ enrolls a profile using a wav recording of them speaking """

    wav_path = cognitive_sr.sound_recorder.record_sound(profile_id)

    with io.open(wav_path, 'rb') as wav_file:
        wav_data = wav_file.read()

    speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
    result = speech_identification.enroll_profile(profile_id, wav_data)
    print(result)


def identify_profile(profile_ids):
    """ identifies a profile using a wav recording of them speaking """
    wav_path = cognitive_sr.sound_recorder.record_sound(profile_id)

    with io.open(wav_path, 'rb') as wav_file:
        wav_data = wav_file.read()

    speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
    result = speech_identification.identify_profile(
        profile_ids.split(','), wav_data, short_audio=True)
    return result


def list_profiles():
    """ lists all the currently registered profiles """
    speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
    profiles = speech_identification.get_all_profiles()

    for profile in profiles:
        print(profile)


def speech2text(BING_KEY):
   cognitive_sr.recognition.recognize(BING_KEY)

speech2text(BING_KEY)
#identify_profile('cde2eb34-02f7-4be9-9433-eb65a8317a1c,53da1d9d-3ebe-44ef-8d05-5e7d258cd7d3')

list_profiles()