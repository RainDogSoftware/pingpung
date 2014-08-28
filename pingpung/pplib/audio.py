try:
    import winsound
except:
    pass

import sys
import threading


def play(wav_file):
    sound_thread = SoundThread(wav_file)
    sound_thread.start()


class SoundThread(threading.Thread):
    def __init__(self, wav_file):
        threading.Thread.__init__(self)
        self.wav_file = wav_file

    def run(self):
        if sys.platform == "win32":
            winsound.PlaySound(self.wav_file, winsound.SND_FILENAME)
        else:
            # TODO:  Add non-win audio support
            print("Audio not yet available on this platform")

