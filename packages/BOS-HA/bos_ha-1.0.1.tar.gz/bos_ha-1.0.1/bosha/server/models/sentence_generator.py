from datetime import datetime, timedelta
from typing import List, Dict, Optional

class SentenceGenerator:
    """句子生成器，将单个手语识别结果组合成有意义的句子"""
    
    def __init__(self, merge_window: int = 5):
        """
        初始化句子生成器
        
        Args:
            merge_window: 结果合并窗口（秒）
        """
        self.merge_window = merge_window
        self.current_sentence = []  # 当前正在构建的句子
        self.last_result_time = None  # 上次结果时间
        self.sentence_history = []  # 历史句子
        
        # 停止词列表，用于判断句子结束
        self.stop_words = ["。", "！", "？", "再见", "谢谢"]
        
        # 常见短语和句子结构
        self.common_phrases = {
            # 问候类
            ("你", "好"): "你好",
            ("谢", "谢"): "谢谢",
            ("再", "见"): "再见",
            ("早", "上", "好"): "早上好",
            ("晚", "上", "好"): "晚上好",
            ("欢", "迎"): "欢迎",
            
            # 情感类
            ("我", "爱", "你"): "我爱你",
            ("喜", "欢"): "喜欢",
            ("开", "心"): "开心",
            ("生", "气"): "生气",
            ("伤", "悲"): "悲伤",
            ("惊", "讶"): "惊讶",
            
            # 回答类
            ("是",): "是",
            ("否",): "否",
            ("不", "知", "道"): "不知道",
            ("可", "能"): "可能",
            ("当", "然"): "当然",
            ("抱", "歉"): "抱歉",
            
            # 请求类
            ("请", "帮", "助"): "请帮助我",
            ("请",): "请",
            ("我", "想", "要"): "我想要",
            ("我", "需", "要"): "我需要",
            ("给", "我"): "给我",
            ("借", "我"): "借我",
            
            # 身份类
            ("我",): "我",
            ("你",): "你",
            ("他",): "他",
            ("她",): "她",
            ("我", "们"): "我们",
            ("你", "们"): "你们",
            ("他", "们"): "他们",
            
            # 生活类
            ("家",): "家",
            ("学", "校"): "学校",
            ("工", "作"): "工作",
            ("医", "院"): "医院",
            ("商", "店"): "商店",
            ("公", "园"): "公园",
            ("餐", "厅"): "餐厅",
            
            # 物品类
            ("食", "物"): "食物",
            ("水",): "水",
            ("饮", "料"): "饮料",
            ("衣", "服"): "衣服",
            ("鞋", "子"): "鞋子",
            ("帽", "子"): "帽子",
            ("手", "机"): "手机",
            ("电", "脑"): "电脑",
            
            # 动作类
            ("走",): "走",
            ("跑",): "跑",
            ("坐",): "坐",
            ("站",): "站",
            ("吃",): "吃",
            ("喝",): "喝",
            ("看",): "看",
            ("听",): "听",
            ("说",): "说",
            ("写",): "写",
            
            # 数量类
            ("一",): "一",
            ("二",): "二",
            ("三",): "三",
            ("四",): "四",
            ("五",): "五",
            ("六",): "六",
            ("七",): "七",
            ("八",): "八",
            ("九",): "九",
            ("十",): "十",
            
            # 其他
            ("时", "间"): "时间",
            ("今", "天"): "今天",
            ("明", "天"): "明天",
            ("昨", "天"): "昨天",
            ("星", "期"): "星期",
            ("月", "份"): "月份",
            ("年",): "年",
            ("钱",): "钱",
            ("价", "格"): "价格",
            ("颜", "色"): "颜色",
            
            # 组合短语
            ("我", "你", "好"): "我你好",
            ("我", "谢", "谢", "你"): "我谢谢你",
            ("请", "给", "我"): "请给我",
            ("我", "想", "要", "喝"): "我想要喝",
            ("我", "需", "要", "帮", "助"): "我需要帮助",
            ("你", "喜", "欢", "吗"): "你喜欢吗",
            ("我", "不", "知", "道"): "我不知道",
            ("当", "然", "是"): "当然是",
            ("可", "能", "是"): "可能是",
            ("我", "很", "开", "心"): "我很开心",
            ("你", "真", "好"): "你真好",
            ("非", "常", "感", "谢"): "非常感谢",
            ("再", "见", "了"): "再见了",
            ("请", "原", "谅", "我"): "请原谅我",
            ("麻", "烦", "你", "了"): "麻烦你了",
            ("我", "很", "抱", "歉"): "我很抱歉",
            ("没", "关", "系"): "没关系"
        }
    
    def add_result(self, result: Dict) -> Optional[str]:
        """
        添加识别结果，生成句子
        
        Args:
            result: 识别结果，包含text、confidence、timestamp
            
        Returns:
            Optional[str]: 生成的完整句子，如果句子未完成则返回None
        """
        text = result.get("text", "")
        timestamp = result.get("timestamp", datetime.now().timestamp())
        confidence = result.get("confidence", 0.0)
        
        if not text:
            return None
        
        # 转换为datetime对象
        current_time = datetime.fromtimestamp(timestamp)
        
        # 检查是否需要开始新句子
        if self.last_result_time and (
            (current_time - self.last_result_time).total_seconds() > self.merge_window
        ):
            # 保存当前句子
            completed_sentence = self._finalize_sentence()
            if completed_sentence:
                return completed_sentence
        
        # 添加当前结果到句子
        self.current_sentence.append({
            "text": text,
            "confidence": confidence,
            "timestamp": current_time
        })
        self.last_result_time = current_time
        
        # 检查是否需要结束句子
        if text in self.stop_words:
            return self._finalize_sentence()
        
        return None
    
    def _finalize_sentence(self) -> Optional[str]:
        """
        结束当前句子并生成完整句子
        
        Returns:
            Optional[str]: 生成的完整句子
        """
        if not self.current_sentence:
            return None
        
        # 提取文本
        words = [item["text"] for item in self.current_sentence]
        
        # 尝试匹配常见短语
        generated_sentence = self._match_common_phrases(words)
        
        # 如果没有匹配到常见短语，则直接拼接
        if not generated_sentence:
            generated_sentence = "".join(words)
        
        # 保存到历史记录
        self.sentence_history.append({
            "sentence": generated_sentence,
            "timestamp": datetime.now().timestamp(),
            "words": self.current_sentence.copy()
        })
        
        # 清空当前句子
        self.current_sentence = []
        
        return generated_sentence
    
    def _match_common_phrases(self, words: List[str]) -> Optional[str]:
        """
        匹配常见短语
        
        Args:
            words: 单词列表
            
        Returns:
            Optional[str]: 匹配到的短语，否则返回None
        """
        if not words:
            return None
            
        # 复制原始单词列表
        matched_words = words.copy()
        
        # 尝试不同长度的短语匹配，从最长到最短
        max_phrase_len = max(len(phrase) for phrase in self.common_phrases.keys())
        min_phrase_len = 1  # 允许单个词匹配
        
        # 多次遍历，直到没有更多匹配
        while True:
            matched = False
            
            # 从最长短语开始匹配
            for phrase_len in range(min(max_phrase_len, len(matched_words)), min_phrase_len - 1, -1):
                i = 0
                while i <= len(matched_words) - phrase_len:
                    phrase_tuple = tuple(matched_words[i:i+phrase_len])
                    if phrase_tuple in self.common_phrases:
                        # 替换匹配到的短语
                        matched_phrase = self.common_phrases[phrase_tuple]
                        matched_words = matched_words[:i] + [matched_phrase] + matched_words[i+phrase_len:]
                        matched = True
                        break
                    i += 1
                if matched:
                    break
            
            if not matched:
                break
        
        # 如果匹配结果有变化，返回匹配后的句子
        matched_sentence = "".join(matched_words)
        original_sentence = "".join(words)
        
        return matched_sentence if matched_sentence != original_sentence else original_sentence
    
    def get_current_sentence(self) -> str:
        """
        获取当前正在构建的句子
        
        Returns:
            str: 当前句子
        """
        words = [item["text"] for item in self.current_sentence]
        return "".join(words)
    
    def get_sentence_history(self, max_count: int = 10) -> List[Dict]:
        """
        获取历史句子
        
        Args:
            max_count: 最大返回数量
            
        Returns:
            List[Dict]: 历史句子列表
        """
        return self.sentence_history[-max_count:]
    
    def clear(self):
        """清空当前状态"""
        self.current_sentence = []
        self.last_result_time = None
    
    def set_merge_window(self, window: int):
        """
        设置合并窗口
        
        Args:
            window: 合并窗口（秒）
        """
        self.merge_window = window
    
    def merge_sentences(self, sentences: List[str]) -> str:
        """
        将多个句子合并为一个
        
        Args:
            sentences: 句子列表
            
        Returns:
            str: 合并后的句子
        """
        if not sentences:
            return ""
        
        # 移除空句子
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return ""
        
        # 合并句子
        merged = "".join(sentences)
        
        # 简单处理：移除重复内容
        # 注意：这是一个简单的实现，更复杂的去重需要更高级的算法
        words = list(merged)
        unique_words = []
        for word in words:
            if not unique_words or word != unique_words[-1]:
                unique_words.append(word)
        
        return "".join(unique_words)
    
    def ai_polish(self, sentence: str) -> str:
        """
        对句子进行AI润色，提高可读性
        
        Args:
            sentence: 原始句子
            
        Returns:
            str: 润色后的句子
        """
        if not sentence:
            return ""
        
        # 简单的AI润色实现
        # 注意：这是一个简单的实现，更高级的润色需要使用AI模型
        polish_rules = {
            # 添加标点符号
            r"你好": r"你好！",
            r"谢谢": r"谢谢！",
            r"再见": r"再见！",
            r"请帮助我": r"请帮助我！",
            r"我想要": r"我想要。",
            r"我需要": r"我需要。",
            r"我不知道": r"我不知道。",
            r"当然": r"当然！",
            r"可能": r"可能。",
            r"是的": r"是的。",
            r"不是": r"不是。",
            
            # 优化句子结构
            r"我你好": r"我你好！",
            r"我谢谢你": r"我谢谢你！",
            r"你真好": r"你真好！",
            r"非常感谢": r"非常感谢！",
            r"我很开心": r"我很开心！",
            r"我很抱歉": r"我很抱歉。",
            r"没关系": r"没关系。",
        }
        
        polished = sentence
        for rule, replacement in polish_rules.items():
            polished = polished.replace(rule, replacement)
        
        # 确保句子以标点符号结尾
        if polished and polished[-1] not in ["。", "！", "？"]:
            polished += "。"
        
        return polished
    
    def get_sentence_history_by_range(self, start_index: int = 0, end_index: int = -1) -> List[str]:
        """
        获取指定范围的历史句子
        
        Args:
            start_index: 起始索引
            end_index: 结束索引
            
        Returns:
            List[str]: 指定范围的历史句子
        """
        if end_index == -1:
            end_index = len(self.sentence_history)
        
        # 确保索引有效
        start_index = max(0, start_index)
        end_index = min(len(self.sentence_history), end_index)
        
        return [item["sentence"] for item in self.sentence_history[start_index:end_index]]
    
    def get_latest_sentences(self, count: int = 5) -> List[str]:
        """
        获取最近的N条句子
        
        Args:
            count: 句子数量
            
        Returns:
            List[str]: 最近的N条句子
        """
        return [item["sentence"] for item in self.sentence_history[-count:]]