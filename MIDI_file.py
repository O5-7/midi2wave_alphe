import os
import time

import numpy as np


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
            self.tempo_list[i][2] = self.tempo_list[i - 1][2] + self.tempo_list[i - 1][1] * (
                        self.tempo_list[i][0] - self.tempo_list[i - 1][0]) / self.midi_division
        self.midi_time = self.tempo_list[-1][2] + self.tempo_list[-1][1] * (
                    self.end_track - self.tempo_list[-1][0]) / self.midi_division  # 文件总时长 微妙

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
