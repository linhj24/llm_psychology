import json
from typing import Dict, List, Any
import copy
import json
import numpy as np
import time
import pickle
from tqdm import tqdm
import re
import argparse
import sys
import os
from translate import Translator
sys.path.append(".")
from client import LlamaClient


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
        self.noun_dict = {
            "direction": ["East", "West", "South", "North", "Northeast", "Northwest", "Southeast", "Southwest"],
            "number":["0","1","2","3","4","5","6","7","8","9"]
            }
        self.sensory_dict = {"color": ["Red", "Orange", "Yellow", "Green", "Cyan", "Blue", "Purple", "Black", "White"]}
        self.helpful_info = {
            'question': 'Please provide the corresponding words in parentheses',
            'choices': [ "\nYou can choose from the following",
                        "select the one you believe is appropriate: 【",
                        "】, if you think none are suitable, you can write the one you believe is appropriate"],
            'intro': '\nPlease select a number from 1 to 7 to indicate your level of confidence.\nIf you have a clear reason, please elaborate.',
            'confidence':'1 represents no confidence at all\n2 represents low confidence\n3 represents moderately low confidence\n4 represents uncertainty, difficult to define\n5 represents moderately high confidence\n6 represents high confidence\n7 represents very confident',
            'format': ['\nPlease include your choice',
                        'and your confidence level in parentheses. Responses must strictly follow the format 【',
                        ', confidence level】.']
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
    def __init__(self, question_type: str,question_info_manager: QuestionInfoManager, noun: str,sensory: str,lang:str = "en"):
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
        self.lang = lang
        
    
    def generate_question(self):
        if self.question_type == "judge":
            pass
            # question_list = []
            # question_prefix = "你认为" + self.noun
            # question_connection = "对应" + self.sensory
            # question_suffix = "吗?只回答是或不是"
            # for noun_content in self.question_info_manager.noun_dict[self.noun]:
            #     for sensory_content in self.question_info_manager.sensory_dict[self.sensory]:
            #         question = question_prefix + noun_content + question_connection + sensory_content + question_suffix
            #         question_list.append(question)    
            # return question_list
            return []
        elif self.question_type == "create":
            question_list = [] 
            noun_dict = self.question_info_manager.noun_dict
            sensory_dict = self.question_info_manager.sensory_dict
            helpful_info = self.question_info_manager.helpful_info
            sensory_choices_str = ' '.join(str(sensory_content) for sensory_content in sensory_dict[self.sensory])
            for i, noun_content in enumerate(noun_dict[self.noun]):
                question_suffix = "\nQuestion " + str(i) + ":give " +  self.sensory +"of 【"+ noun_content + "】 " 
                question = helpful_info['question'] + self.sensory + \
                            helpful_info['choices'][0] + self.sensory + \
                            helpful_info['choices'][1] + sensory_choices_str +\
                            helpful_info['choices'][2] + self.sensory + \
                            helpful_info['intro'] + helpful_info['confidence'] + \
                            helpful_info['format'][0] + self.sensory + \
                            helpful_info['format'][1] + self.sensory + \
                            helpful_info['format'][2] + question_suffix
                question_list.append(question)
            return question_list
            # if self.lang == 'en':
            #     return question_list
            # else:
            #     question_list_lang = []
            #     for question in question_list:
            #         translator = Translator(from_lang="en", to_lang=self.lang)
            #         question_translation = translator.translate(question)
            #         question_list_lang.append(question_translation)
            #     return question_list_lang


