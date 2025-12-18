import sys
from colorama import init

init()

def cursor(x, y):
    sys.stdout.write(f"\033[{y+1};{x+1}H")

def clear():
    sys.stdout.write("\033[2J")
