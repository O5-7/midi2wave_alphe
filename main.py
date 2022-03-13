from MIDI_file import *
from WAVE_88_file import *
from MIDI_Blender import MIDI_Blender
import time


def print_line(tittle=''):
    print('\n\\', end='')
    print(time.strftime("%H:%M:%S", time.localtime()), end=' ')
    print('---------------------------\\' + '  ' + tittle)


if __name__ == '__main__':
    midi_flower_dance = MIDI_file('test_midis/Flower_Dance.mid')
    wave_sample4 = WAVE_88_file()
    print(midi_flower_dance.tempo_list)
    print(midi_flower_dance.midi_time)

    wave_out = MIDI_Blender(midi_flower_dance, wave_sample4)
    wave_out.write_tracks()
    wave_out.wave_write('FFlower_Dance.wav')
