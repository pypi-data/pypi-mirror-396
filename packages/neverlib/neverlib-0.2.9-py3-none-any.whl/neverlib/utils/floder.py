'''
Author: 凌逆战 | Never
Date: 2025-03-26 22:13:21
Description: 路径层级互换（支持 Windows / Linux / macOS）
'''

import os
import shutil
from pathlib import Path
from neverlib.utils import get_path_list


def get_leaf_folders(directory):
    # 获取最底层的文件夹路径
    leaf_folders = []
    for root, dirs, _ in os.walk(directory):
        if not dirs:  # 如果当前文件夹没有子文件夹
            leaf_folders.append(root)
    return leaf_folders


def rename_files_and_folders(directory, replace='_-', replacement='_'):
    # 将路径的指定字符替换为指定字符
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if replace in filename:
                new_filename = filename.replace(replace, replacement)
                old_path = os.path.join(root, filename)
                new_path = os.path.join(root, new_filename)
                os.rename(old_path, new_path)
                print(f'Renamed file: {old_path} -> {new_path}')

        for folder in dirs:
            if replace in folder:
                new_folder = folder.replace(replace, replacement)
                old_path = os.path.join(root, folder)
                new_path = os.path.join(root, new_folder)
                os.rename(old_path, new_path)
                print(f'Renamed folder: {old_path} -> {new_path}')


def del_empty_folders(path):
    """递归删除空文件夹(先删除子文件夹, 再删除父文件夹)"""
    if not os.path.isdir(path):
        return

    # 获取子文件夹
    subfolders = [
        os.path.join(path, d) for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    ]

    # 递归处理子文件夹
    for subfolder in subfolders:
        del_empty_folders(subfolder)

    # 如果文件夹为空，则删除
    if not os.listdir(path):
        os.rmdir(path)
        print(f"删除空文件夹: {path}")


def change_path(source_dir, idx_1, idx_2):
    # 统一路径类型
    source_dir = Path(source_dir)
    path_list = [Path(p) for p in get_path_list(str(source_dir), end="*.*")]

    print("\n📂 文件路径变更预览（前 5 个）:\n")
    preview_count = min(5, len(path_list))

    for i in range(preview_count):
        path = path_list[i]
        parts = list(path.parts)  # 各层级组成的元组
        try:
            # 交换指定索引层级
            parts[idx_1], parts[idx_2] = parts[idx_2], parts[idx_1]
        except IndexError:
            print(f"[警告] 索引越界：文件 {path}")
            continue

        new_path = Path(*parts)
        print(f"原路径: {path}")
        print(f"新路径: {new_path}\n")

    # 交互确认
    user_input = input("是否确认对所有文件进行以上变更? (y/n): ").strip().lower()
    if user_input != "y":
        print("❌ 操作已取消。")
        return

    print("\n🚀 开始批量处理文件...")
    for path in path_list:
        parts = list(path.parts)
        try:
            parts[idx_1], parts[idx_2] = parts[idx_2], parts[idx_1]
        except IndexError:
            print(f"[跳过] 索引错误：{path}")
            continue

        new_path = Path(*parts)
        new_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(path), str(new_path))
        except Exception as e:
            print(f"[错误] 无法移动 {path} -> {new_path}: {e}")

    print("\n✅ 所有文件处理完成！")
    del_empty_folders(str(source_dir))  # 清理空文件夹
    print("🧹 已清空空目录。")


if __name__ == "__main__":
    # 示例路径（自动根据系统适配）
    source_dir = Path("/data01/never/Dataset/kws_data/Command_Word_NN_wrong_high/Crowdsourcing_wash/zh_kws/train/RealPerson")
    change_path(source_dir, 10, 11)
