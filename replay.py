#! python
# -*- coding: utf-8 -*-
import os
import subprocess
import sys



def get_last(value):
    string = value.decode("utf-8")
    array = string.split(";")
    if len(array) > 1:
        return array[1].strip()
    return ""


def print_cyan(text):
    return f"\033[96m{text}\033[00m"


home_path = os.path.expanduser("~")
env_shell = os.path.split(os.environ['SHELL'])

if env_shell[-1] == "zsh":
    history_file = ".zsh_history"
elif env_shell == "bash":
    history_file = ".bash_history"
else:
    raise ValueError("Unsupported shell")

history_path = os.path.join(home_path, history_file)

f = open(history_path, "rb")
raw_data = f.read()
f.close()

data = raw_data.split(b"\n")
comms = [get_last(d) for d in data[-1000:]]
to_execute = []
reverse_comms = list(reversed(comms))

for command in reverse_comms:
    if command.startswith("git commit "):
        proc = subprocess.run("git ls-files . --exclude-standard --others -m", capture_output=True, shell=True, check=True)
        files = [f for f in proc.stdout.decode("utf-8").split("\n") if f]
        to_execute = [
            *[f"git add {f}" for f in files],
            command,
            "git push origin `git branch --show-current`"
        ]
        break

if len(to_execute) == 0:
    print("No recent git commands to execute")
    sys.exit(1)

for comm in to_execute:
    try:
        print(f'{print_cyan("Executing")}: {comm}')
        subprocess.run(comm, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e)
        sys.exit(1)
