import wave
import numpy as np
import time


def print_line(tittle=''):
    print('\n\\', end='')
    print(time.strftime("%H:%M:%S", time.localtime()), end=' ')
    print('---------------------------\\' + '  ' + tittle)


class WAVE_88_file:
    """
    读取88个wave文件，生成一个WAVE_88_file对象
    """

    def get_frame_rate(self):
        self.frame_rate = int(self.keys_frames_framerate[0][1])
        for i in range(88):
            if int(self.keys_frames_framerate[0][1]) != self.frame_rate:
                print('wave文件帧率不一致，无法使用')
                return

    def get_88_keys_len(self):
        return self.keys_frames_framerate[:, 0]

    def __init__(self, wave_pack='sample4', channel=0):
        self.frame_rate = 0
        self.keys_frames_framerate = np.zeros((88, 2))  # 单音总帧数与帧率
        self.keys_wave = list()
        self.diff_dic = {'sample4': 1, 'sample5': 0, 'sampke_new': 1}  # 针对wave文件名偏移

        for i in np.arange(88):
            wave_file_path = wave_pack + '/' + str(i + self.diff_dic[wave_pack]) + '.wav'
            wave_file = wave.open(wave_file_path, "rb")
            self.keys_frames_framerate[i][0] = wave_file.getnframes()
            self.keys_frames_framerate[i][1] = wave_file.getframerate()
            wave_read_frames_bytes = wave_file.readframes(
                int(self.keys_frames_framerate[i][0]))  # 读取并返回以 bytes 对象表示的最多 n 帧音频
            wave_file.close()
            wave_read_frames = np.array(np.frombuffer(wave_read_frames_bytes, dtype=np.short))
            """读取双声道文件"""
            wave_read_frames.shape = -1, 2
            wave_read_frames = wave_read_frames.T
            self.keys_wave.append(wave_read_frames[channel])

        self.get_frame_rate()
