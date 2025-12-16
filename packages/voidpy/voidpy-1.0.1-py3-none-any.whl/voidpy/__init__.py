from .cor import VoidEngine
from .api import VoidAPI

__version__ = "1.0.0"
__author__ = "MERO"
__telegram__ = "@QP4RM"

_engine = VoidEngine()

def encrypt(source, output=None, layers=3):
    return _engine.encrypt(source, output, layers)

def encrypt_inline(code, layers=3):
    return _engine.encrypt_inline(code, layers)

def enc(void_data):
    return _engine.run_inline(void_data)

def run(void_file):
    return _engine.run(void_file)

def run_inline(void_data):
    return _engine.run_inline(void_data)

def protect(source, output=None, layers=5):
    return _engine.encrypt(source, output, layers)

def execute(void_file):
    return _engine.run(void_file)
