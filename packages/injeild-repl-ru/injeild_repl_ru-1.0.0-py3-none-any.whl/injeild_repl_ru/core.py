# core.py
from .commands import *

def start_repl():
    """Запуск INJEILD REPL с русскими командами Python"""
    печать("INJEILD v9.1 REPL (все команды Python на русском)")
    while True:
        try:
            cmd = ввод("INJEILD> ")
            if cmd.strip() in ("выход", "exit", "quit"):
                break
            exec(cmd, globals())
        except Exception as e:
            печать(f"Ошибка: {e}")
