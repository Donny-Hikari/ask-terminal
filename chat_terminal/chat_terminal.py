import subprocess
import os
import re
import requests
import json
import argparse
import sys

default_settings = {
    "use_black_list": False,
    "black_list_pattern": r"\b(rm|sudo)\b",
}

class LLamaTextGeneration:
    def __init__(self, settings):
        self.configs = settings['text_generation']['configs']
        self.user = self.configs['user']
        self.agent = self.configs['agent']

        with open(self.configs['prompt']) as f:
            lines = f.readlines()
        self.prompt = ''.join(lines).strip()
        self.n_keep = self.tokenize(self.prompt)

    def tokenize(self, content):
        data = {
            "content": content,
        }

        res = requests.post(f"{self.configs['server_url']}/tokenize", json=data)
        return len(json.loads(res.content)['tokens'])

    def chat(self, req_role, content, res_role, stop=[], cb=None):
        self.prompt += f"\n[{req_role}]: {content}\n[{res_role}]:"

        req = {
            **self.configs['options'],
            "n_keep": self.n_keep,
            "prompt": self.prompt,
            "stop": stop + self.configs['options'].get('stop', []),
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

                        if res['stop']:
                            break

                        buffer = ""  # Clear the buffer after processing
                    except json.JSONDecodeError:
                        pass  # Incomplete JSON, continue accumulating data
        self.prompt += f'{reply.strip()}'

        return reply

    def query_command(self, query, cb=None):
        return self.chat(
            req_role=self.user,
            content=query,
            res_role='Command',
            stop=["[Observation]:", f"[{self.agent}]:"],
            cb=cb,
        )

    def query_answer(self, observation, cb):
        return self.chat(
            req_role='Observation',
            content=observation,
            res_role=self.agent,
            stop=["[Command]:", "[Observation]:"],
            cb=cb,
        )

def exec_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process, stdout, stderr

def chat(settings):
    text_gen = LLamaTextGeneration(settings)

    while True:
        query = input('[User]: ')
        print('[Command]:', end='')

        def streamResponse(res):
            print(res['content'], end='')
        command = text_gen.query_command(query, cb=streamResponse)
        if not command.endswith('\n'):
            print('')
        command = command.strip()
        command = command.strip('`')

        skip_confirm = False
        if settings['use_black_list']:
            if not re.match(settings['black_list_pattern'], command):
                skip_confirm = True

        if not skip_confirm:
            choice = input('Execute the command?(y/n) ')
            confirmed = choice.lower() == 'y'
        else:
            confirmed = True

        observation = "Illegal command: Command execution refused."
        if confirmed:
            process, stdout, stderr = exec_command(command)
            observation = ""
            if len(stdout):
                observation = f"Stdout: {repr(stdout.decode().strip())}\n"
            if len(stderr):
                observation += f"Stderr: {repr(stderr.decode().strip())}"
            observation = observation.strip()
            observation = f'"""{observation}"""'
        print(f'[Observation]: {observation}')

        print('[Alice]:', end='')
        reply = text_gen.query_answer(observation, cb=streamResponse)
        if not reply.endswith('\n'):
            print('')
        reply = reply.strip()

def parse_arg(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, default="configs/chat_terminal.json")
    parser.add_argument('--use-black-list', '-bl', action="store_true", required=False)
    parser.add_argument('--black-list-pattern', '-blc', type=str, required=False)
    return parser.parse_args(argv)

def load_config(config_file):
    with open(config_file) as f:
        configs = json.load(f)
    return configs

def main():
    args = parse_arg()
    settings = load_config(args.config)

    for opt, default_val in default_settings.items():
        if opt not in settings and getattr(args, opt) is None:
            settings[opt] = default_val
        elif getattr(args, opt) is not None:
            settings[opt] = getattr(args, opt)

    chat(settings)

if __name__ == "__main__":
    main()
