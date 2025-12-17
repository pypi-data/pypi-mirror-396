# 获取一个python脚本里面所有的函数名

import ast
from typing import List


def get_function_names(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as file:
        source = file.read()
    tree = ast.parse(source, filename=file_path)
    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)
    return names


if __name__ == '__main__':
    print(get_function_names('../utils/checkGPU.py'))
