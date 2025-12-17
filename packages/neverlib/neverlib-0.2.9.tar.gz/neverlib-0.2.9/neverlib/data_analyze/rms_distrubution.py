'''
Author: 凌逆战 | Never
Date: 2025-03-26 22:13:22
Description: 统计音频语音段rms值分布
'''
import soundfile as sf
from .temporal_features import rms_amplitude
from neverlib.utils import get_path_list


def get_rms_vad(wav_path):
    wav, wav_sr = sf.read(wav_path, always_2d=True)  # (xxx,ch)
    assert wav_sr == sr, f"期望采样率为{sr}, 但是为{wav_sr}, 文件名: {wav_path}"
    vadstart, vadend = from_path_get_vadpoint(wav_path)
    rms = rms_amplitude(wav[vadstart:vadend]).mean()
    # if rms < -75:
    #     print(wav_path, np.round(rms, 2))
    # if rms > -5:
    #     print(wav_path, np.round(rms, 2))
    return rms


if __name__ == "__main__":
    sr = 16000
    wav_dir_list = [
        "/data/never/Dataset/kws_data/Command_Word/Crowdsourcing/en_kws2/train/RealPerson",
        "/data/never/Dataset/kws_data/Command_Word/Crowdsourcing/en_kws2/val/RealPerson",
        "/data/never/Dataset/kws_data/Command_Word/Crowdsourcing/en_kws2/test/RealPerson",
    ]
    wav_path_list = []
    for wav_dir in wav_dir_list:
        wav_path_list.extend(get_path_list(wav_dir, end="*.wav"))

    rms_list = Parallel(n_jobs=64)(delayed(get_rms_vad)(wav_path) for wav_path in wav_path_list)

    # 绘制时长分布直方图
    plt.hist(rms_list, bins=100, edgecolor='black')
    plt.title("RMS Distribution")
    plt.xlabel("RMS (dB)")
    plt.ylabel("number")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("./png_dist/rms_distribution.png")
