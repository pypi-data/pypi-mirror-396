from .cor import VoidEngine

_engine = VoidEngine()

def encrypt(source, output=None, layers=3):
    return _engine.encrypt(source, output, layers)

def encrypt_inline(code, layers=3):
    return _engine.encrypt_inline(code, layers)
