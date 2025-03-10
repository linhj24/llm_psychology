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

class PromptConfig:
    def __init__(self,gender: str, country: str, age: str, lang: str = "English"):
        self.lang = lang # Chinese,English,Japanese
        self.gender = gender # woman,man
        self.country = country # China, American, Japan
        self.age = age

    def generate_prompt(self,llama_client:LlamaClient) -> str:
        prompt_sentence = f"You are a {self.gender} from {self.country}, aged {self.age}."
        if self.lang == 'English':
            return prompt_sentence
        else:
            completion = llama_client.create_chat_completion(
                messages=[
                         # Todo: prompt
                        {
                            "role": "user",
                            "content": f"please transfer to {self.lang}:{prompt_sentence}"
                        }
                    ],
                max_tokens=128, temperature=0
            )
            return completion["choices"][0]["message"]["content"]