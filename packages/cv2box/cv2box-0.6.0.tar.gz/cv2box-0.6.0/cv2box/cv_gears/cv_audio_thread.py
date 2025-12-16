# -- coding: utf-8 --
# @Time : 2024/11/23
# @LastEdit : 2025/6/14
# @Author : ykk648
import re
import os
import time

import numpy as np

from ..cv_gears.cv_threads_base import Consumer, Factory, Queue, Process, Event
from ..utils import try_import

sd = try_import('sounddevice', 'cv_audio_thread: pip install sounddevice')


class CVAudioDevice:
    def __init__(self):
        pass

    def get_devices(self, update: bool = False):
        """获取设备列表"""
        if update:
            sd._terminate()
            sd._initialize()
        devices_old = sd.query_devices()
        hostapis = sd.query_hostapis()
        # 要排除的device名称列表
        excluded_names = ['Microsoft']
        # 构建排除的正则表达式模式
        excluded_pattern = re.compile('|'.join(map(re.escape, excluded_names)))
        devices = []
        for hostapi in hostapis:
            # 去掉WDM-KS DIRECT ASIO WASAPI(win  OSS(linux
            included_background = ['MME', 'ALSA']
            if hostapi['name'] in included_background:
                for device_idx in hostapi["devices"]:
                    if not re.search(excluded_pattern, devices_old[device_idx]["name"]):
                        devices_old[device_idx]["hostapi_name"] = hostapi["name"]
                        devices.append(devices_old[device_idx])

        input_devices = [f"{d['name']}" for d in devices if d["max_input_channels"] > 0]
        input_devices_indices = [d["index"] if "index" in d else d["name"] for d in devices if d["max_input_channels"] > 0]
        input_devices_rates = [int(d["default_samplerate"]) for d in devices if d["max_input_channels"] > 0]
        input_devices_channels = [int(d["max_input_channels"]) for d in devices if d["max_input_channels"] > 0]
        output_devices = [f"{d['name']}" for d in devices if d["max_output_channels"] > 0]
        output_devices_indices = [d["index"] if "index" in d else d["name"] for d in devices if d["max_output_channels"] > 0]
        output_devices_rates = [int(d["default_samplerate"]) for d in devices if d["max_output_channels"] > 0]
        output_devices_channels = [int(d["max_output_channels"]) for d in devices if d["max_output_channels"] > 0]
        return input_devices, input_devices_indices, input_devices_rates, input_devices_channels, output_devices, output_devices_indices, output_devices_rates, output_devices_channels

    def set_devices(self, input_device=None, output_device=None):
        """设置输出设备"""
        input_devices, input_device_indices, _, _, output_devices, output_devices_indices, _, _ = self.get_devices()
        if input_device is not None:
            sd.default.device[0] = input_device_indices[input_devices.index(input_device)]
            print(f"CVAudioDevice: Input device: {str(sd.default.device[0])}:{input_device}")
        if output_device is not None:
            sd.default.device[1] = output_devices_indices[output_devices.index(output_device)]
            print(f"CVAudioDevice: Output device: {str(sd.default.device[1])}:{output_device}")


class CVMicrophoneThread(Process):
    def __init__(self, queue_list: [list, None], audio_blocksize=80000, input_device_name=None):
        """
        :param queue_list: [in_queue, out_queue], 原声进in_queue，换声从out_queue中取
        :param config_dict:
        :param input_device_name:
        :param output_device_name:
        """
        super().__init__()

        self.cvad = CVAudioDevice()
        input_devices, input_devices_indices, input_devices_rates, _, output_devices, output_devices_indices, output_devices_rates, _, output_device_index, output_device_name = self.cvad.get_devices()

        self.q_1 = queue_list[0]
        self.q_2 = queue_list[1]
        self._stop_event = Event()
        self.pid_number = os.getpid()

        # set input device
        if input_device_name is not None:
            self.input_device_index = input_devices_indices[input_devices.index(input_device_name)]
        else:
            self.input_device_index = sd.default.device[0]
            input_device_name = input_devices[input_devices_indices.index(self.input_device_index)]
            print(f'Input device not set, use default {input_device_name}')

        self.samplerate = 16000
        self.blocksize = audio_blocksize
        print(f'CVAudioThread: samplerate: {self.samplerate} blocksize: {self.blocksize}')

        self.input_volume = 1

    @classmethod
    def class_name(cls):
        return cls.__name__

    def run(self, ):
        with sd.InputStream(
                device=self.input_device_index,
                channels=1,
                callback=self.audio_callback,
                blocksize=self.blocksize,
                samplerate=self.samplerate,
                dtype="float32",
        ) as stream:
            global stream_latency
            stream_latency = stream.latency
            while not self._stop_event.is_set():
                # pass会导致音频传输卡顿
                sd.sleep(1000)
                # print(stream_latency)
        print('stop_event set, {} {} exit !'.format(self.class_name(), self.pid_number))

    def audio_callback(self, indata, frames, times, status):

        try:
            # # 队列里大于2个就丢掉一个
            # while self.q_1.qsize() > 1:
            #     print('CVAudioThread: q_1 Input queue size > 1, drop one.')
            #     _ = self.q_1.get()
            # while self.q_2.qsize() > 1:
            #     print('CVAudioThread: q_2 Input queue size > 1, drop one.')
            #     _ = self.q_2.get()

            self.q_1.put_nowait([indata * self.input_volume])
            self.q_2.put_nowait([indata * self.input_volume])

        except Exception as e:
            print(str(e))

    def stop(self):
        self._stop_event.set()


class CVAudioFileThread(Process):
    def __init__(self, queue_list: [list, None], audio_blocksize=80000, audio_file_path=None):
        """
        :param queue_list: [out_queue1, out_queue2]
        :param audio_file_path: Path to the audio file to read from
        :param audio_blocksize: Size of audio blocks to read
        """
        super().__init__()

        self.audio_file_path = audio_file_path
        self.q_1 = queue_list[0]
        self.q_2 = queue_list[1]
        self._stop_event = Event()
        self.pid_number = os.getpid()

        self.samplerate = 16000  # Fixed sample rate to match microphone
        self.blocksize = audio_blocksize
        self.input_volume = 1
        print(f'CVAudioFileThread: samplerate: {self.samplerate} blocksize: {self.blocksize}')

    @classmethod
    def class_name(cls):
        return cls.__name__

    def run(self):
        # Load the entire audio file
        audio_tensor = load_wav_torch(self.audio_file_path, sr=self.samplerate)
        total_samples = audio_tensor.shape[0]
        current_pos = 0

        while not self._stop_event.is_set():
            # Extract a block of audio
            end_pos = min(current_pos + self.blocksize, total_samples)
            data = audio_tensor[current_pos:end_pos].cpu().numpy()

            # If we reached the end of file, start from beginning
            if len(data) == 0 or current_pos >= total_samples:
                current_pos = 0
                continue

            # Reshape to match microphone format (N,1)
            if len(data.shape) == 1:
                data = data.reshape(-1, 1)

            try:
                # for realtime stream
                # self.q_1.put_nowait([data * self.input_volume])
                # self.q_2.put_nowait([data * self.input_volume])

                self.q_1.put([data * self.input_volume])
                self.q_2.put([data * self.input_volume])

                # Sleep to simulate real-time playback
                time.sleep(len(data) / self.samplerate)

                # Update position
                current_pos = end_pos

            except Exception as e:
                print(f"Error in audio processing: {e}")

        print('stop_event set, {} {} exit !'.format(self.class_name(), self.pid_number))

    def stop(self):
        self._stop_event.set()


class CVSpeakThread(Consumer):
    def __init__(self, queue_list, audio_2_frame, output_blocksize, fps_counter=False, block=True, **kwargs):
        super().__init__(queue_list, fps_counter, block=block, counter_time=300)
        self.cvad = CVAudioDevice()
        input_devices, input_devices_indices, input_devices_rates, _, output_devices, output_devices_indices, output_devices_rates, _, output_device_index, output_device_name = self.cvad.get_devices()

        self.q_in = queue_list[0]
        self.q_sig = queue_list[1]
        self._stop_event = Event()

        import sounddevice as sd
        # set input device
        if kwargs['output_device_name'] is not None:
            self.output_device_index = output_devices_indices[output_devices.index(kwargs['output_device_name'])]
        else:
            self.output_device_index = sd.default.device[0]
            output_device_name = output_devices[output_devices_indices.index(self.output_device_index)]
            print(f'Output device not set, use default {output_device_name}')

        self.samplerate = 16000
        self.audio_2_frame = audio_2_frame
        self.blocksize = output_blocksize
        print(f'CVAudioThread: samplerate: {self.samplerate} blocksize: {self.blocksize}')

        self.input_volume = 1

    def run(self, ):
        self.stream = sd.OutputStream(device=self.output_device_index, blocksize=self.blocksize, samplerate=self.samplerate, channels=1)
        self.stream.start()

        while not self._stop_event.is_set():
            output_audio = self.q_in.get()[0]
            if output_audio is None:
                self.stop()
                break
            for i in range(self.audio_2_frame):
                sig = self.q_sig.get()[0]
                if sig is None:
                    break
                self.stream.write(output_audio[self.blocksize * i:self.blocksize * (i + 1), ...])
        print('stop_event set, {} {} exit !'.format(self.class_name(), self.pid_number))

    def stop(self):
        self._stop_event.set()
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()


class CVAudioRecThread(Factory):
    def __init__(self, queue_list: list, input_device_name, samplerate=40000, blocksize=4096, fps_counter=False):
        super().__init__(queue_list, fps_counter)
        if input_device_name is not None:
            self.set_devices(input_device_name)
        else:
            print(self.get_devices())
            print('Input device not set, use default.')
        self.stream = sd.InputStream(device=sd.default.device[0], channels=1, blocksize=blocksize,
                                     samplerate=samplerate, dtype="float32")
        self.stream.start()
        self.blocksize = blocksize

        self.stream_out = sd.OutputStream(device=sd.default.device[1], channels=1, samplerate=samplerate)
        self.stream_out.start()

    def exit_func(self):
        """
        If something is None, enter exit func, set `pass` if you want deal with exit by yourself.
        """
        self.exit_signal = False
        # self.stream.stop()
        # self.stream.close()

    def get_devices(self, update: bool = True):
        """获取设备列表"""
        if update:
            sd._terminate()
            sd._initialize()
        devices = sd.query_devices()
        hostapis = sd.query_hostapis()
        for hostapi in hostapis:
            for device_idx in hostapi["devices"]:
                devices[device_idx]["hostapi_name"] = hostapi["name"]
        input_devices = [
            f"{d['name']} ({d['hostapi_name']})"
            for d in devices
            if d["max_input_channels"] > 0
        ]
        input_devices_indices = [
            d["index"] if "index" in d else d["name"]
            for d in devices
            if d["max_input_channels"] > 0
        ]
        return (input_devices, input_devices_indices,)

    def set_devices(self, input_device):
        """设置输出设备"""
        (
            input_devices,
            input_device_indices,
        ) = self.get_devices()
        sd.default.device[0] = input_device_indices[
            input_devices.index(input_device)
        ]

        print(f"Input device: {str(sd.default.device[0])}:{input_device}")

    def forward_func(self):
        data = self.stream.read(self.blocksize)
        self.stream_out.write(data[0].astype(np.float32))
        # print(data)
        return [data[0]]


class CVAudioPlayThread(Consumer):
    def __init__(self, queue_list: list[Queue], output_device_name=None, samplerate=40000, fps_counter=False):
        super().__init__(queue_list, fps_counter)
        if output_device_name is not None:
            self.set_devices(output_device_name)
        else:
            print(self.get_devices())
            print('Output device not set, use default.')
        self.stream = sd.OutputStream(device=sd.default.device[1], channels=1, samplerate=samplerate)
        self.stream.start()

    def get_devices(self, update: bool = True):
        """获取设备列表"""
        if update:
            sd._terminate()
            sd._initialize()
        devices = sd.query_devices()
        hostapis = sd.query_hostapis()
        for hostapi in hostapis:
            for device_idx in hostapi["devices"]:
                devices[device_idx]["hostapi_name"] = hostapi["name"]
        output_devices = [f"{d['name']} ({d['hostapi_name']})" for d in devices if d["max_output_channels"] > 0]
        output_devices_indices = [d["index"] if "index" in d else d["name"] for d in devices if
                                  d["max_output_channels"] > 0]
        return (output_devices, output_devices_indices)

    def set_devices(self, output_device):
        """设置输出设备"""
        (
            output_devices,
            output_device_indices,
        ) = self.get_devices()
        sd.default.device[1] = output_device_indices[
            output_devices.index(output_device)
        ]
        print(f"Output device: {str(sd.default.device[1])}:{output_device}")

    def exit_func(self):
        """
        If something is None, enter exit func, set `pass` if you want deal with exit by yourself.
        """
        print('{} {} exit !'.format(self.class_name(), self.pid_number))
        self.exit_signal = True
        self.stream.stop()
        self.stream.close()

    def forward_func(self, something_in):
        output_audio = something_in[0]
        self.stream.write(output_audio.astype(np.float32))
