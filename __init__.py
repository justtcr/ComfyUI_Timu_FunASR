import os
import importlib

# 获取当前目录下所有.py文件(排除__init__.py)
node_files = [f[:-3] for f in os.listdir(os.path.dirname(__file__))
              if f.endswith('.py') and not f.startswith('__')]

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

for module_name in node_files:
    module = importlib.import_module(f".{module_name}", package=__name__)

    if hasattr(module, 'NODE_CLASS_MAPPINGS'):
        NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)

    if hasattr(module, 'NODE_DISPLAY_NAME_MAPPINGS'):
        NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']