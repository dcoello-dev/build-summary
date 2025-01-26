import re
import os
import sys
import time
import argparse

os.environ['PYTHONUNBUFFERED'] = '1'
NVIM_INTEGRATION = "SUMMARY_NVIM" in os.environ.keys()

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


class GenericSink:
    INPUT_REGEX = r"(.*):(\d+): (fatal error|error|warning):(.*)\n"
    ANSI_SCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    CPP_QUICKFIX_FILE = os.environ['CPP_QUICKFIX_FILE']

    def __init__(self):
        self.matches_ = []
        self.quickfix_ = None
        if self.CPP_QUICKFIX_FILE != "":
            self.quickfix_ = open(self.CPP_QUICKFIX_FILE, "w+")

    def __call__(self, line):
        line = self.ANSI_SCAPE.sub('', line)
        match = list(re.findall(self.INPUT_REGEX, line))
        if len(match) > 0:
            self.matches_.append((match[0], line))

    def close(self):
        if self.quickfix_ is not None:
            self.quickfix_.close()

    def matches(self):
        no_repeat = set(self.matches_)
        if self.quickfix_ is not None:
            [self.quickfix_.write(m[1]) for m in no_repeat]
        return sorted(set(self.matches_), key=lambda row: row[0][0])
    
    def format(self):
        mat = self.matches()
        print(len(mat))
        for m in mat:
            print(f"{c(m[0][0], RED if 'error' in m[0][2] else CYAN)}:{m[0][1]} {m[0][3]}")


def parse():
    sink = GenericSink()
    for line in sys.stdin:
        print(line.replace('\n', ''))
        sink(line)
    sink.format()
    sink.close()
    if NVIM_INTEGRATION:
        cmd1 = "nvr --remote-expr \"setqflist([])\""
        cmd2 = f"nvr -q '{GenericSink.CPP_QUICKFIX_FILE}'"
        cmd3 = "nvr -c 'silent copen'"
        cmd = f"{cmd1} && {cmd2} && {cmd3}"
        os.system(cmd)


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
        os.system(
            f"unbuffer {' '.join(sys.argv[1:])} | python3 main.py --parse")
