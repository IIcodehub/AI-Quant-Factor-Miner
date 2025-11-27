# main.py
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import settings
from data_loader.loader import DataLoader
from core.llm_deepseek import DeepSeekLLM
from core.llm_gemini import GeminiLLM
from engine.code_manager import CodeManager
from engine.executor import Executor
from utils.logger import logger

def get_llm_instance():
    if settings.ACTIVE_PROVIDER == 'deepseek':
        logger.info("正在初始化 DeepSeek 模型...")
        return DeepSeekLLM(api_key=settings.DEEPSEEK_API_KEY)
    elif settings.ACTIVE_PROVIDER == 'gemini':
        logger.info("正在初始化 Gemini 模型...")
        return GeminiLLM(api_key=settings.GEMINI_API_KEY)
    else:
        raise ValueError(f"未知的模型类型: {settings.ACTIVE_PROVIDER}")

def process_single_factor_idea(llm, executor, idea_dict, code_output_dir, factor_output_dir):
    factor_name = idea_dict.get("factor_name")
    factor_desc = idea_dict.get("factor_description")
    
    if not factor_name or not factor_desc:
        logger.warning("构思数据不完整，跳过。")
        return

    logger.info(f"--- 开始处理因子: {factor_name} ---")
    
    # 1. 生成代码
    code = llm.code_generation(factor_desc, factor_name)
    if not code:
        logger.error(f"{factor_name} 代码生成失败。")
        return

    # 2. 保存代码并加载函数
    func = CodeManager.save_and_load_function(
        code_string=code, 
        factor_name=factor_name, 
        output_dir=code_output_dir  
    )
    
    if not func:
        logger.error(f"{factor_name} 函数加载失败。")
        return

    # 3. 执行并保存数据
    success = executor.run(
        factor_func=func, 
        factor_name=factor_name, 
        output_dir=factor_output_dir 
    )
    
    if success:
        logger.info(f"--- 因子 {factor_name} 处理成功 ---")
    else:
        logger.info(f"--- 因子 {factor_name} 处理失败 ---")

def main():
    # ==========================================================================
    # 1. 动态路径生成 logic
    # ==========================================================================
    provider_name = settings.ACTIVE_PROVIDER  
    base_dir = settings.BASE_OUTPUT_DIR

    code_dir = os.path.join(base_dir, provider_name, "codes")
    factor_dir = os.path.join(base_dir, provider_name, "factors") 
    
    logger.info(f"当前模型: {provider_name}")
    logger.info(f"代码保存至: {code_dir}")
    logger.info(f"因子保存至: {factor_dir}")
    
    os.makedirs(code_dir, exist_ok=True)
    os.makedirs(factor_dir, exist_ok=True)
    
    # ==========================================================================
    # 2. 加载数据
    # ==========================================================================
    try:
        loader = DataLoader(settings.DATA_PATH_STOCK, settings.DATA_PATH_INDEX)
        data_bundle = loader.load()
    except Exception as e:
        logger.critical(f"数据加载严重失败: {e}")
        return

    # 3. 初始化 LLM
    try:
        llm = get_llm_instance()
    except ValueError as e:
        logger.critical(str(e))
        return
        
    executor = Executor(data_bundle)

    # 4. 获取任务列表
    tasks = settings.FACTOR_MINING_TASKS
    if not tasks:
        logger.warning("任务列表为空。")
        return

    logger.info(f"即将开始执行 {len(tasks)} 个挖掘任务...")

    # 5. 主循环
    for i, task in enumerate(tasks):
        base_idea = task.get('idea')
        num = task.get('num_variations', settings.DEFAULT_NUM_VARIATIONS)
        
        if not base_idea:
            continue

        logger.info(f"\n====== [任务 {i+1}/{len(tasks)}] 种子: {base_idea} ======")
        
        # 阶段 1: 构思
        ideas = llm.ideation(base_idea, num)
        if not ideas:
            logger.error("构思阶段未返回有效结果，跳过此任务。")
            continue
            
        logger.info(f"AI 成功构思了 {len(ideas)} 个新因子变体。")

        # 阶段 2: 逐个生成和执行
        for j, idea in enumerate(ideas):
            logger.info(f"\n>>> 正在处理变体 {j+1}/{len(ideas)} ...")
            process_single_factor_idea(llm, executor, idea, code_dir, factor_dir)

    logger.info("\n====== 所有任务执行完毕 ======")

if __name__ == "__main__":
    main()