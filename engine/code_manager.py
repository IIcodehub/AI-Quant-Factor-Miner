# engine/code_manager.py
import os
import re
import sys
import importlib.util
from utils.logger import logger

class CodeManager:
    @staticmethod
    def save_and_load_function(code_string, factor_name, output_dir):
        """清洗代码，保存文件，并动态加载模块"""
        try:
            # 清洗 Markdown
            code_string = re.sub(r"^```python\n", "", code_string, flags=re.MULTILINE)
            code_string = re.sub(r"\n```$", "", code_string, flags=re.MULTILINE)
            code_string = code_string.strip()

            if not code_string:
                logger.error("AI 返回了空代码。")
                return None

        
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, f"{factor_name}.py")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code_string)
            logger.info(f"代码已保存至: {filepath}")

            module_name = factor_name
            if module_name in sys.modules:
                del sys.modules[module_name]

            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                logger.error(f"无法创建模块 spec: {filepath}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if hasattr(module, factor_name):
                return getattr(module, factor_name)
            else:
                logger.error(f"模块中未找到函数: {factor_name}")
                return None

        except Exception as e:
            logger.error(f"代码保存/加载出错: {e}")
            return None