import winsound
import sys
import threading

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    play_func = winsound.PlaySound
else:
    # On most other platforms the best timer is time.time()
    play_func = None

def play(wav_file):

    sound_thread = SoundThread(wav_file)
    sound_thread.start()

class SoundThread(threading.Thread):
    def __init__(self, wav_file):
        threading.Thread.__init__(self)
        self.wav_file = wav_file
    def run(self):
        print("starting sound")
        play_func(self.wav_file, winsound.SND_FILENAME)

