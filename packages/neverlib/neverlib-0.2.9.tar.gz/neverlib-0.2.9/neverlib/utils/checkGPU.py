'''
Author: 凌逆战 | Never
Date: 2025-09-24 14:28:42
Description: 
检查GPU时候空闲
nohup python -u ./checkGPU.py > ./checkGPU.log 2>&1 &
pid 5993
'''
import time
import subprocess
import numpy as np
from .message import send_QQEmail


def get_gpu_utilization():
    """
    Returns: 返回所有GPU利用率列表
    """
    try:
        result = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'])
        res_list = []
        for res in result.split():
            res_list.append(int(res.decode('utf-8')))
        return res_list
    except Exception as e:
        print(f"Error getting GPU utilization: {e}")
        return None


def get_gpu_utilization2(gpu_id=None):
    try:
        import GPUtil
    except ImportError:
        raise ImportError(
            "GPUtil is required for is_gpu_idle(). "
            "Please install it via `pip install gputil`."
        )
    gpus = GPUtil.getGPUs()  # 获取所有可见的GPU设备列表
    # gpu.memoryUtil表示GPU的内存利用率
    # gpu.load表示GPU的计算利用率
    # gpu.memoryTotal表示GPU的总内存
    # gpu.memoryUsed表示GPU的已使用内存
    # gpu.memoryFree表示GPU的空闲内存
    # 返回所有显卡的利用率列表
    gpu_utilization = np.array([gpu.load * 100 for gpu in gpus])
    if gpu_id is not None:
        return gpu_utilization[gpu_id]
    return gpu_utilization


# 监控显卡利用率
def monitor_gpu_utilization(check_interval=600, duration_limit=1800, threshold=20,
                            MonitorGPUs=None,
                            from_name="凌逆战",
                            from_email="xxxxx@qq.com",
                            from_password="xxxxxxx",
                            to_email="xxxxx@qq.com"):
    """
    check_interval = 5  每5s检查一次
    duration_limit = 300  检查300/60=5min
    threshold = 20  # 利用率阈值
    Returns:
    """
    host_ip = subprocess.check_output(['hostname', '-I']).decode('utf-8').split()[0]    # 172.16.64.33

    while True:
        utilization_mean = []   # 平均利用率
        for i in range(duration_limit // check_interval):  # 30分钟平均一次，每10分钟检查一次
            utilization = get_gpu_utilization2(MonitorGPUs)
            utilization = np.array(utilization)
            utilization_mean.append(utilization)
            time.sleep(check_interval)  # 每隔check_interval分钟检查一次
        utilization_mean = np.mean(utilization_mean, axis=0)
        t_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"{t_now} GPU Utilization: {utilization}")  # [95. 50. 91. 83. 84. 65. 95. 82.]

        # 如果有GPU利用率低于阈值，则发送邮件
        if np.any(utilization_mean < threshold):
            send_QQEmail(title=f"GPU利用率警告",
                         content=f"服务器: {host_ip}\n {t_now} GPU利用率为:{utilization}. 低于阈值 {threshold}% \n",
                         from_name=from_name,
                         from_email=from_email,
                         from_password=from_password,
                         to_email=to_email)
            print(f"Alarm sent: GPU utilization below {threshold}% for GPU(s) {utilization_mean}")


if __name__ == "__main__":
    # print(get_gpu_utilization2(gpu_id=3))
    monitor_gpu_utilization(check_interval=1, duration_limit=3, threshold=100,
                            MonitorGPUs=[4, 5, 6, 7],
                            from_name="xxx",
                            from_email="xxxxxx@qq.com",
                            from_password="xxxxxxx",
                            to_email="xxxxxx@qq.com", )
