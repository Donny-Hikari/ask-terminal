import subprocess
import os
import re
import requests
import json

settings = {
    "text_generation": {
        "endpoint": "local-llama",
        "configs": {
            "server_url": "http://127.0.0.1:40080",
            "prompt": "../prompts/chat-terminal.txt",
            "user": "User",
            "agent": "Alice",
            "options": {
                "temperature": 0.75,
                "top_k": 40,
                "top_p": 0.9,
                "n_predict": 4096,
                "stop": ["[INST]", "User:"],
                "stream": True,
            }
        },
    },
}

class LLamaTextGeneration:
    def __init__(self, settings):
        self.configs = settings['text_generation']['configs']
        self.user = self.configs['user']
        self.agent = self.configs['agent']

        with open(self.configs['prompt']) as f:
            lines = f.readlines()
        self.prompt = ''.join(lines).strip()
        self.n_keep = self.tokenize(lines[0].strip())

    def tokenize(self, content):
        data = {
            "content": content,
        }

        res = requests.post(f"{self.configs['server_url']}/tokenize", json=data)
        return len(json.loads(res.content)['tokens'])

    def chat(self, content, cb=None):
        self.prompt += f"\n{self.user}: {content}\n{self.agent}:"

        req = {
            **self.configs['options'],
            "n_keep": self.n_keep,
            "prompt": self.prompt,
        }

        # Creating a streaming connection with a POST request
        reply = ''
        with requests.post(f"{self.configs['server_url']}/completion", json=req, stream=True) as response:
            # Processing streaming data in chunks
            buffer = ""  # Buffer to accumulate streamed data
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    buffer += chunk
                    try:
                        # Attempt to decode JSON from the accumulated buffer
                        res = json.loads(buffer[6:])

                        reply += res['content']
                        cb(res)

                        buffer = ""  # Clear the buffer after processing
                    except json.JSONDecodeError:
                        pass  # Incomplete JSON, continue accumulating data
        reply = reply.strip()
        self.prompt += f'{reply}'

        return reply

def exec_command(command):
    process = subprocess.run(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def chat(settings):
    text_gen = LLamaTextGeneration(settings)

    while True:
        query = input('User: ')
        print('Alice:', end='')

        def streamResponse(res):
            print(res['content'], end='')
        reply = text_gen.chat(query, streamResponse)
        reply = reply.strip('`')

        confirm = input('Execute the command?(y/n) ')
        if confirm.lower() == 'y':
            process = exec_command(reply)
            print('Stdout: ')
            print(process.stdout.decode())
            print('Stderr: ')
            print(process.stderr.decode())

chat(settings)
