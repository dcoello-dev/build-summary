import re
import os
import sys
import time
import argparse

os.environ['PYTHONUNBUFFERED'] = '1'

HEADER = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
ORANGE = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
BACKSPACE = '\x08'

def c(str: str, color: str) -> str:
    return color + str + ENDC

def set_args():
    parser = argparse.ArgumentParser(
        description="example script on how to use argparse")
    
    parser.add_argument(
        '-p', '--parse',
        action='store_true',
        default=False,
        help="boolean argument")
    
    return parser.parse_known_args()

class CppSink:
    INPUT_REGEX = r"(.*):(\d*):(\d*): (error|warning):(.*)\n"
    ANSI_SCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    def __init__(self):
        self.matches_ = []
        
    def __call__(self, line):
        line = self.ANSI_SCAPE.sub('', line)
        match = list(re.findall(self.INPUT_REGEX, line))
        if len(match) > 0:
            self.matches_.append(match[0])

    def matches(self):
        return sorted(set(self.matches_), key=lambda row: row[0])

def format(result):
    print(len(result))
    for m in result:
        print(f"{c(m[0], RED if m[3] == 'error' else CYAN)}:{m[1]} {m[4]}")

def parse():
    sink = CppSink()
    for line in sys.stdin:
        print(line.replace('\n', ''))   
        sink(line)
    format(sink.matches())


def execute():
    start_time = time.time()
    os.system(f"unbuffer {' '.join(sys.argv[1:])} | summary-pipe")
    print(f"Execution time: {time.time() - start_time}")

if __name__ == "__main__":
    if sys.argv[1][0] == '-':
        args, unknown = set_args()
        start_time = time.time()
        for line in sys.stdin:
            print(line.replace('\n', ''))   
        print(f"Execution time: {time.time() - start_time}")
    else:
        print(' '.join(sys.argv[1:]))
        os.system(f"unbuffer {' '.join(sys.argv[1:])} | python3 main.py --parse")
