"""
gerar.py - Hubstry Logistics Quantum MVP
Uso: python gerar.py
"""
import os, sys, base64, zlib
CHUNK_FILES = ["mvp_b64_0.txt", "mvp_b64_1.txt"]
EXPECTED_SIZE = 46216
EXPECTED_FILES = 17
def main():
    print("=" * 60)
    print("  Hubstry Logistics Quantum MVP - Gerador de Arquivos")
    print("=" * 60)
    print("\n[1/3] Lendo chunks base64...")
    combined = ""
    for cf in CHUNK_FILES:
        path = os.path.join(os.path.dirname(__file__) or ".", cf)
        if not os.path.exists(path):
            print(f"  ERRO: Arquivo nao encontrado: {cf}")
            sys.exit(1)
        with open(path, "r") as f:
            data = f.read().strip()
        print(f"  {cf}: {len(data)} chars")
        combined += data
    if len(combined) != EXPECTED_SIZE:
        print(f"  ERRO: Tamanho {len(combined)} (esperado {EXPECTED_SIZE})")
        sys.exit(1)
    print("\n[2/3] Decodificando e descomprimindo...")
    try:
        compressed = base64.b64decode(combined)
        packed = zlib.decompress(compressed)
        print(f"  OK: {len(packed)} bytes descomprimidos")
    except Exception as e:
        print(f"  ERRO: {e}")
        sys.exit(1)
    print("\n[3/3] Extraindo arquivos...")
    text = packed.decode("utf-8")
    ms, me = "<<FILE:", "<<ENDFILE>>"
    count, pos = 0, 0
    while pos < len(text):
        si = text.find(ms, pos)
        if si == -1: break
        ep = text.find(">>\n", si)
        if ep == -1: break
        fp = text[si + len(ms):ep]
        ei = text.find(me, ep)
        if ei == -1: break
        ct = text[ep + 3:ei].strip("\n")
        dp = os.path.dirname(fp)
        if dp: os.makedirs(dp, exist_ok=True)
        with open(fp, "w", encoding="utf-8", newline="\n") as f:
            f.write(ct)
        count += 1
        print(f"  + {fp} ({len(ct)} bytes)")
        pos = ei + len(me)
    print(f"\n{'=' * 60}")
    if count == EXPECTED_FILES:
        print(f"  {count}/{EXPECTED_FILES} arquivos gerados! Execute: python run_mvp.py")
    else:
        print(f"  AVISO: {count}/{EXPECTED_FILES} arquivos gerados.")
    print(f"{'=' * 60}")
if __name__ == "__main__":
    main()
