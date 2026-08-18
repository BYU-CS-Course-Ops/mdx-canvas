import sys
from pathlib import Path


def entry():
    if sys.argv[1:] == ['skilldir']:
        print(Path(__file__).resolve().parent / 'skills')
        return

    from .main import entry as deploy

    deploy()


if __name__ == '__main__':
    entry()
