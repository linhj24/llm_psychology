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

sys.path.append(".")
from question_config import QuestionConfig,QuestionInfoManager
from client import LlamaClient
from prompt_config import PromptConfig

class QuestionnaireConfig:
    def __init__(self,
                #  lang:str, 
                 llama_client:LlamaClient,
                 prompt_config:PromptConfig,
                 question_info_manager: QuestionInfoManager,question_config_list:list):
        # question_config_list:format:
        #   [{"question_type: str, noun: str,sensory: str"},{},
        # ]
        self.prompt_config = prompt_config
        self.llama_client = llama_client
        self.questions_abstract = question_config_list
        self.question_info_manager = question_info_manager
        self.questions = []
        pass

    def generate_prompt(self) -> str:
        return self.prompt_config.generate_prompt(self.llama_client)
    
    def generate_question_list(self):
        total_question_list = []
        for question_abstract in self.questions_abstract:
            question_config = QuestionConfig(question_abstract["question_type"],self.question_info_manager,question_abstract["noun"],question_abstract["sensory"],self.prompt_config.lang)
            questions_list = question_config.generate_question(self.llama_client)
            total_question_list.extend(questions_list)
        return total_question_list    
        