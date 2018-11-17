import struct
import wave
import pyaudio
from pathlib import Path

from numpy.ma import frombuffer


def wav_to_ndarray(path: Path):
    with path.open("rb") as f, wave.open(f) as wf:
        wav_data = get_wave_info(path=path)
        length = wav_data['frames']
        print(get_wave_info(path=path))
        return wf.readframes(length)


def get_wave_info(path: Path):
    """WAVEファイルの情報を取得"""
    with path.open("rb") as f, wave.open(f) as wf:
        return {'channel': wf.getnchannels(), 'width': wf.getsampwidth(),
                'frame_rate': wf.getframerate(), 'frames': wf.getnframes(),
                'params': wf.getparams(),
                "long": float(wf.getnframes() / wf.getframerate())
                }


def normalization(array) -> list:
    # エフェクトをかけやすいようにバイナリデータを[-1, +1]に正規化
    # wav -> numpy ndArray
    # int16 の絶対値は 32767
    return frombuffer(array, dtype="int16") / 32768.0


def de_normalization(array) -> bytes:
    # 正規化前のバイナリデータに戻す(32768倍)
    new_data = [int(x * 32767.0) for x in array]
    return struct.pack("h" * len(new_data), *new_data)


"""再生用関数"""


def ndarray_to_device(data: bytes, channel: int, width, rate):
    # PyAudioのインスタンスを生成 (1)
    p = pyaudio.PyAudio()

    # Streamを生成(3)
    stream = p.open(format=p.get_format_from_width(width),
                    channels=channel,
                    rate=rate,
                    output=True)
    # 1024個読み取り
    data = data
    while data != '':
        stream.write(data)
    # 再生が終わると、ストリームを停止・解放 (6)
    stream.stop_stream()
    stream.close()
    # close PyAudio (7)
    p.terminate()


"""保存用関数群"""


def ndarray_to_wav(data: bytes, channel: int, fs: int, path: Path):
    """波形データをWAVEファイルへ出力"""
    with path.open("wb") as f, wave.open(f, "w") as wf:
        wf.setnchannels(channel)
        # 16bit // 2 で サンプルサイズは2(らしい)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(data)
        print("data completely saved")
    print(get_wave_info(path=path))
