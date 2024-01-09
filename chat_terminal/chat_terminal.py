import subprocess
import os
import re

settings = {
    "text_generation": {
        "endpoint": "local-llama",
        "config": {
            "main": "../llama.cpp/main",
            "model": "../models/llama-2-13b-chat.Q4_0.gguf",
            "prompt": "../prompts/chat-terminal.txt",
        },
    },
}

def llama_text_generation(settings):
    text_generation_cfg = settings['text_generation']['config']

    master, slave = os.openpty()

    process = subprocess.Popen([text_generation_cfg['main'], '-m', text_generation_cfg['model'], '-e', '-ngl', '50', '--no-mmap', '-c', '3072', '-b', '512', '-n', '4096', '--keep', '48', '--repeat_penalty', '1.0', '--color', '-i', '-r', 'User:', '--in-prefix', ' ', '--in-suffix', 'Alice:', '-f', text_generation_cfg['prompt']], stdin=slave, stdout=subprocess.PIPE)
    os.set_blocking(process.stdout.fileno(), False)
    os.close(slave)

    def get_output():
        # Read the output of the subprocess
        output = process.stdout.readline()
        return output.decode()

    def put_input(input):
        input = input + '\n'
        os.write(master, input.encode())

    return get_output, put_input

def chat(settings):
    get_output, put_input = llama_text_generation(settings)

    def get_until_user():
        while True:
            out = get_output()
            if len(out) > 0:
                print(out, end='')
            if re.fullmatch(r'User: ?', out):
                break

    while True:
        get_until_user()
        query = input('')
        put_input(query)

chat(settings)
