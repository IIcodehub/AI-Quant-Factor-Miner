# engine/executor.py
import os
import pandas as pd
from config import settings
from utils.logger import logger

class Executor:
    def __init__(self, data_bundle):
        self.data_bundle = data_bundle

    def run(self, factor_func, factor_name, output_dir):
        try:
            logger.info(f"正在执行函数: {factor_name} ...")
            
            df_result = factor_func(
                df_raw=self.data_bundle['stock'],
                df_index=self.data_bundle['index']
            )


            if not isinstance(df_result, pd.DataFrame):
                logger.error(f"返回类型错误: {type(df_result)}")
                return False
            
        
            expected_base_cols = settings.REQUIRED_OUTPUT_COLS
            if not all(col in df_result.columns for col in expected_base_cols):
                 logger.error(f"缺少必要索引列: {expected_base_cols}")
                 return False
            
            if factor_name not in df_result.columns:
                 logger.error(f"结果缺少因子值列: {factor_name}")
                 return False

   
            final_cols = expected_base_cols + [factor_name]
            df_final = df_result[final_cols]
            df_final['SecuCode'] = df_final['SecuCode'].astype(str).str.slice(0, 6)

            output_filepath = os.path.join(output_dir, f"{factor_name}.parquet")
            df_final.to_parquet(output_filepath, index=False)
            logger.info(f"保存成功: {output_filepath}")
            return True

        except Exception as e:
            logger.error(f"执行时发生运行时错误: {e}")
            return False