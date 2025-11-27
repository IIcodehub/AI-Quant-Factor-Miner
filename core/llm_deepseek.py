# core/llm_deepseek.py
from openai import OpenAI
import json
from core.llm_base import BaseLLM
from core.prompts import IDEATION_PROMPT_TEMPLATE, CODE_GEN_PROMPT_TEMPLATE
from config import settings
from utils.logger import logger

class DeepSeekLLM(BaseLLM):
    def __init__(self, api_key):
        self.config = settings.MODEL_CONFIG['deepseek']
        self.client = OpenAI(
            api_key=api_key, 
            base_url=self.config['base_url']
        )
        
    def ideation(self, user_base_idea: str, num_variations: int) -> list[dict]:
        prompt = IDEATION_PROMPT_TEMPLATE.format(
            user_base_idea=user_base_idea, 
            num_variations=num_variations,
            stock_columns=settings.STOCK_COLUMNS_DESC,
            index_columns=settings.INDEX_COLUMNS_DESC
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.config['ideation_model'],
                messages=[
                    {"role": "system", "content": "你是一个量化因子构思专家，只输出JSON。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                temperature=self.config['temperature_ideation']
            )
            
            # 清洗 Markdown 标记并解析 JSON
            content = response.choices[0].message.content
            content = content.strip().replace("```json", "").replace("```", "")
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"DeepSeek 构思失败: {e}")
            return None

    def code_generation(self, factor_description: str, factor_name: str) -> str:
        prompt = CODE_GEN_PROMPT_TEMPLATE.format(
            factor_description=factor_description, 
            factor_name=factor_name,
            stock_columns=settings.STOCK_COLUMNS_DESC,
            index_columns=settings.INDEX_COLUMNS_DESC
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.config['coding_model'],
                messages=[
                    {"role": "system", "content": "你是一个量化因子代码生成器。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                temperature=self.config['temperature_coding']
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"DeepSeek 代码生成失败: {e}")
            return None