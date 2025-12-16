import sys

class VoidVM:
    def __init__(self):
        self._mem = {}
        self._fn = {}
        self._mod = {}
        self._out = []
        self._ret = None
        self._MERO_NIL = "MERO_NIL_VALUE"
        self._MERO_ERR = "MERO_EXECUTION_BLOCKED"
    
    def execute(self, states):
        self._mem = {}
        self._fn = {}
        self._mod = {}
        self._out = []
        self._ret = None
        
        sorted_states = sorted(states, key=lambda s: s.get('_ord', 0))
        
        for s in sorted_states:
            if s.get('op') == 'FDEF':
                self._fn[s.get('fn')] = s
        
        for s in sorted_states:
            if s.get('op') != 'FDEF' and not s.get('_body', False):
                self._run(s, sorted_states)
        
        return self._ret
    
    def _run(self, state, all_states):
        if not state.get('r', False):
            return
        
        op = state.get('op')
        
        if op == 'DEF':
            self._op_def(state)
        elif op == 'AUG':
            self._op_aug(state)
        elif op == 'EFF':
            self._op_eff(state)
        elif op == 'COND':
            self._op_cond(state, all_states)
        elif op == 'LOOP':
            self._op_loop(state, all_states)
        elif op == 'CALL':
            self._op_call(state)
        elif op == 'MCALL':
            self._op_mcall(state)
        elif op == 'RET':
            self._op_ret(state)
        elif op == 'IMP':
            self._op_imp(state)
        elif op == 'IMPF':
            self._op_impf(state)
        elif op == 'FRAG':
            self._op_frag(state)
    
    def _op_def(self, state):
        t = state.get('t', [])
        v = self._val(state.get('v'))
        if len(t) == 1:
            self._mem[t[0]] = v
        elif len(t) > 1 and hasattr(v, '__iter__') and not isinstance(v, (str, bytes)):
            vl = list(v)
            for i, k in enumerate(t):
                self._mem[k] = vl[i] if i < len(vl) else None
    
    def _op_aug(self, state):
        t = state.get('t')
        ao = state.get('ao')
        v = self._val(state.get('v'))
        c = self._mem.get(t, 0)
        self._mem[t] = self._math(c, v, ao)
    
    def _op_eff(self, state):
        ef = state.get('ef')
        a = [self._val(x) for x in state.get('a', [])]
        
        if ef == 'PRINT':
            o = ' '.join(str(x) for x in a)
            print(o)
            self._out.append(o)
        elif ef == 'INPUT':
            p = a[0] if a else ''
            self._ret = input(p)
        elif ef == 'IO_OPEN':
            if len(a) >= 1:
                m = a[1] if len(a) > 1 else 'r'
                self._ret = open(a[0], m)
        elif ef == 'LEN':
            self._ret = len(a[0]) if a else 0
        elif ef == 'RANGE':
            if len(a) == 1:
                self._ret = range(a[0])
            elif len(a) == 2:
                self._ret = range(a[0], a[1])
            elif len(a) >= 3:
                self._ret = range(a[0], a[1], a[2])
    
    def _op_cond(self, state, all_states):
        c = self._cond(state.get('c'))
        ids = state.get('tb', []) if c else state.get('fb', [])
        for sid in ids:
            s = self._find(sid, all_states)
            if s:
                self._run(s, all_states)
    
    def _op_loop(self, state, all_states):
        lt = state.get('lt')
        bids = state.get('bd', [])
        
        if lt == 'WHILE':
            mx = 10000
            ct = 0
            while self._cond(state.get('c')) and ct < mx:
                for sid in bids:
                    s = self._find(sid, all_states)
                    if s:
                        self._run(s, all_states)
                ct += 1
        elif lt == 'FOR':
            it = state.get('it')
            sq = self._val(state.get('sq'))
            if sq:
                for item in sq:
                    self._mem[it] = item
                    for sid in bids:
                        s = self._find(sid, all_states)
                        if s:
                            self._run(s, all_states)
    
    def _op_call(self, state):
        fn = state.get('fn')
        a = [self._val(x) for x in state.get('a', [])]
        if fn in self._fn:
            self._ret = self._fn[fn](*a)
    
    def _op_mcall(self, state):
        o = self._val(state.get('o'))
        m = state.get('m')
        a = [self._val(x) for x in state.get('a', [])]
        if hasattr(o, m):
            self._ret = getattr(o, m)(*a)
    
    def _op_ret(self, state):
        self._ret = self._val(state.get('v'))
    
    def _op_imp(self, state):
        for md in state.get('md', []):
            try:
                self._mod[md] = __import__(md)
            except:
                pass
    
    def _op_impf(self, state):
        md = state.get('md')
        nm = state.get('nm', [])
        try:
            m = __import__(md, fromlist=nm)
            for n in nm:
                if hasattr(m, n):
                    self._mod[n] = getattr(m, n)
        except:
            pass
    
    def _op_frag(self, state):
        ft = state.get('ft')
        fid = f"_f_{state['id']}"
        
        if ft == 'LEFT':
            self._mem[fid] = self._val(state.get('v'))
        elif ft == 'RIGHT':
            self._mem[fid] = self._val(state.get('v'))
        elif ft == 'COMBINE':
            ls = f"_f_{state.get('ls')}"
            rs = f"_f_{state.get('rs')}"
            ao = state.get('ao')
            lv = self._mem.get(ls, 0)
            rv = self._mem.get(rs, 0)
            self._mem[fid] = self._math(lv, rv, ao)
    
    def _math(self, l, r, op):
        if l is None:
            l = 0
        if r is None:
            r = 0
        try:
            if op == 'ADD':
                return l + r
            elif op == 'SUB':
                return l - r
            elif op == 'MUL':
                return l * r
            elif op == 'DIV':
                return l / r if r != 0 else 0
            elif op == 'FDIV':
                return l // r if r != 0 else 0
            elif op == 'MOD':
                return l % r if r != 0 else 0
            elif op == 'POW':
                return l ** r
        except:
            return 0
        return 0
    
    def _val(self, v):
        if v is None:
            return None
        
        t = v.get('t')
        
        if t == 'NONE':
            return None
        elif t == 'CONST':
            return v.get('v')
        elif t == 'VAR':
            return self._mem.get(v.get('v'))
        elif t == 'BIN':
            return self._math(self._val(v.get('l')), self._val(v.get('ri')), v.get('op'))
        elif t == 'UNA':
            vv = self._val(v.get('v'))
            op = v.get('op')
            if op == 'NEG':
                return -vv if vv is not None else 0
            elif op == 'POS':
                return +vv if vv is not None else 0
            elif op == 'NOT':
                return not vv
            elif op == 'INV':
                return ~vv if vv is not None else 0
            return vv
        elif t == 'LST':
            return [self._val(e) for e in v.get('e', [])]
        elif t == 'DCT':
            ks = [self._val(k) for k in v.get('k', [])]
            vs = [self._val(x) for x in v.get('v', [])]
            return dict(zip(ks, vs))
        elif t == 'TPL':
            return tuple(self._val(e) for e in v.get('e', []))
        elif t == 'BCALL':
            fn = v.get('fn')
            a = [self._val(x) for x in v.get('a', [])]
            bi = {'int': int, 'str': str, 'float': float, 'list': list,
                  'dict': dict, 'tuple': tuple, 'set': set, 'bool': bool,
                  'len': len, 'range': range, 'print': print, 'input': input,
                  'abs': abs, 'min': min, 'max': max, 'sum': sum, 'sorted': sorted,
                  'reversed': reversed, 'enumerate': enumerate, 'zip': zip,
                  'map': map, 'filter': filter, 'type': type, 'isinstance': isinstance,
                  'hasattr': hasattr, 'getattr': getattr, 'setattr': setattr,
                  'round': round, 'hex': hex, 'bin': bin, 'oct': oct, 'ord': ord, 'chr': chr}
            if fn in bi:
                try:
                    return bi[fn](*a)
                except:
                    return None
        elif t == 'FCALL':
            fn = v.get('fn')
            a = [self._val(x) for x in v.get('a', [])]
            if fn in self._fn:
                return self._fn[fn](*a)
        elif t == 'MCALL':
            o = self._val(v.get('o'))
            m = v.get('m')
            a = [self._val(x) for x in v.get('a', [])]
            if o is not None and hasattr(o, m):
                try:
                    return getattr(o, m)(*a)
                except:
                    return None
        elif t == 'SUB':
            vv = self._val(v.get('v'))
            s = self._val(v.get('s'))
            if vv is not None and s is not None:
                try:
                    return vv[s]
                except:
                    return None
        elif t == 'ATTR':
            vv = self._val(v.get('v'))
            a = v.get('a')
            if vv is not None and hasattr(vv, a):
                return getattr(vv, a)
        elif t == 'CMP':
            return self._cond(v)
        elif t == 'IFEX':
            c = self._cond(v.get('c'))
            return self._val(v.get('b') if c else v.get('o'))
        elif t == 'LAM':
            ar = v.get('ar', [])
            bd = v.get('bd')
            def lf(*args):
                old = self._mem.copy()
                for i, k in enumerate(ar):
                    self._mem[k] = args[i] if i < len(args) else None
                r = self._val(bd)
                self._mem = old
                return r
            return lf
        
        return None
    
    def _cond(self, c):
        if c is None:
            return False
        
        t = c.get('t')
        
        if t == 'CMP':
            l = self._val(c.get('l'))
            ops = c.get('ops', [])
            cs = [self._val(x) for x in c.get('cs', [])]
            r = True
            cur = l
            for i, op in enumerate(ops):
                cp = cs[i] if i < len(cs) else None
                if not self._cmp(cur, cp, op):
                    r = False
                    break
                cur = cp
            return r
        elif t == 'BOOL':
            op = c.get('op')
            vs = [self._cond(x) for x in c.get('vs', [])]
            return all(vs) if op == 'AND' else any(vs)
        elif t == 'NOT':
            return not self._cond(c.get('v'))
        
        return bool(self._val(c))
    
    def _cmp(self, a, b, op):
        try:
            if op == 'EQ':
                return a == b
            elif op == 'NE':
                return a != b
            elif op == 'LT':
                return a < b
            elif op == 'LE':
                return a <= b
            elif op == 'GT':
                return a > b
            elif op == 'GE':
                return a >= b
            elif op == 'IS':
                return a is b
            elif op == 'ISN':
                return a is not b
            elif op == 'IN':
                return a in b
            elif op == 'NIN':
                return a not in b
        except:
            return False
        return False
    
    def _find(self, sid, states):
        for s in states:
            if s.get('id') == sid:
                return s
        return None
