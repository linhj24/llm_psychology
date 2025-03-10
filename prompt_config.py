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

class PromptConfig:
    def __init__(self,gender: str, country: str, age: str, lang: str = "en"):
        self.lang = lang # en,ze
        self.gender = gender # woman,man
        self.country = country # China, American, Japan
        self.age = age

    def generate_prompt(self) -> str:
        prompt_sentence = f"You are a {self.gender} from {self.country}, aged {self.age}."
        if self.lang == 'en':
            
            return prompt_sentence
        else:
            translator = Translator(from_lang="en", to_lang=self.lang)
            prompt_sentence_translation = translator.translate(prompt_sentence_translation)
            print(prompt_sentence_translation)
            return prompt_sentence_translation
            


    