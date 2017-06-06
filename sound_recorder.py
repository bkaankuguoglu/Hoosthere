import pyaudio
import wave
import datetime

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 6


def record_sound():

    audio = pyaudio.PyAudio()
    numdevices = audio.get_device_count()
    print('asd' + str(numdevices))

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK, input_device_index=1, output=False)
    print('INFO: Voice recording started.')
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print('INFO: Voice recording finished.')

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    filename = 'sound_recog.wav'

    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    return filename