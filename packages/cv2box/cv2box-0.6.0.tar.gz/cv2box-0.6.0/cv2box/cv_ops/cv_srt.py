# -- coding: utf-8 --
# @Time : 2024/11/23
# @Author : ykk648
import math
import re


def convert_to_hms(seconds: float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = math.floor((seconds % 1) * 1000)
    output = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"
    return output


def parse_hms(time_str: str) -> float:
    # 将时间字符串解析为时、分、秒和毫秒部分
    try:
        hms, ms = time_str.split(',')
        hours, minutes, seconds = map(int, hms.split(':'))
        milliseconds = int(ms)
    except ValueError:
        raise ValueError("Invalid time format. Should be 'hh:mm:ss,mmm'.")

    # 计算总秒数
    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    return total_seconds


class CVSrt:
    def __init__(self):
        self.text_list = []
        self.full_lines = []
        self.timestamps = []

    def replace_dots(self, text, language):
        if language in ['zh', 'ja', 'yue']:
            dot = '。'
        else:
            dot = '.'
        # 找到最后一个句号的位置
        last_dot_index = text.rfind(dot)
        # 将文本中除了最后一个句号之外的所有句号替换为逗号
        modified_text = text[:last_dot_index].replace(dot, ',') + text[last_dot_index:]
        return modified_text

    def write2srt(self, output_path="file.srt", from_whisper=False):
        if not from_whisper and self.full_lines[4] != '\n':
            for i, line in enumerate(self.full_lines):
                if (i - 3) % 4 == 0:
                    self.full_lines[i] = line.replace('\n', '\n\n')
        with open(output_path, mode="w", encoding="UTF-8") as f:
            f.writelines(self.full_lines)

    def read_srt(self, srt_path="file.srt"):
        with open(srt_path, mode="r", encoding="UTF-8") as f:
            self.full_lines = f.readlines()
            self.get_text_list_from_full_lines()
            self.get_timestamps_from_full_lines()

    def update_srt_from_text_list(self, text_list=None):
        if text_list is None:
            text_list = self.text_list
        assert len(text_list) * 4 == len(self.full_lines)
        for i, line in enumerate(self.full_lines):
            if i >= 2 and (i - 2) % 4 == 0:
                self.full_lines[i] = text_list[(i - 2) // 4]

    def update_srt_from_timestamps(self, timestamps_list=None):
        pass

    def parse_faster_whisper(self, segment_list, language='zh'):
        for i, segment in enumerate(segment_list):
            srt_line = f"{convert_to_hms(segment.start)} --> {convert_to_hms(segment.end)}\n{segment.text.lstrip()}\n\n"
            srt_line = self.replace_dots(srt_line, language)
            if i == len(segment_list) - 1:
                if srt_line[-3] not in ['。', '.']:
                    if language in ['zh', 'ja', 'yue']:
                        srt_line = srt_line.replace('\n\n', '。\n\n')
                    else:
                        srt_line = srt_line.replace('\n\n', '.\n\n')
            # self.text_list.append(segment.text)
            self.full_lines.append(f"{i + 1}\n{srt_line}")

    def get_text_list_from_full_lines(self):
        for i in range(len(self.full_lines)):
            if i >= 2 and (i - 2) % 4 == 0:
                self.text_list.append(self.full_lines[i].strip('\n'))

    def get_timestamps_from_full_lines(self):
        for i in range(len(self.full_lines)):
            if i >= 1 and (i - 1) % 4 == 0:
                hms_list = self.full_lines[i].strip('\n').split(' --> ')
                self.timestamps.append([parse_hms(hms_list[0]), parse_hms(hms_list[1])])


if __name__ == '__main__':
    srt_file = './faster_whisper.srt'
    from CVSrt import CVSrt

    cvs = CVSrt()
    cvs.read_srt(srt_file)
    print(cvs.full_lines)
    print(cvs.text_list)
