import sys
import os
import webbrowser

def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help', 'help', 'h']:
        _help()
        return
    
    cmd = args[0]
    
    if cmd in ['encrypt', 'enc', 'e', 'protect', 'p', 'lock', 'l']:
        _encrypt(args[1:])
    elif cmd in ['run', 'r', 'exec', 'x', 'go', 'g']:
        _run(args[1:])
    elif cmd in ['inline', 'i', 'test', 't', 'quick', 'q']:
        _inline(args[1:])
    elif cmd in ['version', 'v', '-v', '--version', 'ver']:
        _version()
    elif cmd in ['on', 'dev', 'developer', 'contact', 'tg', 'telegram', 'mero']:
        _developer()
    elif cmd in ['info', 'about', 'a']:
        _info()
    elif cmd in ['check', 'c', 'verify']:
        _check(args[1:])
    elif cmd in ['batch', 'b', 'all']:
        _batch(args[1:])
    else:
        print(f"Unknown command: {cmd}")
        _help()

def _help():
    print("voidpy - Void Execution Engine")
    print("Developer: MERO | Telegram: @QP4RM")
    print()
    print("Commands:")
    print("  encrypt, e, p, l   Encrypt Python file")
    print("  run, r, x, g       Run encrypted .void file")
    print("  inline, i, t, q    Encrypt and run inline code")
    print("  check, c           Verify .void file integrity")
    print("  batch, b           Encrypt multiple files")
    print("  version, v         Show version")
    print("  on, dev, tg        Open developer contact")
    print("  info, about, a     Show detailed info")
    print("  help, h            Show this help")
    print()
    print("Encrypt Options:")
    print("  -o FILE       Output file path")
    print("  -l N          Encryption layers (1-10, default: 3)")
    print()
    print("Examples:")
    print("  voidpy e script.py")
    print("  voidpy e script.py -o out.void")
    print("  voidpy e script.py -o out.void -l 5")
    print("  voidpy r out.void")
    print("  voidpy i \"print('Hello')\"")
    print("  voidpy on")

def _encrypt(args):
    if not args:
        print("Error: No input file")
        return
    
    source = args[0]
    output = None
    layers = 3
    
    i = 1
    while i < len(args):
        if args[i] in ['-o', '--output']:
            if i + 1 < len(args):
                output = args[i + 1]
                i += 2
            else:
                i += 1
        elif args[i] in ['-l', '--layers']:
            if i + 1 < len(args):
                try:
                    layers = int(args[i + 1])
                except:
                    pass
                i += 2
            else:
                i += 1
        else:
            if output is None:
                output = args[i]
            i += 1
    
    if output is None:
        output = source.replace('.py', '.void')
    
    from .cor import VoidEngine
    engine = VoidEngine()
    engine.encrypt(source, output, layers)
    print(f"Encrypted: {source} -> {output}")
    print(f"Layers: {layers}")

def _run(args):
    if not args:
        print("Error: No .void file")
        return
    
    void_file = args[0]
    
    from .cor import VoidEngine
    engine = VoidEngine()
    engine.run(void_file)

def _inline(args):
    if not args:
        print("Error: No code")
        return
    
    code = ' '.join(args)
    
    from .cor import VoidEngine
    engine = VoidEngine()
    data = engine.encrypt_inline(code)
    engine.run_inline(data)

def _version():
    print("voidpy 1.0.0")
    print("Developer: MERO")
    print("Telegram: @QP4RM")

def _developer():
    print("=" * 40)
    print("  Developer: MERO")
    print("  Telegram: @QP4RM")
    print("  https://t.me/QP4RM")
    print("=" * 40)
    try:
        webbrowser.open("https://t.me/QP4RM")
        print("Opening Telegram...")
    except:
        print("Open: https://t.me/QP4RM")

def _info():
    print("=" * 50)
    print("  voidpy - Void Execution Engine")
    print("  Version: 1.0.0")
    print("=" * 50)
    print()
    print("What is voidpy?")
    print("  - Python code protection system")
    print("  - Translates code to Logic States")
    print("  - NOT traditional obfuscation")
    print("  - No Python code in output")
    print("  - Direct VM execution")
    print()
    print("Security Features:")
    print("  - 75%+ fake states")
    print("  - Multi-layer encryption")
    print("  - Logic fragmentation")
    print("  - S-Box + rotation + XOR")
    print("  - 16 rounds per layer")
    print()
    print("Developer: MERO | Telegram: @QP4RM")
    print("=" * 50)

def _check(args):
    import struct
    import hashlib
    
    if not args:
        print("Error: No .void file to check")
        return
    
    void_file = args[0]
    
    if not os.path.exists(void_file):
        print(f"Error: File not found: {void_file}")
        return
    
    try:
        with open(void_file, 'rb') as f:
            data = f.read()
        
        if len(data) < 19:
            print("INVALID: File too small (need at least 19 bytes)")
            return
        
        magic = data[:4]
        if magic != b'VOID':
            print("INVALID: Not a .void file (wrong magic)")
            return
        
        version = struct.unpack('>H', data[4:6])[0]
        layers = struct.unpack('>B', data[6:7])[0]
        seed = struct.unpack('>Q', data[7:15])[0]
        checksum = data[15:19]
        
        expected_check = hashlib.md5(data[:15]).digest()[:4]
        
        if checksum != expected_check:
            print("INVALID: Checksum mismatch (file corrupted)")
            return
        
        if layers < 1 or layers > 10:
            print(f"WARNING: Unusual layer count: {layers}")
        
        print(f"File: {void_file}")
        print(f"Size: {len(data)} bytes")
        print(f"Magic: VOID")
        print(f"Version: {version}")
        print(f"Layers: {layers}")
        print(f"Checksum: OK")
        print("Status: VALID")
        
    except Exception as e:
        print(f"Error checking file: {e}")

def _batch(args):
    if not args:
        print("Error: No files specified")
        print("Usage: voidpy batch file1.py file2.py file3.py")
        return
    
    layers = 3
    files = []
    
    i = 0
    while i < len(args):
        if args[i] in ['-l', '--layers']:
            if i + 1 < len(args):
                try:
                    layers = int(args[i + 1])
                except:
                    pass
                i += 2
            else:
                i += 1
        else:
            files.append(args[i])
            i += 1
    
    if not files:
        print("Error: No files to encrypt")
        return
    
    from .cor import VoidEngine
    engine = VoidEngine()
    
    print(f"Batch encrypting {len(files)} files with {layers} layers...")
    print()
    
    for source in files:
        if not os.path.exists(source):
            print(f"SKIP: {source} (not found)")
            continue
        
        output = source.replace('.py', '.void')
        try:
            engine.encrypt(source, output, layers)
            print(f"OK: {source} -> {output}")
        except Exception as e:
            print(f"FAIL: {source} ({e})")
    
    print()
    print("Batch complete!")

if __name__ == '__main__':
    main()
