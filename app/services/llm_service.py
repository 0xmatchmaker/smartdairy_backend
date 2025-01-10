from typing import Dict, List, Optional
from app.db.models.enums import MemoryType, CoreFocusType
from appl import gen, ppl, AIRole
from datetime import datetime, timedelta

class LLMService:
    """
    LLM服务：使用 APPL + Deepseek 实现文本结构化分析
    """
    
    @ppl
    async def analyze_content(self, content: str) -> Dict:
        """
        分析用户输入的自由文本，提取结构化信息
        """
        prompt = f"""
        请分析以下日记内容，提取结构化信息。重点关注：
        1. 时间点信息
        2. 核心关注点（今日改变、外部期待、个人期待、重要事项）
        3. 情绪状态
        4. 相关标签

        日记内容：
        {content}
        
        请以JSON格式返回分析结果。
        """
        
        with AIRole():
            result = gen()  # APPL会自动处理JSON输出
            
            # 简单验证返回的数据结构
            if not isinstance(result, dict):
                raise ValueError("LLM返回格式错误")
                
            return {
                'memory_type': self._determine_memory_type(result),
                'structured_data': result,
                'tags': result.get('tags', []),
                'emotion_score': result.get('emotion_score', {})
            }

    @ppl
    async def extract_dreams(self, content: str) -> Optional[Dict]:
        """
        从内容中提取与梦想/目标相关的信息
        """
        prompt = f"""
        请分析以下内容，判断是否包含具体的目标或梦想。如果包含，请提取：
        1. 目标标题
        2. 详细描述
        3. 目标日期（如果有）
        4. 目标数值（如果有）
        5. 当前进度（如果有）

        内容：
        {content}
        
        如果不包含具体目标，请返回null。否则返回JSON格式的目标信息。
        """
        
        with AIRole():
            result = gen()
            
            if result is None:
                return None
                
            # 处理日期
            if 'target_date' in result:
                try:
                    result['target_date'] = datetime.strptime(
                        result['target_date'], 
                        '%Y-%m-%d'
                    ).date()
                except ValueError:
                    result['target_date'] = None
            
            return result

    def _determine_memory_type(self, analyzed_data: Dict) -> MemoryType:
        """
        根据分析结果确定记忆类型
        """
        if 'timeline' in analyzed_data:
            return MemoryType.TIMELINE
        elif any(key in analyzed_data for key in ['changes', 'external_expect', 'self_expect', 'important']):
            return MemoryType.CORE_FOCUS
        elif 'dream' in analyzed_data or 'goal' in analyzed_data:
            return MemoryType.DREAM_TRACK
        else:
            return MemoryType.QUICK_NOTE 