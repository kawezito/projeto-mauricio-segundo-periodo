import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from container import Container
from cli import TerminalInterface


def main():
    container = Container()
    try:
        app = TerminalInterface(container)
        app.iniciar()
    finally:
        container.fechar()


if __name__ == "__main__":
    main()
