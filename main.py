import os
import time

import numpy as np

import wave
import scipy.io.wavfile as wavfile


def print_line(tittle=''):
    print('\n\\', end='')
    print(time.strftime("%H:%M:%S", time.localtime()), end=' ')
    print('---------------------------\\' + '  ' + tittle)


class MIDI_file:
    """
    MIDI_文件类，-读取并记录midi文件信息，-绑定wave文件\n
    self.file_name-------------------文件名\n
    self.lines----------------------文件行数\n
    self.notes_num------------------按键数\n
    self.midi_type------------------文件类型\n
    self.midi_tracks----------------轨道数\n
    self.all_tracks-----------------按键事件数\n
    self.midi_division--------------每四分之一音符的时钟脉冲数\n
    self.end_track------------------最后的track\n
    self.midi_time------------------文件持续事件\n
    self.tempo_list-----------------每四分之一音符的微秒数的列表  # 时间， tempo， tempo开始的微秒数\n
    """

    def print_inf(self):
        """
        打印midi文件信息
        """
        print('file_name:  ', self.file_name)
        print('file_lines:  ', self.lines)
        print('notes_num:  ', self.notes_num)
        print('midi_type:  ', self.midi_type)
        print('midi_tracks:  ', self.midi_tracks)
        print('midi_division:  ', self.midi_division)
        print('tempo_list:  \n', self.tempo_list)
        print('end_track:  ', self.end_track)
        print('midi_time:  ', self.midi_time, 'μs', self.midi_time / 1000000, 's')
        print('all_tracks_num:  ', len(self.all_tracks))

    def midi2csv(self, file_name="NULL"):

        """
        利用 Midicsv.exe 将midi文件转为csv文件
        判断输入文件是否为MIDI文件
        cmd调用Midicsv
        """

        if not file_name.endswith(".mid"):
            print("File is not a midi file!")
            return 0
        else:
            print('Convert midi file to csv file N.csv')
        cmd = r'midicsv -v ' + self.file_name + ' N.csv'
        print('cmd: ' + cmd)
        os.system(cmd)
        time.sleep(0.001)
        print('N.csv file build successfully!')

    # 利用 Midicsv.exe 将midi文件转为csv文件

    def csv_read(self):
        """
        np.loadtext() 读取N.csv 并且写入信息
        """

        csv_reader = np.loadtxt('N.csv', str, delimiter="\n", )
        self.lines = len(csv_reader)
        line_now = 0
        part = 1
        for csv_line in csv_reader:
            line_now += 1
            if line_now > part * self.lines / 100:
                part += 1
                print('|', end='')
            # 进度条

            csv_line_str = str(csv_line).split(', ')  # 分行读取，转为str， 分割

            """----------Header----------"""
            if csv_line_str[0] == '0':
                if csv_line_str[2] == 'Header':  # 文件基本信息
                    self.midi_type = int(csv_line_str[3])
                    self.midi_tracks = int(csv_line_str[4])
                    self.midi_division = float(csv_line_str[5])
                    continue

            """----------End_track----------"""
            if csv_line_str[2] == 'End_track':  # 文件终止时间
                end_track = int(csv_line_str[1])
                if end_track > self.end_track:
                    self.end_track = end_track
                continue

            """----------Tempo----------"""
            if csv_line_str[2] == 'Tempo':  # 读取tempo
                tempo_trick = (int(csv_line_str[1]), int(csv_line_str[3]), 0.0)  # 时间clock， tempo， tempo开始的微秒数
                self.tempo_list.append(tempo_trick)
                self.tempo_num += 1
                continue

            """----------Note_on_off----------"""
            if csv_line_str[2] == 'Note_on_c' or csv_line_str[2] == 'Note_off_c':  # 读取按键
                if csv_line_str[2] == 'Note_on_c':
                    self.all_tracks.append((
                        int(csv_line_str[1]),
                        0,
                        int(csv_line_str[4]) - 20,
                        int(csv_line_str[5])
                    ))  # (clock, 按, 键位, 力度)
                    self.notes_num += 1
                    continue
                if csv_line_str[2] == 'Note_off_c':
                    self.all_tracks.append((
                        int(csv_line_str[1]),
                        1,
                        int(csv_line_str[4]) - 20,
                        int(csv_line_str[5])
                    ))  # (clock, 抬, 键位, 力度)
                    continue
        print('')

    def after_effert(self):
        """
        后处理，tempo tracks 排序
        """

        """tempo"""
        self.tempo_list = np.array(self.tempo_list)
        self.tempo_list = self.tempo_list[np.argsort(self.tempo_list[:, 0])]  # 排序
        for i in range(len(self.tempo_list)):  # 每次tempo改变的微秒数
            if i == 0:
                continue
            self.tempo_list[i][2] = self.tempo_list[i - 1][2] + self.tempo_list[i - 1][1] * \
                                    (self.tempo_list[i][0] - self.tempo_list[i - 1][0]) / self.midi_division
        self.midi_time = self.tempo_list[-1][2] + self.tempo_list[-1][1] * \
                         (self.end_track - self.tempo_list[-1][0]) / self.midi_division  # 文件总时长 微妙

        """tracks"""
        self.all_tracks = np.array(self.all_tracks)
        self.all_tracks = self.all_tracks[np.argsort(self.all_tracks[:, 0])]

    def __init__(self, file_name=''):
        self.file_name = file_name  # 文件名
        self.lines = 0  # 文件行数
        self.notes_num = 0  # 按键数
        self.midi_type = 0  # 文件类型
        self.midi_tracks = 0  # 轨道数
        self.all_tracks = list()  # 按键事件数
        self.midi_division = 0  # 每四分之一音符的时钟脉冲数
        self.end_track = 0  # 最后的track
        self.midi_time = 0  # 文件持续事件
        self.tempo_list = list()  # 每四分之一音符的微秒数的列表
        self.tempo_num = 0  # tempo 的数量
        """
        division: 每四分之一音符的时钟脉冲数(the number of clock pulses per quarter note)
        tempo: 指定为每四分之一音符的微秒数，介于1和16777215之间。500000相当于每分钟120个四分之一音符（“节拍”）。要将每分钟的节拍转换为一个节拍值，可以用60000000除以每分钟的节拍得到商。
        """

        """
        midi文件的各项数据
        按键数， midi文件类型， 通道数， 每四分音符的分段数
        """
        print_line('midi转csv')
        self.midi2csv(file_name)
        print_line('解析读取csv文件')
        self.csv_read()
        '''后处理'''
        self.after_effert()
        print_line('读取完成')


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


class MIDI_Blender:
    """
    MIDI合成器， 输入一个 MIDI_file 和 WAVE_88_file 对象
    """

    def clock2ftime(self, clock):
        time_for_clock = 0
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
                self.tracks_88[key][int(frame_start + self.wave_file.keys_frames_framerate[key][0]) - 500:int(frame_start + self.wave_file.keys_frames_framerate[key][0])] *= \
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

    def __init__(self, midi_file=MIDI_file(), wave_file=WAVE_88_file()):
        self.midi_file = midi_file
        self.wave_file = wave_file
        self.frame_rate = self.wave_file.frame_rate  # 合成器帧率
        self.all_frams = self.frame_rate * (self.midi_file.midi_time / 1000000 + 7)  # 合成器帧数 (额外1秒缓冲)
        self.tracks_88 = np.zeros(shape=(88, int(self.all_frams)), dtype=np.double)  # 88条轨道
        self.tracks_88_combine = np.zeros((int(self.all_frams),), dtype=np.double)
        print(int(self.all_frams / self.frame_rate))


if __name__ == '__main__':
    midi_flower_dance = MIDI_file('test_midis/HUAN_SHI_ZHI_YE.mid')
    wave_sample4 = WAVE_88_file()
    print(midi_flower_dance.tempo_list)
    print(midi_flower_dance.midi_time)

    wave_out = MIDI_Blender(midi_flower_dance, wave_sample4)
    wave_out.write_tracks()
    wave_out.wave_write('HUAN_SHI_ZHI_YE.wav')
