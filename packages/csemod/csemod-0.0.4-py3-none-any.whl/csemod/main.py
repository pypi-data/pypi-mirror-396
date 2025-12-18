""" A simple Python Module for Educational Purpose"""

import pyperclip
from .content import answer_dict

def get(arg_string):
    arg_string = arg_string.replace(" ", "").replace("_", "").lower()
    
    # First try exact match
    answer_text = answer_dict.get(arg_string, None)
    
    # If not found, search for keys starting with arg_string
    if answer_text is None:
        for key in answer_dict.keys():
            if key.startswith(arg_string):
                answer_text = answer_dict[key]
                break
    
    if answer_text is None:
        print("Not found")
    else:
        pyperclip.copy(answer_text)
        print("Success")


def show():
    print("Available Programs:")
    for key in answer_dict.keys():
        print(f"- {key}")