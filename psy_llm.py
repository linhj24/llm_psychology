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

def save_questionnaire_file(conversation_info: dict,turn_num: int, question_type: str, noun: str, sensory: str,
                            file_dir:str = "./answers/",):
    save_json_file_name = file_dir + f"turn_num_{turn_num}_question_type_{question_type}_noun_{noun}_sensory_{sensory}_questionnaire.json" # {questionnaire_lang}_request_{request_lang}
    with open(save_json_file_name, "w", encoding='utf-8') as file:
        json.dump(conversation_info, file, ensure_ascii=False, indent=4)  # 使用 indent=4 使文件格式更美观
    print(f"saved to file {save_json_file_name}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # parser.add_argument('-a', '--agent', type=int, default=3, help='Agent number (default: 3)')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port number (default: 8080)')
    parser.add_argument('-qt', '--question_type', type=str, default='create', help='Question type (default: "create")')
    parser.add_argument('-t', '--turn_num', type=int, default=3, help='Turns (default: 3.0)')
    parser.add_argument('-n', '--noun', type=str, default='方向', help='noun (default: "方向")')
    parser.add_argument('-s', '--sensory', type=str, default='颜色', help='sensory (default: "颜色")')

    args = parser.parse_args()

    llama_client = LlamaClient(base_url=f'http://127.0.0.1:{args.port}') 

    conversation_info = {}
    conversation_info['noun'] = args.noun
    conversation_info['sensory'] = args.sensory
    conversation_info['content'] = {}
    question_list = QuestionConfig(args.question_type,QuestionInfoManager("./data"),args.noun,args.sensory) .generate_question()
    
    for turn_id in range(args.turn_num):
        print(f"======{turn_id}======")
        
        conversation_info['content'][f"turn_{turn_id}"] = {}
        for i, quest in enumerate(question_list):
            # prompt = prelude + "\n" + confidence_list + "\n" + answer_format + "\n" \
            #     + question_prefix[0] + f"{i}" + question_prefix[1] + question_prefix[2] + quest + question_prefix[3] + question_prefix[4] + color_candidate
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

            # print(completion["choices"][0]["message"]["content"])
            conversation_info['content'][f"turn_{turn_id}"][f"problem_{i}"] = completion["choices"][0]["message"]["content"]
    
    save_questionnaire_file(conversation_info,args.turn_num,args.question_type,args.noun,args.sensory)