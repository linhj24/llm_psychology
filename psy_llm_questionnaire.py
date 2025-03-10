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
from questionnaire_config import QuestionnaireConfig
from prompt_config import PromptConfig

def save_questionnaire_file(conversation_info: dict,turn_num: int, 
                            questionnaire_file_name: str,
                            file_dir:str = "./answers/",):
    save_json_file_name = file_dir + f"turn_num_{turn_num}_question_type_{questionnaire_file_name}.json" # {questionnaire_lang}_request_{request_lang}
    with open(save_json_file_name, "w", encoding='utf-8') as file:
        json.dump(conversation_info, file, ensure_ascii=False, indent=4)  # 使用 indent=4 使文件格式更美观
    print(f"saved to file {save_json_file_name}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port number (default: 8080)')
    parser.add_argument('-t', '--turn_num', type=int, default=3, help='Turns (default: 3.0)')
    parser.add_argument('-qf','--questionnaire_file_name',type=str,default='questionnaire',help='Questionnaire File Name(default:"questionnaire")')
    args = parser.parse_args()

    llama_client = LlamaClient(base_url=f'http://127.0.0.1:{args.port}') 
    questionnaire_file_name = args.questionnaire_file_name + ".json"
    with open(questionnaire_file_name,'r',encoding='utf-8') as file:
        questionnaire = json.load(file)

    
    prompt_config = PromptConfig(questionnaire["prompt_config"]["gender"],
                                 questionnaire["prompt_config"]["country"],
                                 questionnaire["prompt_config"]["age"],
                                 questionnaire["prompt_config"]["lang"],
                                 )
    
    question_info = QuestionInfoManager()
    questionnaire_config = QuestionnaireConfig(
                                               prompt_config,                                               
                                               question_info,
                                               questionnaire["question_config_list"]
                                               )
    question_list = questionnaire_config.generate_question_list()
    conversation_info = {}
    conversation_info['questionnaire'] = questionnaire
    conversation_info['content'] = {}
    # question_list = QuestionConfig(args.question_type,QuestionInfoManager("./data"),args.noun,args.sensory) .generate_question()
    
    for turn_id in range(args.turn_num):
        print(f"======{turn_id}======")
        
        conversation_info['content'][f"turn_{turn_id}"] = {}
        for i, quest in enumerate(question_list):
            print(f"------{i}------")
            print(quest)
            completion = llama_client.create_chat_completion(
                messages=[
                        {"role": "system", "content": "你是中国女性，请用中文回答"}, # Todo: prompt
                        {
                            "role": "user",
                            "content": quest
                        }
                    ],
                max_tokens=1280, temperature=0.7
            )
            conversation_info['content'][f"turn_{turn_id}"][f"problem_{i}"] = completion["choices"][0]["message"]["content"]
            print(f"....answer....")
            print(completion["choices"][0]["message"]["content"])
    
    save_questionnaire_file(conversation_info,args.turn_num,args.questionnaire_file_name)