import ast
import random
import string

class VoidParser:
    def __init__(self):
        self._id = 0
        self._vars = {}
        self._funcs = {}
    
    def _nid(self):
        self._id += 1
        return f"S{self._id:04X}"
    
    def _vid(self, name):
        if name not in self._vars:
            self._vars[name] = f"V{len(self._vars):03X}"
        return self._vars[name]
    
    def _fid(self, name):
        if name not in self._funcs:
            self._funcs[name] = f"F{len(self._funcs):03X}"
        return self._funcs[name]
    
    def parse(self, code):
        self._id = 0
        self._vars = {}
        self._funcs = {}
        tree = ast.parse(code)
        states = self._parse_body(tree.body)
        return self._link_states(states)
    
    def _parse_body(self, body):
        states = []
        for node in body:
            s = self._node_to_state(node)
            if s:
                if isinstance(s, list):
                    states.extend(s)
                else:
                    states.append(s)
        return states
    
    def _node_to_state(self, node):
        if isinstance(node, ast.Assign):
            return self._parse_assign(node)
        elif isinstance(node, ast.AugAssign):
            return self._parse_aug_assign(node)
        elif isinstance(node, ast.Expr):
            return self._parse_expr(node)
        elif isinstance(node, ast.If):
            return self._parse_if(node)
        elif isinstance(node, ast.While):
            return self._parse_while(node)
        elif isinstance(node, ast.For):
            return self._parse_for(node)
        elif isinstance(node, ast.FunctionDef):
            return self._parse_func(node)
        elif isinstance(node, ast.Return):
            return self._parse_return(node)
        elif isinstance(node, ast.Import):
            return self._parse_import(node)
        elif isinstance(node, ast.ImportFrom):
            return self._parse_import_from(node)
        elif isinstance(node, ast.Try):
            return self._parse_try(node)
        elif isinstance(node, ast.With):
            return self._parse_with(node)
        elif isinstance(node, ast.ClassDef):
            return self._parse_class(node)
        return None
    
    def _parse_assign(self, node):
        sid = self._nid()
        targets = []
        for t in node.targets:
            if isinstance(t, ast.Name):
                targets.append(self._vid(t.id))
            elif isinstance(t, ast.Tuple):
                for e in t.elts:
                    if isinstance(e, ast.Name):
                        targets.append(self._vid(e.id))
        val = self._val_to_rep(node.value)
        return {'id': sid, 'op': 'DEF', 't': targets, 'v': val, 'r': True}
    
    def _parse_aug_assign(self, node):
        sid = self._nid()
        if isinstance(node.target, ast.Name):
            t = self._vid(node.target.id)
        else:
            t = 'MERO_UNK'
        op = self._op_to_rep(node.op)
        val = self._val_to_rep(node.value)
        return {'id': sid, 'op': 'AUG', 't': t, 'ao': op, 'v': val, 'r': True}
    
    def _parse_expr(self, node):
        if isinstance(node.value, ast.Call):
            return self._parse_call(node.value)
        return None
    
    def _parse_call(self, node):
        sid = self._nid()
        if isinstance(node.func, ast.Name):
            fn = node.func.id
            if fn == 'print':
                args = [self._val_to_rep(a) for a in node.args]
                return {'id': sid, 'op': 'EFF', 'ef': 'PRINT', 'a': args, 'r': True}
            elif fn == 'input':
                args = [self._val_to_rep(a) for a in node.args]
                return {'id': sid, 'op': 'EFF', 'ef': 'INPUT', 'a': args, 'r': True}
            elif fn == 'open':
                args = [self._val_to_rep(a) for a in node.args]
                return {'id': sid, 'op': 'EFF', 'ef': 'IO_OPEN', 'a': args, 'r': True}
            elif fn == 'len':
                args = [self._val_to_rep(a) for a in node.args]
                return {'id': sid, 'op': 'EFF', 'ef': 'LEN', 'a': args, 'r': True}
            elif fn == 'range':
                args = [self._val_to_rep(a) for a in node.args]
                return {'id': sid, 'op': 'EFF', 'ef': 'RANGE', 'a': args, 'r': True}
            else:
                args = [self._val_to_rep(a) for a in node.args]
                return {'id': sid, 'op': 'CALL', 'fn': self._fid(fn), 'a': args, 'r': True}
        elif isinstance(node.func, ast.Attribute):
            obj = self._val_to_rep(node.func.value)
            meth = node.func.attr
            args = [self._val_to_rep(a) for a in node.args]
            return {'id': sid, 'op': 'MCALL', 'o': obj, 'm': meth, 'a': args, 'r': True}
        return None
    
    def _parse_if(self, node):
        states = []
        sid = self._nid()
        cond = self._cond_to_rep(node.test)
        
        tb_states = self._parse_body(node.body)
        fb_states = self._parse_body(node.orelse) if node.orelse else []
        
        for s in tb_states:
            s['_body'] = True
        for s in fb_states:
            s['_body'] = True
        
        tb_ids = [s['id'] for s in tb_states]
        fb_ids = [s['id'] for s in fb_states]
        
        states.append({'id': sid, 'op': 'COND', 'c': cond, 'tb': tb_ids, 'fb': fb_ids, 'r': True})
        states.extend(tb_states)
        states.extend(fb_states)
        return states
    
    def _parse_while(self, node):
        states = []
        sid = self._nid()
        cond = self._cond_to_rep(node.test)
        
        body_states = self._parse_body(node.body)
        for s in body_states:
            s['_body'] = True
        body_ids = [s['id'] for s in body_states]
        
        states.append({'id': sid, 'op': 'LOOP', 'lt': 'WHILE', 'c': cond, 'bd': body_ids, 'r': True})
        states.extend(body_states)
        return states
    
    def _parse_for(self, node):
        states = []
        sid = self._nid()
        if isinstance(node.target, ast.Name):
            it = self._vid(node.target.id)
        else:
            it = 'MERO_UNK'
        seq = self._val_to_rep(node.iter)
        
        body_states = self._parse_body(node.body)
        for s in body_states:
            s['_body'] = True
        body_ids = [s['id'] for s in body_states]
        
        states.append({'id': sid, 'op': 'LOOP', 'lt': 'FOR', 'it': it, 'sq': seq, 'bd': body_ids, 'r': True})
        states.extend(body_states)
        return states
    
    def _parse_func(self, node):
        states = []
        sid = self._nid()
        fid = self._fid(node.name)
        args = []
        for a in node.args.args:
            args.append(self._vid(a.arg))
        
        body_states = self._parse_body(node.body)
        for s in body_states:
            s['_body'] = True
        body_ids = [s['id'] for s in body_states]
        
        states.append({'id': sid, 'op': 'FDEF', 'fn': fid, 'ar': args, 'bd': body_ids, 'r': True})
        states.extend(body_states)
        return states
    
    def _parse_return(self, node):
        sid = self._nid()
        val = self._val_to_rep(node.value) if node.value else None
        return {'id': sid, 'op': 'RET', 'v': val, 'r': True}
    
    def _parse_import(self, node):
        sid = self._nid()
        mods = [a.name for a in node.names]
        return {'id': sid, 'op': 'IMP', 'md': mods, 'r': True}
    
    def _parse_import_from(self, node):
        sid = self._nid()
        mod = node.module
        names = [a.name for a in node.names]
        return {'id': sid, 'op': 'IMPF', 'md': mod, 'nm': names, 'r': True}
    
    def _parse_try(self, node):
        sid = self._nid()
        return {'id': sid, 'op': 'TRY', 'r': True}
    
    def _parse_with(self, node):
        sid = self._nid()
        return {'id': sid, 'op': 'WITH', 'r': True}
    
    def _parse_class(self, node):
        sid = self._nid()
        cid = self._fid(node.name)
        return {'id': sid, 'op': 'CDEF', 'cn': cid, 'r': True}
    
    def _val_to_rep(self, node):
        if node is None:
            return {'t': 'NONE'}
        if isinstance(node, ast.Constant):
            return {'t': 'CONST', 'v': node.value}
        elif isinstance(node, ast.Num):
            return {'t': 'CONST', 'v': node.n}
        elif isinstance(node, ast.Str):
            return {'t': 'CONST', 'v': node.s}
        elif isinstance(node, ast.Name):
            return {'t': 'VAR', 'v': self._vid(node.id)}
        elif isinstance(node, ast.BinOp):
            return {'t': 'BIN', 'l': self._val_to_rep(node.left), 
                    'op': self._op_to_rep(node.op), 'ri': self._val_to_rep(node.right)}
        elif isinstance(node, ast.UnaryOp):
            return {'t': 'UNA', 'op': self._uop_to_rep(node.op), 'v': self._val_to_rep(node.operand)}
        elif isinstance(node, ast.List):
            return {'t': 'LST', 'e': [self._val_to_rep(e) for e in node.elts]}
        elif isinstance(node, ast.Dict):
            return {'t': 'DCT', 'k': [self._val_to_rep(k) for k in node.keys],
                    'v': [self._val_to_rep(v) for v in node.values]}
        elif isinstance(node, ast.Tuple):
            return {'t': 'TPL', 'e': [self._val_to_rep(e) for e in node.elts]}
        elif isinstance(node, ast.Call):
            return self._call_to_rep(node)
        elif isinstance(node, ast.Subscript):
            return {'t': 'SUB', 'v': self._val_to_rep(node.value), 
                    's': self._val_to_rep(node.slice) if hasattr(node, 'slice') else None}
        elif isinstance(node, ast.Attribute):
            return {'t': 'ATTR', 'v': self._val_to_rep(node.value), 'a': node.attr}
        elif isinstance(node, ast.Compare):
            return self._cond_to_rep(node)
        elif isinstance(node, ast.IfExp):
            return {'t': 'IFEX', 'c': self._cond_to_rep(node.test),
                    'b': self._val_to_rep(node.body), 'o': self._val_to_rep(node.orelse)}
        elif isinstance(node, ast.Lambda):
            args = [self._vid(a.arg) for a in node.args.args]
            return {'t': 'LAM', 'ar': args, 'bd': self._val_to_rep(node.body)}
        elif isinstance(node, ast.ListComp):
            return {'t': 'LCOM', 'e': self._val_to_rep(node.elt)}
        elif isinstance(node, ast.Index):
            return self._val_to_rep(node.value)
        return {'t': 'UNK'}
    
    def _call_to_rep(self, node):
        if isinstance(node.func, ast.Name):
            fn = node.func.id
            args = [self._val_to_rep(a) for a in node.args]
            if fn in ['print', 'input', 'open', 'len', 'range', 'int', 'str', 'float', 'list', 'dict', 'tuple', 'set', 'bool']:
                return {'t': 'BCALL', 'fn': fn, 'a': args}
            return {'t': 'FCALL', 'fn': self._fid(fn), 'a': args}
        elif isinstance(node.func, ast.Attribute):
            return {'t': 'MCALL', 'o': self._val_to_rep(node.func.value),
                    'm': node.func.attr, 'a': [self._val_to_rep(a) for a in node.args]}
        return {'t': 'UNK'}
    
    def _cond_to_rep(self, node):
        if isinstance(node, ast.Compare):
            left = self._val_to_rep(node.left)
            ops = [self._cop_to_rep(o) for o in node.ops]
            comps = [self._val_to_rep(c) for c in node.comparators]
            return {'t': 'CMP', 'l': left, 'ops': ops, 'cs': comps}
        elif isinstance(node, ast.BoolOp):
            op = 'AND' if isinstance(node.op, ast.And) else 'OR'
            vals = [self._cond_to_rep(v) for v in node.values]
            return {'t': 'BOOL', 'op': op, 'vs': vals}
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return {'t': 'NOT', 'v': self._cond_to_rep(node.operand)}
        return self._val_to_rep(node)
    
    def _op_to_rep(self, op):
        ops = {ast.Add: 'ADD', ast.Sub: 'SUB', ast.Mult: 'MUL', ast.Div: 'DIV',
               ast.FloorDiv: 'FDIV', ast.Mod: 'MOD', ast.Pow: 'POW',
               ast.LShift: 'LSH', ast.RShift: 'RSH', ast.BitOr: 'BOR',
               ast.BitXor: 'XOR', ast.BitAnd: 'BAND', ast.MatMult: 'MMUL'}
        return ops.get(type(op), 'UNK')
    
    def _uop_to_rep(self, op):
        ops = {ast.UAdd: 'POS', ast.USub: 'NEG', ast.Not: 'NOT', ast.Invert: 'INV'}
        return ops.get(type(op), 'UNK')
    
    def _cop_to_rep(self, op):
        ops = {ast.Eq: 'EQ', ast.NotEq: 'NE', ast.Lt: 'LT', ast.LtE: 'LE',
               ast.Gt: 'GT', ast.GtE: 'GE', ast.Is: 'IS', ast.IsNot: 'ISN',
               ast.In: 'IN', ast.NotIn: 'NIN'}
        return ops.get(type(op), 'UNK')
    
    def _link_states(self, states):
        for i, s in enumerate(states):
            if i < len(states) - 1:
                s['nx'] = states[i + 1]['id']
            else:
                s['nx'] = None
        return states
