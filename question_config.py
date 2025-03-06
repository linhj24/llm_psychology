import json
from typing import Dict, List, Any

class QuestionInfoManager:
    """管理数据字典的类，支持文件读写"""
    
    def __init__(self, data_path: str = "./data"):
        self.data_path = data_path
        self.noun_dict: Dict[str, List[str]] = {}
        self.sensory_dict: Dict[str, List[str]] = {}
        self.helpful_info: Dict[str, Any] = {}
        self._load_data()

    def _load_data(self):
        """从文件加载数据"""
        try:
            # 加载名词字典
            with open(f"{self.data_path}/noun_dict.json", "r", encoding="utf-8") as f:
                self.noun_dict = json.load(f)
            
            # 加载感官字典
            with open(f"{self.data_path}/sensory_dict.json", "r", encoding="utf-8") as f:
                self.sensory_dict = json.load(f)
            
            # 加载帮助信息
            with open(f"{self.data_path}/helpful_info.json", "r", encoding="utf-8") as f:
                self.helpful_info = json.load(f)
                
        except FileNotFoundError:
            # 如果文件不存在，创建默认数据
            self._initialize_default_data()
            self.save_data()

    def _initialize_default_data(self):
        """初始化默认数据"""
        self.noun_dict = {"方向": ["东", "西", "南", "北"]}
        self.sensory_dict = {"颜色": ["红", "橙", "黄", "绿", "青", "蓝", "紫", "黑", "白"]}
        self.helpful_info = {
            'question': '请给出括号中词语相对应的',
            'choices': ["\n你可以在以下", "选择你认为合适的：【", "】,如果你认为都不合适，可以写你认为合适的"],
            'intro': '\n请从 1 - 7 中选择一个数字，表示您的自信程度。\n如果您有明确的理由，请再加以说明。',
            'confidence': '1代表完全没有自信\n2代表较低自信\n3代表中等偏低自信\n4代表不好说，难以界定\n5代表中等偏高自信\n6代表较高自信\n7代表非常有自信',
            'format': ['\n请将你选择的', '和自信程度用括号括起来。例如【', '，分数】。']
        }

    def save_data(self):
        """将数据保存到文件"""
        # 保存名词字典
        with open(f"{self.data_path}/noun_dict.json", "w", encoding="utf-8") as f:
            json.dump(self.noun_dict, f, ensure_ascii=False, indent=2)
        
        # 保存感官字典
        with open(f"{self.data_path}/sensory_dict.json", "w", encoding="utf-8") as f:
            json.dump(self.sensory_dict, f, ensure_ascii=False, indent=2)
        
        # 保存帮助信息
        with open(f"{self.data_path}/helpful_info.json", "w", encoding="utf-8") as f:
            json.dump(self.helpful_info, f, ensure_ascii=False, indent=2)

    def reload_data(self):
        """重新加载数据"""
        self._load_data()

    def add_noun_category(self, category: str, items: List[str]):
        """添加新的名词类别"""
        self.noun_dict[category] = items
        self.save_data()

    def add_sensory_category(self, category: str, items: List[str]):
        """添加新的感官类别"""
        self.sensory_dict[category] = items
        self.save_data()

class QuestionConfig:
    """
    A class to configure synesthesia-related questions for a large language model.
    """
    def __init__(self, question_type: str,question_info_manager: QuestionInfoManager, noun: str,sensory: str):
        """
        Initialize the QuestionConfig instance.
        
        :param question_type: Type of synesthesia question (e.g., "color-hearing", "shape-taste").
        :param modality_mapping: A dictionary defining how one sensory modality maps to another.
        :param difficulty: The difficulty level of the question (e.g., "easy", "medium", "hard").
        """
        self.question_type = question_type # 生成任务 判别任务
        self.question_info_manager = question_info_manager
        self.noun = noun
        self.sensory = sensory
        
    
    def generate_question(self):
        if self.question_type == "judge":
            question_list = []
            question_prefix = "你认为" + self.noun
            question_connection = "对应" + self.sensory
            question_suffix = "吗?只回答是或不是"
            for noun_content in self.question_info_manager.noun_dict[self.noun]:
                for sensory_content in self.question_info_manager.sensory_dict[self.sensory]:
                    question = question_prefix + noun_content + question_connection + sensory_content + question_suffix
                    question_list.append(question)    
            return question_list
        elif self.question_type == "create":
            question_list = [] 
            noun_dict = self.question_info_manager.noun_dict
            sensory_dict = self.question_info_manager.sensory_dict
            helpful_info = self.question_info_manager.helpful_info
            sensory_choices_str = ' '.join(str(sensory_content) for sensory_content in sensory_dict[self.sensory])
            for i, noun_content in enumerate(noun_dict[self.noun]):
                question_suffix = "问题" + str(i) + ":给出【" + noun_content + "】对应的" + self.sensory
                question = helpful_info['question'] + self.sensory + \
                            helpful_info['choices'][0] + self.sensory + \
                            helpful_info['choices'][1] + sensory_choices_str +\
                            helpful_info['choices'][2] + self.sensory + \
                            helpful_info['intro'] + helpful_info['confidence'] + \
                            helpful_info['format'][0] + self.sensory + \
                            helpful_info['format'][1] + self.sensory + \
                            helpful_info['format'][2] + question_suffix
                # print(question)
                question_list.append(question)
            
            return question_list

# print("begin")
# a = QuestionConfig("create",QuestionInfoManager("."),"方向","颜色")
# a.generate_question()
# print("end")
