from .cor import VoidEngine

_engine = VoidEngine()

def run(void_file):
    return _engine.run(void_file)

def run_inline(void_data):
    return _engine.run_inline(void_data)
