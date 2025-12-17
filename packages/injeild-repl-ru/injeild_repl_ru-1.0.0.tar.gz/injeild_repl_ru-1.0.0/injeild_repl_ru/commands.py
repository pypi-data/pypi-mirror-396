# commands.py
import builtins
import os, sys, shutil, pathlib
import math, random
import datetime, time
import json

# =========================
# Встроенные функции Python
# =========================
печать = print
ввод = input
список = list
словарь = dict
кортеж = tuple
множество = set
целое = int
строка = str
число = float
логическое = bool
файл_открыть = open
абсолютное = abs
все = all
любой = any
длина = len
минимум = min
максимум = max
сортировать = sorted
обратный = reversed
карта = map
фильтр = filter
зип = zip
округление = round
степень = pow
тип = type
существует = isinstance
исключение = Exception

# =========================
# OS и Path
# =========================
список_файлов = os.listdir
текущая_папка = os.getcwd
сменить_папку = os.chdir
удалить_файл = os.remove
создать_папку = os.mkdir
проверка_существования = os.path.exists
копировать = shutil.copy
переместить = shutil.move
удалить_папку = shutil.rmtree
пути = pathlib.Path

# =========================
# Math
# =========================
корень = math.sqrt
синус = math.sin
косинус = math.cos
тангенс = math.tan
логарифм = math.log
эксп = math.exp
факториал = math.factorial
pi = math.pi
e = math.e
округление = round

# =========================
# Random
# =========================
случайное_число = random.randint
случайное_дробное = random.random
выбрать_случайное = random.choice
перемешать = random.shuffle
выбрать_несколько = random.sample

# =========================
# datetime
# =========================
текущее_время = datetime.datetime.now
создать_дату = datetime.datetime
создать_время = datetime.time
разница_времени = datetime.timedelta

# =========================
# JSON
# =========================
json_загрузить = json.loads
json_выгрузить = json.dumps

# =========================
# Библиотеки INJEILD
# =========================
_loaded_libs = {}

def библиотека_загрузить(name, module):
    _loaded_libs[name] = module
    печать(f"Библиотека '{name}' загружена")

def библиотека_список():
    return list(_loaded_libs.keys())
