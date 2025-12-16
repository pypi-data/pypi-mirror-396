from .cor import VoidEngine

class VoidAPI:
    def __init__(self, layers=3):
        self._engine = VoidEngine()
        self._layers = layers
    
    def set_layers(self, layers):
        self._layers = max(1, min(layers, 10))
    
    def encrypt_file(self, source, output=None):
        return self._engine.encrypt(source, output, self._layers)
    
    def encrypt_code(self, code):
        return self._engine.encrypt_inline(code, self._layers)
    
    def run_file(self, void_file):
        return self._engine.run(void_file)
    
    def run_data(self, void_data):
        return self._engine.run_inline(void_data)
    
    def encrypt_and_run(self, code):
        data = self.encrypt_code(code)
        return self.run_data(data)
