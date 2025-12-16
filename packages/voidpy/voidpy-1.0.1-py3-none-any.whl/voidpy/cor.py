import ast
import hashlib
import struct
import random
import zlib
import base64
from .prs import VoidParser
from .stm import StateManager
from .crp import VoidCrypto
from .vm import VoidVM

class VoidEngine:
    def __init__(self):
        self.parser = VoidParser()
        self.state_mgr = StateManager()
        self.crypto = VoidCrypto()
        self.vm = VoidVM()
        self._seed = None
    
    def _gen_seed(self, data):
        h = hashlib.sha256(data.encode() if isinstance(data, str) else data).digest()
        return struct.unpack('>Q', h[:8])[0]
    
    def encrypt(self, source, output=None, layers=3):
        if isinstance(source, str) and source.endswith('.py'):
            with open(source, 'r', encoding='utf-8') as f:
                code = f.read()
        else:
            code = source
        
        self._seed = self._gen_seed(code)
        random.seed(self._seed)
        
        states = self.parser.parse(code)
        states = self.state_mgr.add_fake_states(states)
        states = self.state_mgr.fragment_logic(states)
        states = self.state_mgr.shuffle_states(states, self._seed)
        
        serialized = self.state_mgr.serialize(states)
        
        encrypted = serialized
        for i in range(layers):
            layer_seed = (self._seed + i * 0x1337) & 0xFFFFFFFFFFFFFFFF
            encrypted = self.crypto.encrypt_layer(encrypted, layer_seed)
        
        header = self._build_header(layers, self._seed)
        final = header + encrypted
        
        if output:
            with open(output, 'wb') as f:
                f.write(final)
            return output
        return final
    
    def encrypt_inline(self, code, layers=3):
        return self.encrypt(code, None, layers)
    
    def _build_header(self, layers, seed):
        magic = b'VOID'
        version = struct.pack('>H', 1)
        layer_b = struct.pack('>B', layers)
        seed_b = struct.pack('>Q', seed)
        check = hashlib.md5(magic + version + layer_b + seed_b).digest()[:4]
        return magic + version + layer_b + seed_b + check
    
    def _parse_header(self, data):
        if data[:4] != b'VOID':
            raise ValueError("MERO_FUK_INVALID_MAGIC")
        version = struct.unpack('>H', data[4:6])[0]
        layers = struct.unpack('>B', data[6:7])[0]
        seed = struct.unpack('>Q', data[7:15])[0]
        check = data[15:19]
        exp_check = hashlib.md5(data[:15]).digest()[:4]
        if check != exp_check:
            raise ValueError("MERO_FUK_CORRUPTED")
        return version, layers, seed, 19
    
    def run(self, void_file):
        with open(void_file, 'rb') as f:
            data = f.read()
        return self.run_inline(data)
    
    def run_inline(self, data):
        if isinstance(data, str):
            data = data.encode('latin-1')
        
        version, layers, seed, offset = self._parse_header(data)
        encrypted = data[offset:]
        
        decrypted = encrypted
        for i in range(layers - 1, -1, -1):
            layer_seed = (seed + i * 0x1337) & 0xFFFFFFFFFFFFFFFF
            decrypted = self.crypto.decrypt_layer(decrypted, layer_seed)
        
        states = self.state_mgr.deserialize(decrypted)
        states = self.state_mgr.unshuffle_states(states, seed)
        states = self.state_mgr.filter_real_states(states)
        
        return self.vm.execute(states)
