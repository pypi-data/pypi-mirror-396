# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/27
"""

"""
import random
import numpy as np
from scipy import signal
from ..utils import EPS
from ..filter import HPFilter


def limiter(wav, threshold=0.999):
    """
    简单限幅器, threshold=0.999 ~ -0.1dBFS
    超过阈值的样本被压缩到阈值限制
    """
    peak = np.max(np.abs(wav))
    if peak > threshold:
        scalar = threshold / (peak + EPS)
        wav = wav * scalar
    return wav


def add_reverb(wav, rir, ratio=1, mode="same"):
    """添加混响,
    Args:
        wav: [T, channel]
        rir: [T, channel]
        ratio:  0-1
        mode: "same" for SE or "full" for kws
    """
    if random.random() < ratio:
        wav = signal.fftconvolve(wav, rir, mode=mode)  # (28671, 3)
        # note: 建议过完添加混响后再进行归一化, 否则可能会出现溢出
        # 防止削波
        if np.max(np.abs(wav)) > 1:
            scale_factor = 1 / np.max(np.abs(wav))
            wav *= scale_factor
    return wav


def snr_aug_changeNoise(clean, noise, target_snr, hpf=False, sr=16000, order=4, cutoff=100):
    """ 
    保持语音不变, 改变噪声的幅度
    HP: 高通滤波, 如果你的数据工频干扰较高, 建议设置为True, 否则snr会不准
    snr = 10 * log10(signal_power / k*noise_power) 
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hpf:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    # 纯净语音功率, 噪声功率
    clean_power, noise_power = np.mean(clean_tmp ** 2), np.mean(noise_tmp ** 2)
    noise_scale = np.sqrt(clean_power / (noise_power * 10 ** (target_snr / 10) + EPS))
    noisy = clean + noise_scale * noise
    # 防止削波
    if np.max(np.abs(noisy)) > 1:
        scale_factor = 1 / np.max(np.abs(noisy))
        noisy *= scale_factor
        clean *= scale_factor
    return noisy, clean


def snr_aug_changeClean(clean, noise, target_snr, clip_check=True, hpf=False, sr=16000, order=4, cutoff=100):
    """ 
    保持噪声不变，改变纯净语音的幅度以达到目标信噪比
    snr = 10 * log10(k*signal_power/ noise_power)
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hpf:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    # 纯净语音功率, 噪声功率
    clean_power, noise_power = np.mean(clean_tmp ** 2), np.mean(noise_tmp ** 2)
    # 计算纯净信号需要的幅度因子
    clean_scale = np.sqrt(noise_power * 10 ** (target_snr / 10) / (clean_power + EPS))
    noisy = clean * clean_scale + noise
    # 防止削波
    if clip_check:
        if np.max(np.abs(noisy)) > 1:
            scale_factor = 1 / np.max(np.abs(noisy))
            noisy *= scale_factor
            clean *= scale_factor
    return noisy, clean * clean_scale


def snr_diff_changeNoise(clean, noise, target_snr, hpf=False, sr=16000, order=4, cutoff=100):
    """ 
    保持语音不变, 改变噪声的幅度, 和snr_aug_changeNoise作用等效
    snr = 10 * log10(signal_power / k*noise_power) 
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hpf:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    # 纯净语音功率, 噪声功率
    clean_power, noise_power = np.mean(clean_tmp ** 2), np.mean(noise_tmp ** 2)
    source_snr = 10 * np.log10(clean_power / (noise_power + EPS) + EPS)
    noise_dB = source_snr - target_snr     # 噪声还差多少dB
    noise_gain = 10 ** (noise_dB / 20)
    noisy = clean + noise_gain * noise
    # 防止削波
    if np.max(np.abs(noisy)) > 1:
        scale_factor = 1 / np.max(np.abs(noisy))
        noisy *= scale_factor
        clean *= scale_factor
    return noisy, clean


def snr_diff_changeClean(clean, noise, target_snr, clip_check=True, hpf=False, sr=16000, order=4, cutoff=100):
    """ 
    保持噪声不变, 改变纯净语音的幅度, 和snr_aug_changeClean作用等效
    snr = 10 * log10(signal_power / k*noise_power) 
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hpf:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    # 纯净语音功率, 噪声功率
    clean_power, noise_power = np.mean(clean_tmp ** 2), np.mean(noise_tmp ** 2)
    source_snr = 10 * np.log10(clean_power / (noise_power + EPS) + EPS)
    clean_dB = target_snr - source_snr     # 纯净语音还差多少dB
    clean_gain = 10 ** (clean_dB / 20)
    noisy = clean_gain * clean + noise
    # 防止削波
    if clip_check:
        if np.max(np.abs(noisy)) > 1:
            scale_factor = 1 / np.max(np.abs(noisy))
            noisy *= scale_factor
            clean *= scale_factor
    return noisy, clean * clean_gain


def snr_aug_Interpolation(clean, noise, target_snr, hpf=False, sr=16000, order=4, cutoff=100):
    """
    在已知clean_len<=noise_len的情况下
    将clean插入到noise中的snr aug方法
    Args:
        clean: 语音
        noise: 噪声
        snr: snr=random.uniform(*snr_range)
    """
    clean_len, noise_len = clean.shape[0], noise.shape[0]
    assert clean_len <= noise_len, f"clean_len must be less than noise_len."
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hpf:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    noisy = noise.copy()
    index = random.randint(0, noise_len - clean_len)
    noise_tmp = noise_tmp[index:index + clean_len, :]
    # 这里必须把clip_check设置为False, 否则外面的noise和里面的不一致
    noisy_tmp, clean_tmp = snr_aug_changeClean(clean_tmp, noise_tmp, target_snr, clip_check=False, hpf=False)
    noisy[index:index + clean_len, :] = noisy_tmp
    # 防止削波
    if np.max(np.abs(noisy)) > 1:
        scale_factor = 1 / np.max(np.abs(noisy))
        noisy *= scale_factor
        clean *= scale_factor
    return noisy, np.pad(clean, ((index, noise_len - index - clean_len), (0, 0)))


def get_snr_use_vad(wav, vad, sr=16000):
    # 通过vad获得语音原始的snr
    wav = HPFilter(wav, sr=sr, order=6, cutoff=100)
    vadstart, vadend = vad["start"], vad["end"]
    noise = np.concatenate([wav[:vadstart], wav[vadend:]], axis=0)
    speech_segment = wav[vadstart:vadend]

    # 计算信噪比
    # 统计语音段的均方功率谱
    P_speech_noise = np.mean(speech_segment ** 2)  # 语音+噪声功率
    # P_speech_noise = np.mean(wav ** 2)  # 如果用全局的, 会存在噪声功率过大的问题, 导致snr过低
    P_noise = np.mean(noise ** 2)  # 纯噪声功率

    # 计算净语音功率(确保非负)
    P_speech = max(P_speech_noise - P_noise, 1e-8)
    if P_noise < 1e-8:
        P_noise = 1e-8

    snr = 10 * np.log10(P_speech / P_noise)  # 计算 SNR
    # snr保留小数点后一位
    return round(snr, 1)


def snr_aug_vad_Interpolation(clean, noise, target_snr, vad, hpf=False, sr=16000, order=4, cutoff=100):
    """
    在已知clean_len<=noise_len的情况下, 将clean插入到noise中的snr aug方法,
    使用VAD信息, 精确地找到语音位置
    Args:
        clean: 语音
        noise: 噪声
        vad: {"start": xxx, "end": xxx}
    """
    clean_len, noise_len = clean.shape[0], noise.shape[0]
    assert clean_len <= noise_len, f"clean_len must be less than noise_len."
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    noisy = noise.copy()
    index = random.randint(0, noise_len - clean_len)
    noise = noise[index:index + clean_len, :]  # 现在语音和噪声长度一致
    if hpf:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    # 只根据语音段求SNR
    clean_vad = clean_tmp[vad["start"]:vad["end"]]
    noise_tmp = noise_tmp[vad["start"]:vad["end"]]
    power_clean, power_noise = np.mean(clean_vad ** 2), np.mean(noise_tmp ** 2)
    snr_in = 10 * np.log10(power_clean / (power_noise + EPS) + EPS)
    clean_dB = target_snr - snr_in  # 语音还差多少dB
    # noise_dB = snr_in - target_snr    # 噪声还差多少dB
    clean_gain = 10 ** (clean_dB / 20)
    noisy_tmp = clean_gain * clean + noise

    noisy[index:index + clean_len, :] = noisy_tmp
    # 防止削波
    if np.max(np.abs(noisy)) > 1:
        scale_factor = 1 / np.max(np.abs(noisy))
        noisy *= scale_factor
        clean *= scale_factor
    return noisy, np.pad(clean, ((index, noise_len - index - clean_len), (0, 0))) * clean_gain


# ----------------------------------------------------------------
# 音量增强
# ----------------------------------------------------------------
def volume_norm(wav):
    """
    音量归一化
    :param wav: (T,)
    :return: (T,)
    """
    wav = wav / (np.max(np.abs(wav)) + 1e-8)
    return wav


def volume_aug(wav, range, rate, method="linmax"):
    """音量增强 """
    if random.random() < rate:
        target_level = random.uniform(range[0], range[1])
        if method == "dbrms":
            wav_rms = (wav ** 2).mean() ** 0.5
            scalar = 10 ** (target_level / 20) / (np.max(wav_rms) + EPS)
        elif method == "linmax":
            ipt_max = np.max(np.abs(wav))
            scalar = target_level / (ipt_max + EPS)
        else:
            raise ValueError("method must be 'dbrms' or 'linmax'")
        wav *= scalar
    return wav


def volume_aug_dbrms(wav, target_level, hpf=False, sr=16000, order=4, cutoff=100):
    """
    音量增强, 使用dbrms方法
    为了避免有冲击响应影响了最大值，所以使用dBRMS方法, 一定要选好范围，不然容易削波
    Args:
        wav: 音频
        target_level: 目标音量, 单位dB
        hpf: 是否高通滤波
        sr: 采样率
        order: 滤波器阶数
        cutoff: 截止频率
    """
    wav_tmp = wav.copy()
    if hpf:
        wav_tmp = HPFilter(wav_tmp, sr=sr, order=order, cutoff=cutoff)
    wav_rms = (wav_tmp ** 2).mean() ** 0.5
    scalar = 10 ** (target_level / 20) / (np.max(wav_rms) + EPS)
    wav_opt = wav_tmp * scalar
    return wav_opt


def volume_aug_linmax(wav, target_level, hpf=False, sr=16000, order=4, cutoff=100):
    """
    音量增强, 使用linmax方法
    Args:
        wav: 音频
        target_level: 目标音量, 单位dB
        hpf: 是否高通滤波
        sr: 采样率
        order: 滤波器阶数
        cutoff: 截止频率
    """
    assert target_level > 0 and target_level < 1, "target_level must be between 0 and 1"
    wav_tmp = wav.copy()
    if hpf:
        wav_tmp = HPFilter(wav_tmp, sr=sr, order=order, cutoff=cutoff)
    wav_max = np.max(np.abs(wav_tmp))
    scalar = target_level / (wav_max + EPS)
    wav_opt = wav_tmp * scalar
    wav_opt = limiter(wav_opt)
    return wav_opt


# 注意: 避免在模块导入阶段引入可选依赖 pyloudnorm

def volume_aug_lufs(wav, target_lufs, hpf=False, sr=16000, order=4, cutoff=100):
    """
    音量增强, 使用lufs方法, 
    LUFS是“感知响度” → 跟人耳听感对齐，而且符合国际响度标准。

    LUFS 使用 感知加权（K-weighting）
    - 高频增强（模拟人耳在 3~6kHz 的敏感）
    - 低频衰减（降低 <100Hz 对响度的影响）。
    使用 短时块（400ms）能量 + 响度门限（-70 LUFS） 过滤极静音段。

    Args:
        wav: 音频
        target_lufs: 目标音量, 单位lufs
        hpf: 是否高通滤波
        sr: 采样率
        order: 滤波器阶数
        cutoff: 截止频率

    补充信息: 
    ## 推荐的 target_lufs 值（行业参考）
    平台	推荐目标 LUFS
    YouTube / Spotify	-14
    Apple Music	-16
    广播 / TV	-23
    游戏音频	-16 ~ -18
    有声书	-18 ~ -20
    """
    try:
        import pyloudnorm as pyln
    except Exception as e:
        raise ImportError("需要安装 pyloudnorm 才能使用 volume_aug_lufs: pip install pyloudnorm") from e

    wav_tmp = wav.copy()
    if hpf:
        wav_tmp = HPFilter(wav_tmp, sr=sr, order=4, cutoff=1000)

    # Step2: 创建 LUFS 测量器（ITU-R BS.1770）
    meter = pyln.Meter(sr, block_size=0.400)  # block_size=400ms

    # Step3: 测量当前 LUFS
    loudness = meter.integrated_loudness(wav_tmp)

    # Step4: 计算增益并应用
    loudness_diff = target_lufs - loudness
    scalar = 10 ** (loudness_diff / 20.0)
    wav_opt = wav * scalar

    wav_opt = limiter(wav_opt, threshold=0.999)  # Step5: 限幅
    return wav_opt


def measure_loudness(wav, sr):
    """
    测量音频的 Peak / RMS / LUFS，以及峰均比（Crest Factor）

    参数:
        wav: np.ndarray, 音频波形（范围 [-1, 1]）
        sr: int, 采样率

    返回:
        dict:
            - peak_dbfs: 峰值(dBFS)
            - rms_dbfs: 均方根电平(dBFS)
            - lufs: 感知响度（LUFS，ITU-R BS.1770-4标准）
            - crest_factor_db: 峰均比(dB)，峰值与RMS的差值
    """
    EPS = 1e-9

    # 1. Peak
    peak_linear = np.max(np.abs(wav))
    peak_dbfs = 20 * np.log10(peak_linear + EPS)

    # 2. RMS
    rms_val = np.sqrt(np.mean(wav ** 2))
    rms_dbfs = 20 * np.log10(rms_val + EPS)

    # 3. LUFS
    meter = pyln.Meter(sr, block_size=0.400)  # 400ms 块
    loudness_lufs = meter.integrated_loudness(wav)

    # 4. Crest Factor (峰均比)
    crest_factor_db = peak_dbfs - rms_dbfs

    return {
        "peak_dbfs": peak_dbfs,
        "rms_dbfs": rms_dbfs,
        "lufs": loudness_lufs,
        "crest_factor_db": crest_factor_db
    }


def volume_convert(value,
                   from_unit="linear", to_unit="dBFS",
                   crest_factor_db=None, lufs_offset=None):
    """
    音量单位转换函数

    参数:
        value: float
            输入值（可能是线性幅度、dBFS、LUFS）
        from_unit: str
            输入单位: "linear", "dBFS", "RMS_dBFS", "LUFS"
        to_unit: str
            输出单位: "linear", "dBFS", "RMS_dBFS", "LUFS"
        crest_factor_db: float | None
            峰均比（用于 Peak <-> RMS 的转换）
        lufs_offset: float | None
            LUFS 与 RMS 的差值（用于 RMS <-> LUFS 转换）
            例如, 对人声，LUFS ≈ RMS_dBFS - 1.5

    返回:
        float
    """
    EPS = 1e-9

    # Step 1: 统一转换成线性幅度（以满刻度 1.0 为基准）
    if from_unit == "linear":
        lin_val = value
    elif from_unit in ("dBFS", "Peak_dBFS"):
        lin_val = 10 ** (value / 20)
    elif from_unit == "RMS_dBFS":
        lin_val = 10 ** (value / 20)
    elif from_unit == "LUFS":
        if lufs_offset is None:
            raise ValueError("LUFS ↔ RMS 转换需要提供 lufs_offset")
        rms_dbfs = value + lufs_offset
        lin_val = 10 ** (rms_dbfs / 20)
    else:
        raise ValueError(f"未知单位：{from_unit}")

    # Step 2: 从线性幅度转换到目标单位
    if to_unit == "linear":
        return lin_val
    elif to_unit in ("dBFS", "Peak_dBFS"):
        return 20 * np.log10(lin_val + EPS)
    elif to_unit == "RMS_dBFS":
        if from_unit in ("dBFS", "Peak_dBFS") and crest_factor_db is not None:
            # 用Peak -> RMS
            peak_dbfs = 20 * np.log10(lin_val + EPS)
            return peak_dbfs - crest_factor_db
        return 20 * np.log10(lin_val + EPS)
    elif to_unit == "LUFS":
        if lufs_offset is None:
            raise ValueError("RMS ↔ LUFS 转换需要提供 lufs_offset")
        rms_dbfs = 20 * np.log10(lin_val + EPS)
        return rms_dbfs - lufs_offset
    else:
        raise ValueError(f"未知单位：{to_unit}")
