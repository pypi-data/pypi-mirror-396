# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/6/14
"""
babble噪声生成
"""
import os
import torch
import random
import numpy as np
import soundfile as sf
import pickle

from neverlib.utils import get_path_list
from vad import EnergyVAD
from utils.audio_aug import volume_aug, add_reverb
from joblib import Parallel, delayed
from multiprocessing import Pool

vad = EnergyVAD(
    sample_rate=16000,
    frame_length=25,  # in milliseconds
    frame_shift=20,  # in milliseconds
    energy_threshold=0.05,  # you may need to adjust this value
    pre_emphasis=0.95,
)  # default values are used here


def get_one_babble(speech_path_list, rir_path_list):
    sub_len = 0
    sub_list = []
    while sub_len < sentence_len:
        speech_path = random.choice(speech_path_list)
        rir_path = random.choice(rir_path_list)
        # 加rir
        with open(rir_path, 'rb') as f:
            # arrayCoor (2,3) (num_mic, 3(x,y,z))
            # sPos (4,3) (num_source, 3(x,y,z))
            [arrayCoor, sPos, sAziPth, rir, L, rt, c, mtype, n, fs] = pickle.load(f)
            rir = np.array(rir)  # (souece, mic, T) (4, 3, 2668)
            rir_idx = np.random.randint(0, rir.shape[0])  # 随机选择一个source
            sPos = sPos[rir_idx]  # (3,) (x,y,z)
            DistMic2Source_1 = np.sqrt(np.sum((arrayCoor[0] - sPos) ** 2))
            DistMic2Source_2 = np.sqrt(np.sum((arrayCoor[1] - sPos) ** 2))
            if DistMic2Source_1 < 2 or DistMic2Source_2 < 2:
                continue
            rir = rir[rir_idx]

        wav, _ = sf.read(speech_path, dtype='float32', always_2d=True)
        assert wav.shape[-1] == 1, f"音频应该为单通道"
        if len(wav) > sentence_len:
            idx = random.randint(0, len(wav) - sentence_len)
            wav = wav[idx:idx + sentence_len]

        wav = wav / np.abs(wav).max()  # 归一化
        wav = vad.apply_vad(wav.T).T

        wav = add_reverb(wav, rir, add_rir_ratio=1)  # 双麦wav
        # 音量增强
        rms = np.sqrt(np.mean(wav ** 2))
        wav *= random.uniform(0.5, 1.0) / rms

        sub_len += len(wav)
        sub_list.append(wav)

    sub_babble = np.concatenate(sub_list, axis=0)
    if sub_len >= sentence_len:
        sub_babble = sub_babble[:sentence_len]
    return sub_babble


def babble_noise_generate(i, speech_path_list, rir_path_list):
    source_num = random.randint(15, 25)
    babble_noise = np.zeros((sentence_len, 2))
    for _ in range(source_num):
        sub_babble = get_one_babble(speech_path_list, rir_path_list)
        babble_noise += sub_babble

    babble_path = os.path.join(target_dir, f"babble_noise_{i}.wav")
    print(babble_path)
    babble_noise = babble_noise / np.max(np.abs(babble_noise)) * 0.5
    sf.write(babble_path, babble_noise, sr)


if __name__ == "__main__":
    speech_dir = "/data/never/kws_data/BigDataset/speech"
    rir_dir = "/data/never/RIR/2mic_Line_r50mm_fs16k_4source_t60mix08_maxdist8m_2w"
    target_dir = "/data/never/SE_dataset/babble_noise10"
    # if os.path.exists(target_dir):
    #     os.system(f"rm -rf {target_dir}")
    #     os.makedirs(target_dir, exist_ok=True)
    # else:
    #     os.makedirs(target_dir, exist_ok=True)
    speech_path_list = get_path_list(speech_dir, "*.wav")
    rir_path_list = get_path_list(rir_dir, "*.rir")

    sentence_num = 20000
    sr = 16000
    volume_range = [0.5, 1.0]
    sentence_len = sr * 10
    # for i in range(10):
    #     babble_noise_generate(i, speech_path_list, rir_path_list)

    # 多核并行处理
    # Parallel(n_jobs=-1)(delayed(babble_noise_generate)(i, speech_path_list, rir_path_list) for i in range(sentence_num))

    pool = Pool(32)  # 创建进程池, 一定要放在 事件函数之后, 不然会保错

    for i in range(sentence_num):
        r = pool.apply_async(func=babble_noise_generate, args=(i, speech_path_list, rir_path_list,))

    pool.close()  # 关闭进程池
    pool.join()  # 回收进程池