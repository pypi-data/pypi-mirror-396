import hashlib
import struct

class VoidCrypto:
    def __init__(self):
        self._rnd = 16
        self._blk = 64
        self._sig = b'MERO_VOID_QP4RM'
        self._magic = [0x4D, 0x45, 0x52, 0x4F, 0x56, 0x4F, 0x49, 0x44]
    
    def _kdf(self, seed, length):
        key = b''
        counter = 0
        while len(key) < length:
            data = struct.pack('>QI', seed, counter) + self._sig
            key += hashlib.sha256(data).digest()
            counter += 1
        return key[:length]
    
    def _mero_transform(self, data, key):
        result = bytearray(len(data))
        klen = len(key)
        mlen = len(self._magic)
        
        for i, b in enumerate(data):
            k = key[i % klen]
            m = self._magic[i % mlen]
            
            v = b
            v = (v + k) & 0xFF
            v = ((v << 3) | (v >> 5)) & 0xFF
            v = (v + m) & 0xFF
            v = ((v << 5) | (v >> 3)) & 0xFF
            v = (v + (i & 0xFF)) & 0xFF
            
            result[i] = v
        
        return bytes(result)
    
    def _mero_untransform(self, data, key):
        result = bytearray(len(data))
        klen = len(key)
        mlen = len(self._magic)
        
        for i, b in enumerate(data):
            k = key[i % klen]
            m = self._magic[i % mlen]
            
            v = b
            v = (v - (i & 0xFF)) & 0xFF
            v = ((v >> 5) | (v << 3)) & 0xFF
            v = (v - m) & 0xFF
            v = ((v >> 3) | (v << 5)) & 0xFF
            v = (v - k) & 0xFF
            
            result[i] = v
        
        return bytes(result)
    
    def _void_cipher(self, data, seed):
        n = len(data)
        result = bytearray(data)
        
        st = seed
        for i in range(n):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            mix = (st >> 32) & 0xFF
            result[i] = (result[i] + mix) & 0xFF
        
        return bytes(result)
    
    def _void_decipher(self, data, seed):
        n = len(data)
        result = bytearray(data)
        
        st = seed
        for i in range(n):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            mix = (st >> 32) & 0xFF
            result[i] = (result[i] - mix) & 0xFF
        
        return bytes(result)
    
    def _qp4rm_cipher(self, data, seed):
        n = len(data)
        result = bytearray(data)
        
        table = list(range(256))
        st = seed
        for i in range(255, 0, -1):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            j = st % (i + 1)
            table[i], table[j] = table[j], table[i]
        
        for i in range(n):
            result[i] = table[result[i]]
        
        return bytes(result)
    
    def _qp4rm_decipher(self, data, seed):
        n = len(data)
        result = bytearray(data)
        
        table = list(range(256))
        st = seed
        for i in range(255, 0, -1):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            j = st % (i + 1)
            table[i], table[j] = table[j], table[i]
        
        inv_table = [0] * 256
        for i, t in enumerate(table):
            inv_table[t] = i
        
        for i in range(n):
            result[i] = inv_table[result[i]]
        
        return bytes(result)
    
    def _perm(self, data, seed, rev=False):
        n = len(data)
        if n < 2:
            return data
        
        data = bytearray(data)
        perm = list(range(n))
        st = seed
        for i in range(n - 1, 0, -1):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            j = st % (i + 1)
            perm[i], perm[j] = perm[j], perm[i]
        
        if rev:
            inv = [0] * n
            for i, p in enumerate(perm):
                inv[p] = i
            perm = inv
        
        result = bytearray(n)
        for i, p in enumerate(perm):
            result[i] = data[p]
        
        return bytes(result)
    
    def _sbox(self, data, seed, rev=False):
        sbox = list(range(256))
        st = seed
        for i in range(255, 0, -1):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            j = st % (i + 1)
            sbox[i], sbox[j] = sbox[j], sbox[i]
        
        if rev:
            inv = [0] * 256
            for i, s in enumerate(sbox):
                inv[s] = i
            sbox = inv
        
        return bytes(sbox[b] for b in data)
    
    def _rot(self, data, seed, rev=False):
        result = bytearray(len(data))
        for i, b in enumerate(data):
            r = ((seed + i) & 0x7)
            if rev:
                r = 8 - r if r > 0 else 0
            result[i] = ((b << r) | (b >> (8 - r))) & 0xFF
        return bytes(result)
    
    def _mero_block_cipher(self, data, seed):
        n = len(data)
        result = bytearray(data)
        
        st = seed
        for i in range(0, n - 7, 8):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            
            for j in range(8):
                shift = ((st >> (j * 8)) & 0x7)
                result[i + j] = ((result[i + j] << shift) | (result[i + j] >> (8 - shift))) & 0xFF
                result[i + j] = (result[i + j] + ((st >> (j * 4)) & 0xFF)) & 0xFF
        
        return bytes(result)
    
    def _mero_block_decipher(self, data, seed):
        n = len(data)
        result = bytearray(data)
        
        states = []
        st = seed
        for i in range(0, n - 7, 8):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            states.append((i, st))
        
        for i, st in reversed(states):
            for j in range(7, -1, -1):
                shift = ((st >> (j * 8)) & 0x7)
                result[i + j] = (result[i + j] - ((st >> (j * 4)) & 0xFF)) & 0xFF
                unshift = 8 - shift if shift > 0 else 0
                result[i + j] = ((result[i + j] << unshift) | (result[i + j] >> (8 - unshift))) & 0xFF
        
        return bytes(result)
    
    def _mero_diffuse(self, data, seed):
        n = len(data)
        if n < 2:
            return data
        
        result = bytearray(data)
        
        st = seed
        for i in range(n):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            add_val = (st >> 24) & 0xFF
            result[i] = (result[i] + add_val) & 0xFF
        
        return bytes(result)
    
    def _mero_undiffuse(self, data, seed):
        n = len(data)
        if n < 2:
            return data
        
        result = bytearray(data)
        
        st = seed
        for i in range(n):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            add_val = (st >> 24) & 0xFF
            result[i] = (result[i] - add_val) & 0xFF
        
        return bytes(result)
    
    def _pad(self, data, seed):
        pad_len = (16 - (len(data) % 16)) % 16
        if pad_len == 0:
            pad_len = 16
        pad = bytes([(seed >> (i * 8)) & 0xFF for i in range(pad_len)])
        return data + pad + bytes([pad_len])
    
    def _unpad(self, data):
        if len(data) < 1:
            return data
        pad_len = data[-1]
        if pad_len > len(data) - 1:
            return data
        return data[:-pad_len-1]
    
    def encrypt_layer(self, data, seed):
        data = self._pad(data, seed)
        key = self._kdf(seed, max(len(data), 256))
        
        for r in range(self._rnd):
            rseed = (seed + r * 0xDEAD + 0x4D45524F) & 0xFFFFFFFFFFFFFFFF
            
            data = self._mero_transform(data, key)
            data = self._sbox(data, rseed)
            data = self._perm(data, rseed)
            data = self._rot(data, rseed)
            data = self._void_cipher(data, rseed)
            data = self._qp4rm_cipher(data, rseed)
            data = self._mero_block_cipher(data, rseed)
            data = self._mero_diffuse(data, rseed)
            
            key = self._kdf(rseed, max(len(data), 256))
        
        data = self._mero_transform(data, key)
        return data
    
    def decrypt_layer(self, data, seed):
        all_keys = []
        key = self._kdf(seed, max(len(data), 256))
        
        for r in range(self._rnd):
            rseed = (seed + r * 0xDEAD + 0x4D45524F) & 0xFFFFFFFFFFFFFFFF
            all_keys.append((key, rseed))
            key = self._kdf(rseed, max(len(data), 256))
        
        data = self._mero_untransform(data, key)
        
        for r in range(self._rnd - 1, -1, -1):
            key, rseed = all_keys[r]
            
            data = self._mero_undiffuse(data, rseed)
            data = self._mero_block_decipher(data, rseed)
            data = self._qp4rm_decipher(data, rseed)
            data = self._void_decipher(data, rseed)
            data = self._rot(data, rseed, rev=True)
            data = self._perm(data, rseed, rev=True)
            data = self._sbox(data, rseed, rev=True)
            data = self._mero_untransform(data, key)
        
        data = self._unpad(data)
        return data
