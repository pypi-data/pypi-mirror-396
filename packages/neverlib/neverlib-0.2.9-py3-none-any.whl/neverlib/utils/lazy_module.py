'''
Author: 凌逆战 | Never
Date: 2025-09-04
Description: 懒加载模块
'''
import sys
import importlib
from types import ModuleType
from typing import Dict, Tuple, Union, Iterable

class LazyModule(ModuleType):
    """
    一个懒加载模块，可以按需导入子模块或对象。
    - 支持 name -> 'pkg.subpkg.module' 的懒导入(返回模块对象)
    - 支持 name -> ('pkg.subpkg.module', 'attr') 的懒导入(返回模块内的对象)
    - 透传 __spec__/__path__/__all__ 以兼容 import 系统和 IDE 补全
    """
    def __init__(self, name: str, import_structure: Dict[str, Union[str, Tuple[str, str]]], module_spec=None, module_path: Iterable[str] = None):
        super().__init__(name)
        # 提取代理模块配置: __all_from__ 可为 str 或 list[str]
        proxy_modules = []
        if import_structure and "__all_from__" in import_structure:
            raw = import_structure.get("__all_from__")
            if isinstance(raw, (list, tuple)):
                proxy_modules = list(raw)
            elif isinstance(raw, str):
                proxy_modules = [raw]
            # 不参与普通键映射
            import_structure = {k: v for k, v in import_structure.items() if k != "__all_from__"}

        self.__dict__["_import_structure"] = import_structure   # 导入结构
        self.__dict__["_modules"] = {}                          # 模块字典
        self.__dict__["_proxy_modules"] = proxy_modules         # 代理模块(其公开符号可直接在包下访问)
        if module_spec is not None:
            self.__dict__["__spec__"] = module_spec
        if module_path is not None:
            self.__dict__["__path__"] = list(module_path)
        # 若存在代理模块，则不预设 __all__，避免阻断 import * 的 dir() 行为
        if not proxy_modules:
            self.__dict__["__all__"] = sorted(list(import_structure.keys()))

    def __getattr__(self, name):
        import_structure = self.__dict__["_import_structure"]   # 导入结构
        if name in import_structure:
            target = import_structure[name]
            # 目标是模块名: 懒导入并返回模块
            if isinstance(target, str):
                module = importlib.import_module(target)
                self.__dict__["_modules"][name] = module
                setattr(self, name, module)
                return module
            # 目标是 (模块, 属性): 懒导入并返回对象
            if isinstance(target, tuple) and len(target) == 2:
                module_name, attr_name = target
                module = importlib.import_module(module_name)
                obj = getattr(module, attr_name)
                setattr(self, name, obj)
                return obj
        # 若未在显式映射中，尝试到代理模块中查找公开符号
        for proxy_name in self.__dict__.get("_proxy_modules", []):
            mod_cache_key = f"__proxy__::{proxy_name}"
            module = self.__dict__["_modules"].get(mod_cache_key)
            if module is None:
                module = importlib.import_module(proxy_name)
                self.__dict__["_modules"][mod_cache_key] = module
            if hasattr(module, name):
                obj = getattr(module, name)
                setattr(self, name, obj)
                return obj
        raise AttributeError(f"Module {self.__name__} has no attribute {name}")  # 如果模块没有属性，则抛出异常

    def __dir__(self):
        # 将懒加载键与现有属性合并，便于 IDE 补全
        keys = set(self.__dict__.keys()) | set(self.__dict__.get("_import_structure", {}).keys())
        # 若配置了代理模块，将其公开符号加入补全(会触发代理模块导入)
        for proxy_name in self.__dict__.get("_proxy_modules", []):
            module = importlib.import_module(proxy_name)
            for n in dir(module):
                if not n.startswith('_'):
                    keys.add(n)
        return sorted(keys)
