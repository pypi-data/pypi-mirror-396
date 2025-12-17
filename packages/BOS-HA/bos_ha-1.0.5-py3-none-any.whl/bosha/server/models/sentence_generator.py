from datetime import datetime, timedelta
from typing import List, Dict, Optional

class SentenceGenerator:
    """句子生成器，将单个手语识别结果组合成有意义的句子"""
    
    def __init__(self, merge_window: int = 12):
        """
        初始化句子生成器
        
        Args:
            merge_window: 结果合并窗口（秒），扩大到12秒以处理复杂句子
        """
        self.merge_window = merge_window
        self.current_sentence = []  # 当前正在构建的句子
        self.last_result_time = None  # 上次结果时间
        self.sentence_history = []  # 历史句子
        self.context_buffer = []  # 上下文缓冲区，用于理解手语间的关系
        
        # 停止词列表，用于判断句子结束
        self.stop_words = ["。", "！", "？", "再见", "谢谢", "结束", "完成", "好的", "没问题"]
        
        # 扩展常见短语和句子结构
        self.common_phrases = {
            # 问候类
            ("你", "好"): "你好",
            ("谢", "谢"): "谢谢",
            ("再", "见"): "再见",
            ("早", "上", "好"): "早上好",
            ("晚", "上", "好"): "晚上好",
            ("欢", "迎"): "欢迎",
            ("请", "问"): "请问",
            ("没", "关", "系"): "没关系",
            ("不", "客", "气"): "不客气",
            
            # 情感类
            ("我", "爱", "你"): "我爱你",
            ("喜", "欢"): "喜欢",
            ("开", "心"): "开心",
            ("生", "气"): "生气",
            ("伤", "悲"): "悲伤",
            ("惊", "讶"): "惊讶",
            ("感", "动"): "感动",
            ("害", "怕"): "害怕",
            ("骄", "傲"): "骄傲",
            ("失", "望"): "失望",
            ("很", "开", "心"): "很开心",
            ("非", "常", "开", "心"): "非常开心",
            ("我", "很", "开", "心"): "我很开心",
            ("我", "很", "感", "动"): "我很感动",
            ("你", "真", "好"): "你真好",
            ("非", "常", "感", "谢"): "非常感谢",
            
            # 回答类
            ("是",): "是",
            ("否",): "否",
            ("不", "知", "道"): "不知道",
            ("可", "能"): "可能",
            ("当", "然"): "当然",
            ("抱", "歉"): "抱歉",
            ("对",): "对",
            ("错",): "错",
            ("好", "的"): "好的",
            ("没", "问", "题"): "没问题",
            ("一", "定"): "一定",
            ("也", "许"): "也许",
            ("当", "然", "是"): "当然是",
            ("可", "能", "是"): "可能是",
            ("我", "不", "知", "道"): "我不知道",
            
            # 请求类
            ("请", "帮", "助"): "请帮助我",
            ("请",): "请",
            ("我", "想", "要"): "我想要",
            ("我", "需", "要"): "我需要",
            ("给", "我"): "给我",
            ("借", "我"): "借我",
            ("麻", "烦"): "麻烦",
            ("拜", "托"): "拜托",
            ("让", "一", "下"): "让一下",
            ("请", "给", "我"): "请给我",
            ("麻", "烦", "你", "了"): "麻烦你了",
            ("我", "需", "要", "帮", "助"): "我需要帮助",
            
            # 身份类
            ("我",): "我",
            ("你",): "你",
            ("他",): "他",
            ("她",): "她",
            ("我", "们"): "我们",
            ("你", "们"): "你们",
            ("他", "们"): "他们",
            ("老", "师"): "老师",
            ("医", "生"): "医生",
            ("学", "生"): "学生",
            
            # 生活类
            ("家",): "家",
            ("学", "校"): "学校",
            ("工", "作"): "工作",
            ("医", "院"): "医院",
            ("商", "店"): "商店",
            ("公", "园"): "公园",
            ("餐", "厅"): "餐厅",
            ("银", "行"): "银行",
            ("超", "市"): "超市",
            ("邮", "局"): "邮局",
            ("餐", "厅", "吃", "饭"): "餐厅吃饭",
            ("公", "园", "散", "步"): "公园散步",
            
            # 物品类
            ("食", "物"): "食物",
            ("水",): "水",
            ("饮", "料"): "饮料",
            ("衣", "服"): "衣服",
            ("鞋", "子"): "鞋子",
            ("帽", "子"): "帽子",
            ("手", "机"): "手机",
            ("电", "脑"): "电脑",
            ("书", "本"): "书本",
            ("我", "的", "手", "机"): "我的手机",
            ("你", "的", "电", "脑"): "你的电脑",
            
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
            ("读",): "读",
            ("画",): "画",
            ("唱",): "唱",
            ("跳",): "跳",
            ("睡",): "睡",
            ("醒",): "醒",
            ("来",): "来",
            ("去",): "去",
            ("上",): "上",
            ("下",): "下",
            ("我", "想", "要", "喝"): "我想要喝",
            ("我", "想", "要", "吃"): "我想要吃",
            ("请", "帮", "我", "拿"): "请帮我拿",
            
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
            ("百",): "百",
            ("千",): "千",
            ("万",): "万",
            ("第", "一"): "第一",
            ("第", "二"): "第二",
            
            # 时间类
            ("时", "间"): "时间",
            ("今", "天"): "今天",
            ("明", "天"): "明天",
            ("昨", "天"): "昨天",
            ("星", "期"): "星期",
            ("星", "期", "一"): "星期一",
            ("星", "期", "二"): "星期二",
            ("星", "期", "三"): "星期三",
            ("星", "期", "四"): "星期四",
            ("星", "期", "五"): "星期五",
            ("星", "期", "六"): "星期六",
            ("星", "期", "日"): "星期日",
            ("月", "份"): "月份",
            ("年",): "年",
            ("早",): "早",
            ("晚",): "晚",
            ("快",): "快",
            ("慢",): "慢",
            
            # 其他
            ("钱",): "钱",
            ("价", "格"): "价格",
            ("颜", "色"): "颜色",
            ("红", "色"): "红色",
            ("蓝", "色"): "蓝色",
            ("绿", "色"): "绿色",
            ("黄", "色"): "黄色",
            ("大",): "大",
            ("小",): "小",
            ("长",): "长",
            ("短",): "短",
            ("高",): "高",
            ("矮",): "矮",
            ("好",): "好",
            ("坏",): "坏",
            ("新",): "新",
            ("旧",): "旧",
            ("我", "谢", "谢", "你"): "我谢谢你",
            ("你", "喜", "欢", "吗"): "你喜欢吗",
            ("再", "见", "了"): "再见了",
            ("请", "原", "谅", "我"): "请原谅我",
            ("我", "很", "抱", "歉"): "我很抱歉",
            ("开", "始"): "开始",
            ("结", "束"): "结束",
            ("继", "续"): "继续",
            ("停", "止"): "停止",
            ("等", "待"): "等待",
            ("出", "发"): "出发",
            ("返", "回"): "返回",
            ("离", "开"): "离开",
            ("到", "达"): "到达",
            ("停", "留"): "停留"
        }
        
        # 语法规则
        self.grammar_rules = {
            "subject": ["我", "你", "他", "她", "我们", "你们", "他们", "老师", "医生", "学生"],
            "verb": ["喜欢", "想要", "需要", "吃", "喝", "看", "听", "说", "写", "读", "画", "唱", "跳"],
            "object": ["食物", "水", "饮料", "衣服", "鞋子", "帽子", "手机", "电脑", "书本"],
            "adjective": ["红色", "蓝色", "绿色", "黄色", "大", "小", "长", "短", "高", "矮", "新", "旧", "好", "坏"],
            "adverb": ["很", "非常", "十分", "特别", "稍微", "比较"],
            "preposition": ["在", "上", "下", "前", "后", "左", "右", "里", "外", "内", "外"]
        }
        
        # 短语优先级（长度越长，优先级越高）
        self.phrase_priority = sorted(self.common_phrases.keys(), key=lambda x: len(x), reverse=True)
    
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
        
        # 1. 尝试匹配常见短语
        generated_sentence = self._match_common_phrases(words)
        
        # 2. 改进句子结构
        generated_sentence = self._improve_sentence_structure(generated_sentence)
        
        # 3. 保存到历史记录
        self.sentence_history.append({
            "sentence": generated_sentence,
            "timestamp": datetime.now().timestamp(),
            "words": self.current_sentence.copy(),
            "raw_sentence": "".join(words)
        })
        
        # 4. 更新上下文缓冲区
        self.context_buffer.append(generated_sentence)
        if len(self.context_buffer) > 5:  # 保持最近5个句子的上下文
            self.context_buffer = self.context_buffer[-5:]
        
        # 5. 清空当前句子
        self.current_sentence = []
        
        return generated_sentence
    
    def _match_common_phrases(self, words: List[str]) -> Optional[str]:
        """
        智能匹配常见短语，支持子序列匹配和模糊匹配
        
        Args:
            words: 单词列表
            
        Returns:
            Optional[str]: 匹配到的短语，否则返回None
        """
        if not words:
            return None
            
        # 复制原始单词列表
        matched_words = words.copy()
        
        # 计算最大短语长度
        max_phrase_len = max(len(phrase) for phrase in self.common_phrases.keys())
        min_phrase_len = 1  # 允许单个词匹配
        
        # 多次遍历，直到没有更多匹配
        total_matches = 0
        max_iterations = 15  # 增加最大迭代次数以处理复杂序列
        iteration = 0
        
        while iteration < max_iterations:
            matched = False
            iteration += 1
            
            # 从最长短语开始匹配，使用预排序的短语优先级
            for phrase_len in range(min(max_phrase_len, len(matched_words)), min_phrase_len - 1, -1):
                i = 0
                while i <= len(matched_words) - phrase_len:
                    # 当前窗口的单词组合
                    current_window = tuple(matched_words[i:i+phrase_len])
                    
                    # 精确匹配
                    if current_window in self.common_phrases:
                        matched_phrase = self.common_phrases[current_window]
                        matched_words = matched_words[:i] + [matched_phrase] + matched_words[i+phrase_len:]
                        matched = True
                        total_matches += 1
                        break
                    
                    # 支持子序列匹配（允许跳过中间一些字符）
                    if phrase_len > 2:
                        # 尝试子序列匹配，允许跳过1-2个字符
                        for skip in range(1, 3):
                            if i + phrase_len + skip <= len(matched_words):
                                extended_window = tuple(matched_words[i:i+phrase_len+skip])
                                # 检查是否包含当前短语作为子序列
                                if self._is_subsequence(current_window, extended_window):
                                    # 确保current_window存在于common_phrases字典中
                                    if current_window in self.common_phrases:
                                        matched_phrase = self.common_phrases[current_window]
                                        matched_words = matched_words[:i] + [matched_phrase] + matched_words[i+phrase_len+skip:]
                                        matched = True
                                        total_matches += 1
                                        break
                    
                    i += 1
                if matched:
                    break
            
            if not matched:
                break
        
        # 生成匹配后的句子
        matched_sentence = "".join(matched_words)
        return matched_sentence
    
    def _is_subsequence(self, pattern: tuple, sequence: tuple) -> bool:
        """
        检查pattern是否是sequence的子序列
        
        Args:
            pattern: 目标模式
            sequence: 待检查的序列
            
        Returns:
            bool: 是否是子序列
        """
        if not pattern:
            return True
        if not sequence:
            return False
            
        ptr_pattern = 0
        ptr_sequence = 0
        
        while ptr_pattern < len(pattern) and ptr_sequence < len(sequence):
            if pattern[ptr_pattern] in sequence[ptr_sequence]:
                ptr_pattern += 1
            ptr_sequence += 1
        
        return ptr_pattern == len(pattern)
    
    def _add_grammar(self, sentence: str) -> str:
        """
        添加高级语法结构，提高句子可读性和准确性
        
        Args:
            sentence: 原始句子
            
        Returns:
            str: 带有语法结构的句子
        """
        if not sentence:
            return sentence
        
        # 1. 主语-谓语-宾语结构检测与优化
        sentence = self._optimize_spo_structure(sentence)
        
        # 2. 形容词位置优化
        sentence = self._optimize_adjective_position(sentence)
        
        # 3. 检查是否以问候语开头
        greetings = ["你好", "早上好", "晚上好", "欢迎", "再见"]
        for greeting in greetings:
            if sentence.startswith(greeting):
                # 添加感叹号
                if not sentence.endswith("！"):
                    sentence = sentence + "！"
                return sentence
        
        # 4. 检查是否以问号结尾
        question_words = ["吗", "？", "为什么", "什么", "哪里", "谁", "什么时候", "怎么样", "多少"]
        ends_with_question = any(sentence.endswith(word) for word in question_words)
        
        if ends_with_question and not sentence.endswith("？"):
            sentence = sentence + "？"
        
        # 3. 添加适当的标点符号
        if not sentence.endswith(("。", "！", "？")):
            # 根据句子长度和内容添加标点
            if len(sentence) > 15:
                sentence = sentence + "。"
            elif len(sentence) > 8:
                sentence = sentence + "！"
            else:
                sentence = sentence + "。"
        
        return sentence
    
    def _remove_redundancy(self, sentence: str) -> str:
        """
        智能移除句子中的冗余内容，保留关键信息
        
        Args:
            sentence: 原始句子
            
        Returns:
            str: 精简后的句子
        """
        if not sentence:
            return sentence
        
        # 移除连续重复的词（除了标点符号）
        words = []
        prev_word = None
        
        for char in sentence:
            if char in ["。", "！", "？"]:
                # 处理标点符号
                if words and words[-1] in ["。", "！", "？"]:
                    # 替换为更合适的标点
                    words[-1] = char
                else:
                    words.append(char)
                prev_word = char
            else:
                # 处理普通字符
                if char != prev_word:
                    words.append(char)
                prev_word = char
        
        # 移除连续重复的短语
        result = "".join(words)
        
        # 移除常见冗余短语
        redundant_phrases = ["我我", "你你", "他他", "她她", "我们我们", "你们你们", "他们他们"]
        for phrase in redundant_phrases:
            result = result.replace(phrase, phrase[:2])
        
        return result
    
    def _optimize_spo_structure(self, sentence: str) -> str:
        """
        优化主语-谓语-宾语结构
        
        Args:
            sentence: 原始句子
            
        Returns:
            str: 优化后的句子
        """
        # 检查是否缺少主语
        has_subject = any(subject in sentence for subject in self.grammar_rules["subject"])
        if not has_subject:
            # 如果没有主语且句子较长，尝试添加合适的主语
            if len(sentence) > 5:
                # 尝试从上下文获取主语
                if self.context_buffer:
                    # 从最近的句子中提取主语
                    last_sentence = self.context_buffer[-1]
                    for subject in self.grammar_rules["subject"]:
                        if subject in last_sentence:
                            sentence = subject + sentence
                            break
        
        return sentence
    
    def _optimize_adjective_position(self, sentence: str) -> str:
        """
        优化形容词位置，确保形容词在名词之前
        
        Args:
            sentence: 原始句子
            
        Returns:
            str: 优化后的句子
        """
        # 简单的形容词位置优化
        # 例如："苹果红色" -> "红色苹果"
        for adjective in self.grammar_rules["adjective"]:
            for noun in self.grammar_rules["object"] + self.grammar_rules["subject"]:
                if noun + adjective in sentence:
                    sentence = sentence.replace(noun + adjective, adjective + noun)
        
        return sentence
    
    def _improve_sentence_structure(self, sentence: str) -> str:
        """
        改进句子结构，使其更符合自然语言，包含上下文理解
        
        Args:
            sentence: 原始句子
            
        Returns:
            str: 结构优化后的句子
        """
        if not sentence:
            return sentence
        
        # 应用各种优化
        sentence = self._remove_redundancy(sentence)
        sentence = self._add_grammar(sentence)
        sentence = self.ai_polish(sentence)
        
        # 上下文理解与优化
        if self.context_buffer:
            sentence = self._use_context(sentence)
        
        return sentence
    
    def _use_context(self, sentence: str) -> str:
        """
        使用上下文信息优化句子
        
        Args:
            sentence: 原始句子
            
        Returns:
            str: 优化后的句子
        """
        # 简单的上下文理解
        last_sentence = self.context_buffer[-1]
        
        # 1. 指代消解
        pronouns = ["他", "她", "它", "他们", "她们", "它们"]
        for pronoun in pronouns:
            if pronoun in sentence:
                # 尝试从上下文中找到指代的名词
                for noun in self.grammar_rules["subject"] + self.grammar_rules["object"]:
                    if noun in last_sentence and noun not in sentence:
                        sentence = sentence.replace(pronoun, noun)
                        break
        
        return sentence
    
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
        高级AI润色功能，使用更智能的规则和上下文理解
        
        Args:
            sentence: 原始句子
            
        Returns:
            str: 润色后的句子
        """
        if not sentence:
            return ""
        
        # 1. 基础规则润色
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
            r"请": r"请。",
            r"对不起": r"对不起！",
            r"没关系": r"没关系。",
            
            # 优化句子结构
            r"我你好": r"你好！",
            r"我谢谢你": r"谢谢你！",
            r"你真好": r"你真好！",
            r"非常感谢": r"非常感谢！",
            r"我很开心": r"我很开心！",
            r"我很抱歉": r"我很抱歉。",
            r"我喜欢你": r"我喜欢你！",
            r"我讨厌你": r"我讨厌你。",
            r"我想要吃": r"我想要吃东西。",
            r"我想要喝": r"我想要喝饮料。",
            
            # 常见错误修正
            r"你好吗？": r"你好吗？",
            r"谢谢你们": r"谢谢你们！",
            r"早上好啊": r"早上好！",
            r"晚上好啊": r"晚上好！",
        }
        
        polished = sentence
        for rule, replacement in polish_rules.items():
            polished = polished.replace(rule, replacement)
        
        # 2. 高级语法修正
        polished = self._fix_grammar(polished)
        
        # 3. 上下文感知修正
        if self.context_buffer:
            polished = self._context_aware_correction(polished)
        
        # 4. 确保句子以标点符号结尾
        if polished and polished[-1] not in ["。", "！", "？"]:
            # 根据句子情感选择合适的标点
            if any(word in polished for word in ["开心", "喜欢", "谢谢", "好", "棒", "优秀"]):
                polished += "！"
            elif any(word in polished for word in ["抱歉", "对不起", "难过", "悲伤"]):
                polished += "。"
            else:
                polished += "。"
        
        return polished
    
    def _fix_grammar(self, sentence: str) -> str:
        """
        修复常见语法错误
        
        Args:
            sentence: 原始句子
            
        Returns:
            str: 修复后的句子
        """
        # 修正常见的语法错误
        grammar_fixes = {
            # 量词修正
            r"一苹果": r"一个苹果",
            r"一书本": r"一本书",
            r"一水杯": r"一个水杯",
            
            # 动词时态修正（简单实现）
            r"我在吃": r"我正在吃东西。",
            r"我在喝": r"我正在喝饮料。",
            r"我在看": r"我正在看东西。",
            
            # 词序修正
            r"苹果红色": r"红色苹果",
            r"衣服蓝色": r"蓝色衣服",
            r"鞋子黑色": r"黑色鞋子",
        }
        
        fixed = sentence
        for error, correction in grammar_fixes.items():
            fixed = fixed.replace(error, correction)
        
        return fixed
    
    def _context_aware_correction(self, sentence: str) -> str:
        """
        基于上下文的句子修正
        
        Args:
            sentence: 原始句子
            
        Returns:
            str: 修正后的句子
        """
        # 从上下文中提取信息，用于修正当前句子
        if not self.context_buffer:
            return sentence
        
        # 示例：如果上一句提到了具体物品，当前句可以更明确
        last_sentence = self.context_buffer[-1]
        
        # 提取上下文中的名词
        context_nouns = []
        for noun in self.grammar_rules["subject"] + self.grammar_rules["object"]:
            if noun in last_sentence:
                context_nouns.append(noun)
        
        # 如果当前句子有"它"，尝试替换为上下文中的名词
        if "它" in sentence and context_nouns:
            # 选择最近提到的名词
            nearest_noun = context_nouns[-1]
            sentence = sentence.replace("它", nearest_noun)
        
        return sentence
    
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