
import numpy as np
import soundfile as sf


def pcm2wav(pcm_path, wav_path, sr=16000, channels=1, subtype='PCM_16'):
    """
    将pcm文件转换为wav文件
    :param pcm_path: pcm文件路径
    :param wav_path: wav文件路径
    :param sr: 采样率
    :param channels: 声道数
    :param subtype: 子类型
    """
    pcm_data = np.fromfile(pcm_path, dtype=np.int16)
    pcm_data = pcm_data.reshape(-1, channels)  # 支持多通道
    sf.write(wav_path, pcm_data, sr, subtype=subtype)


def wav2pcm(wav_path, pcm_path):
    """
    将wav文件转换为pcm文件
    :param wav_path: wav文件路径
    :param pcm_path: pcm文件路径
    """
    data, _ = sf.read(wav_path, dtype='int16')
    data.tofile(pcm_path)


def read_pcm(file_path, channels=5, sample_rate=16000, sample_width=2):
    # Read raw binary data from the PCM file
    with open(file_path, 'rb') as f:
        raw_data = f.read()

    # Convert binary data to numpy array of the correct dtype
    audio_data = np.frombuffer(raw_data, dtype=np.int16)

    # Reshape the data into a 2D array with shape (num_frames, channels)
    num_frames = len(audio_data) // channels
    audio_data = audio_data.reshape((num_frames, channels))

    return audio_data
