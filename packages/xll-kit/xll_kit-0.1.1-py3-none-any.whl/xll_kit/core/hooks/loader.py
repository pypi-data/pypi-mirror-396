import pkgutil
import importlib
from pathlib import Path
from types import ModuleType
from typing import List, Optional, Set

import logging
logger = logging.getLogger(__name__)


class HookLoader:
    """
    自动加载所有 hooks 的加载器。

    支持：
    - 指定多个扫描包
    - 自动导入子包中的 hooks.py / *_hooks.py
    - 可重复调用但不重复加载（排重）
    """

    def __init__(self, packages: Optional[List[str]] = None):
        self.packages = packages or ["app.hooks", "app.modules"]
        self.loaded_modules: Set[str] = set()

    # -------------------------------------------------------------

    def discover_modules(self, package: str) -> List[str]:
        """发现某个 package 下所有子模块（dotted path）"""
        modules = []
        try:
            pkg = importlib.import_module(package)
        except Exception:
            return modules

        pkg_path = Path(pkg.__file__).parent

        for finder, name, ispkg in pkgutil.walk_packages([str(pkg_path)]):
            full_name = f"{package}.{name}"
            modules.append(full_name)

        return modules

    # -------------------------------------------------------------

    def should_load(self, module_name: str) -> bool:
        """判断模块是否为 hooks 模块"""
        name = module_name.lower()

        return (
            name.endswith(".hooks")
            or name.endswith("_hooks")
            or ".hooks." in name
        )

    # -------------------------------------------------------------

    def import_module(self, module_name: str) -> Optional[ModuleType]:
        """安全导入模块（带日志 + 排重）"""
        if module_name in self.loaded_modules:
            return None

        try:
            module = importlib.import_module(module_name)
            self.loaded_modules.add(module_name)

            logger.info(f"[HOOK LOADER] Loaded {module_name}")
            return module

        except Exception as e:
            logger.warning(f"[HOOK LOADER] Failed to load {module_name}: {e}")
            return None

    # -------------------------------------------------------------

    def load_all(self) -> List[str]:
        """扫描所有 packages 并加载所有 hook 模块"""
        imported = []

        for pkg in self.packages:
            mods = self.discover_modules(pkg)

            for m in mods:
                if self.should_load(m):
                    module = self.import_module(m)
                    if module:
                        imported.append(m)

        return imported


# 全局实例
# global_hook_loader = HookLoader()
