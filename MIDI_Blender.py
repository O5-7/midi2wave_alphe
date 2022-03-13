import time
import WAVE_88_file
import MIDI_file
import numpy as np

import scipy.io.wavfile as wavfile


def print_line(tittle=''):
    print('\n\\', end='')
    print(time.strftime("%H:%M:%S", time.localtime()), end=' ')
    print('---------------------------\\' + '  ' + tittle)


class MIDI_Blender:
    """
    MIDI合成器， 输入一个 MIDI_file 和 WAVE_88_file 对象
    """

    def clock2ftime(self, clock):
        tempo_index = 0  # tempo 在 tempo_list 的 index
        for i in range(self.midi_file.tempo_num):
            if clock >= self.midi_file.tempo_list[i][0]:
                tempo_index = i
                continue
            else:
                break
        tempo_line = self.midi_file.tempo_list[tempo_index]
        time_for_clock = tempo_line[2] + (clock - tempo_line[0]) * tempo_line[1] / self.midi_file.midi_division
        return time_for_clock

    def write_tracks(self, delay=100):
        """
        将88个wave依照midi的格式写入88个tracks内
        对于超出常规钢琴范围的midi文件提示警告
        """
        print_line('write_tracks')

        delay_array = np.arange(int(delay * self.wave_file.frame_rate / 1000)) / (
                delay * self.wave_file.frame_rate / 1000)
        delay_array = np.exp(-3 * delay_array)
        delay_array = delay_array - np.min(delay_array)
        delay_array = delay_array / np.max(delay_array)

        if np.min(self.midi_file.all_tracks[:, 2]) < 1 or np.max(self.midi_file.all_tracks[:, 2]) > 88:
            print('存在key超出常规88键范围')
        '''进度条'''
        write_count = 0
        write_part = 0
        write_all_count = len(self.midi_file.all_tracks)
        print('事件数： ', write_all_count)  # 事件数
        for sign_key_event in self.midi_file.all_tracks:
            write_count += 1
            if write_count > write_part * write_all_count / 100:
                print('|', end='')
                write_part += 1
            if sign_key_event[2] < 1 or sign_key_event[2] > 88:
                continue

            '''获取按键开始的帧位置'''
            clock = sign_key_event[0]  # 对应的时钟脉冲clock
            time_4_clock = self.clock2ftime(clock)  # 对应的时间 微秒_time
            frame_start = int(time_4_clock * self.frame_rate / 1000000)  # 对应的帧
            key = sign_key_event[2] - 1

            if sign_key_event[1] == 0:
                '''选段， 填充'''
                self.tracks_88[key][frame_start:int(frame_start + self.wave_file.keys_frames_framerate[key][0])] \
                    = self.wave_file.keys_wave[key] * (sign_key_event[3] / 127)
                self.tracks_88[key][frame_start:frame_start + 100] *= (np.arange(100) / 100)
                self.tracks_88[key][int(frame_start + self.wave_file.keys_frames_framerate[key][0]) - 500:int(
                    frame_start + self.wave_file.keys_frames_framerate[key][0])] *= \
                    np.power((1 - np.arange(500) / 500), 2)
                continue

            if sign_key_event[1] == 1:
                self.tracks_88[key][frame_start:frame_start + int(delay * self.wave_file.frame_rate / 1000)] *= \
                    delay_array * (sign_key_event[3] / 127) + (127 - sign_key_event[3]) / 127
                self.tracks_88[key][frame_start + int(delay * self.wave_file.frame_rate / 1000):] *= (
                        sign_key_event[3] / 127)

    def wave_write(self, file_name):
        self.tracks_88_combine = np.sum(self.tracks_88, axis=0)
        self.tracks_88_combine = self.tracks_88_combine / np.max(np.abs(self.tracks_88_combine))
        wavfile.write(file_name, self.frame_rate, self.tracks_88_combine)
        print_line('导出完成')

    def __init__(self, midi_file: MIDI_file, wave_file: WAVE_88_file):
        self.midi_file = midi_file
        self.wave_file = wave_file
        self.frame_rate = self.wave_file.frame_rate  # 合成器帧率
        self.all_frams = self.frame_rate * (self.midi_file.midi_time / 1000000 + 7)  # 合成器帧数 (额外1秒缓冲)
        self.tracks_88 = np.zeros(shape=(88, int(self.all_frams)), dtype=np.double)  # 88条轨道
        self.tracks_88_combine = np.zeros((int(self.all_frams),), dtype=np.double)
        print(int(self.all_frams / self.frame_rate))
