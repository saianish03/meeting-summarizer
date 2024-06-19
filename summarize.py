import subprocess 
import os
import shutil
import warnings
import ollama
import json
import time
warnings.filterwarnings("ignore")
import torch

def move_transcriptions(audio_name:str):
    curr_path = os.getcwd()
    names = audio_name.split(".")
    names.pop()
    audio_name = ""
    for i in names:
        audio_name+=i
    transcr_path = os.path.join(curr_path, 'transcriptions', f'{audio_name}')
    if not os.path.exists(transcr_path):
        os.makedirs(transcr_path)
    files = os.listdir(curr_path)
    to_return = []
    for file in files:
        if file.split('.')[-1] in ['json', 'srt', 'tsv', 'txt', 'vtt']:
            source_file = os.path.join(curr_path, file)
            dest_file = os.path.join(transcr_path, file)
            shutil.move(source_file, dest_file)
            if "json" in dest_file:
                to_return.append(dest_file)
    return to_return[0]

def audio_to_text(file_path):
    path = str(os.getcwd())
    final_file_path = os.path.join(path, file_path)
    w_t_cmd = f"whisper {final_file_path} --language en --verbose False" # --model medium.en
    print()
    print("Transcribing the audio...")
    print()
    try:
        subprocess.run(w_t_cmd, shell=True)
        print("Audio transcribed successfully")
    except subprocess.CalledProcessError as e:
        print("Error Occured while transcription: ",e)
    
    dest_path = move_transcriptions(file_path)
    return dest_path

def text_summarization(dest_path):
    with open(dest_path, "r") as f:
        data = json.load(f)
    text = data['text']
    print()
    print("Generating the summary...")
    print()
    torch.cuda.set_device(0)
    
    response = ollama.chat(model='gemma', messages=[
            {
            'role': 'system',
            'content': 'Your goal is to summarize the text given to you. It is from a meeting between one or more people. Only output the summary without any additional text in third person form.'
            },
            {
                'role': 'user',
                'content': text,
            },
        ])
    summary = response['message']['content']
    return summary


def generate_summary(file_path):

    start_time = time.time()

    dest_path = audio_to_text(file_path)

    summary = text_summarization(dest_path)
    
    end_time = time.time()
    print("Done!")
    print("Total Time Taken: ", end_time - start_time, "seconds")
    return summary
#     return "Hello"