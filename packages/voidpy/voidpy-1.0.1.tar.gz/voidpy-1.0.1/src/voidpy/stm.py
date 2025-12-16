import random
import json
import struct
import hashlib
import zlib

class StateManager:
    def __init__(self):
        self._fr = 0.75
        self._pk = [
            "MERO_FUK", "MERO_NIL", "MERO_DEAD", "MERO_VOID", "MERO_NULL",
            "MERO_FAKE", "MERO_TRAP", "MERO_JUNK", "MERO_SKIP", "MERO_NOOP",
            "QP4RM_X", "QP4RM_Y", "QP4RM_Z", "VOID_ERR", "VOID_END"
        ]
    
    def add_fake_states(self, states):
        rc = len(states)
        fc = int(rc * self._fr / (1 - self._fr))
        fc = max(fc, rc * 3)
        
        fakes = []
        for i in range(fc):
            fakes.append(self._gf(i))
        
        return states + fakes
    
    def _gf(self, idx):
        ops = ['DEF', 'AUG', 'EFF', 'COND', 'LOOP', 'CALL']
        op = random.choice(ops)
        sid = f"X{idx:04X}"
        
        f = {'id': sid, 'op': op, 'r': False}
        
        if op == 'DEF':
            f['t'] = [f"MV{random.randint(0, 999):03X}"]
            f['v'] = self._fv()
        elif op == 'AUG':
            f['t'] = f"MV{random.randint(0, 999):03X}"
            f['ao'] = random.choice(['ADD', 'SUB', 'MUL'])
            f['v'] = self._fv()
        elif op == 'EFF':
            f['ef'] = random.choice(self._pk)
            f['a'] = [self._fv()]
        elif op == 'COND':
            f['c'] = {'t': 'CMP', 'l': self._fv(), 'ops': ['EQ'], 'cs': [self._fv()]}
            f['tb'] = []
            f['fb'] = []
        elif op == 'LOOP':
            f['lt'] = random.choice(['WHILE', 'FOR'])
            f['c'] = {'t': 'CONST', 'v': False}
        elif op == 'CALL':
            f['fn'] = random.choice(self._pk)
            f['a'] = []
        
        f['nx'] = None
        return f
    
    def _fv(self):
        t = random.choice(['CONST', 'VAR', 'BIN'])
        if t == 'CONST':
            v = random.choice([
                random.randint(-9999, 9999),
                random.choice(self._pk),
                random.random(),
                None,
                True,
                False
            ])
            return {'t': 'CONST', 'v': v}
        elif t == 'VAR':
            return {'t': 'VAR', 'v': f"MV{random.randint(0, 999):03X}"}
        else:
            return {'t': 'BIN', 'l': {'t': 'CONST', 'v': random.randint(0, 100)},
                    'op': random.choice(['ADD', 'SUB', 'MUL']),
                    'ri': {'t': 'CONST', 'v': random.randint(0, 100)}}
    
    def fragment_logic(self, states):
        fg = []
        for s in states:
            if s.get('r') and s.get('op') == 'DEF':
                fg.extend(self._fd(s))
            else:
                fg.append(s)
        return fg
    
    def _fd(self, state):
        frags = []
        sid = state['id']
        val = state.get('v', {})
        
        if val.get('t') == 'BIN':
            f1 = f"{sid}_L"
            f2 = f"{sid}_R"
            f3 = f"{sid}_C"
            
            frags.append({'id': f1, 'op': 'FRAG', 'ft': 'LEFT', 'v': val.get('l'), 
                         'r': True, 'ps': sid, 'nx': f2})
            frags.append({'id': f2, 'op': 'FRAG', 'ft': 'RIGHT', 'v': val.get('ri'),
                         'r': True, 'ps': sid, 'nx': f3})
            frags.append({'id': f3, 'op': 'FRAG', 'ft': 'COMBINE', 'ao': val.get('op'),
                         'ls': f1, 'rs': f2, 'r': True, 'ps': sid, 'nx': state.get('nx')})
            
            state['fs'] = [f1, f2, f3]
            frags.append(state)
        else:
            frags.append(state)
        
        return frags
    
    def shuffle_states(self, states, seed):
        for i, s in enumerate(states):
            s['_ord'] = i
        
        random.seed(seed)
        order = list(range(len(states)))
        random.shuffle(order)
        
        shuffled = [None] * len(states)
        for new_idx, old_idx in enumerate(order):
            shuffled[new_idx] = states[old_idx]
        
        return shuffled
    
    def unshuffle_states(self, states, seed):
        random.seed(seed)
        n = len(states)
        order = list(range(n))
        random.shuffle(order)
        
        unshuffled = [None] * n
        for i, s in enumerate(states):
            orig_pos = order[i]
            unshuffled[orig_pos] = s
        
        return unshuffled
    
    def filter_real_states(self, states):
        return [s for s in states if s.get('r', False)]
    
    def serialize(self, states):
        data = json.dumps(states, separators=(',', ':'), ensure_ascii=False)
        compressed = zlib.compress(data.encode('utf-8'), 9)
        return compressed
    
    def deserialize(self, data):
        decompressed = zlib.decompress(data)
        return json.loads(decompressed.decode('utf-8'))
