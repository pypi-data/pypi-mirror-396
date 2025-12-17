from lazy_loader import attach
import importlib


def attach_and_expose_all(pkg_name: str, g: dict, submodules, submod_attrs=None):
    submod_attrs = submod_attrs or {}
    _getattr, _dir, _all = attach(pkg_name, submodules=submodules, submod_attrs=submod_attrs)
    _all_set = set(_all)

    def __getattr__(name: str):
        try:
            return _getattr(name)
        except AttributeError:
            for mod in submodules:
                m = importlib.import_module(f"{pkg_name}.{mod}")
                if hasattr(m, name) and not name.startswith("_"):
                    obj = getattr(m, name)
                    g[name] = obj
                    _all_set.add(name)
                    return obj
            raise

    def __dir__():
        # 避免为补全而导入所有子模块，保持冷启动轻量
        # 仅返回 attach 提供的名称 + 已经懒暴露过的名称
        return sorted(set(_dir()) | _all_set)

    g["__all__"] = sorted(_all_set)
    return __getattr__, __dir__, g["__all__"]
