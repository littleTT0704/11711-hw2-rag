import os
from transformers import GPT2TokenizerFast


def split_files_to_chunks(input_folder, max_tokens=512):
    program = []
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
  
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            tokens = tokenizer.encode(text)
            chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]

            for chunk in chunks:
                chunk_text = tokenizer.decode(chunk)
                program.append(chunk_text)  # Append the entire chunk_text as a single element
                
    print(program)
    return program

# Usage
#split_files_to_chunks("/Users/hahaha/Desktop/cmu/24spr/nlp/hw/hw2/files/program")



def load_history(data_dir):
    history = []
    for root, dirs, files in os.walk(os.path.join(data_dir, "history")):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                history += f.read().split("\n\n")
    print(history)
    return history
    
# usage
# load_history("/Users/hahaha/Desktop/cmu/24spr/nlp/hw/hw2/files")