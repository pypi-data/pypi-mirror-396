
import base64
DATA_B64 = "VGVzdA=="
def save(filename="code_moi_ve.py"):
    try:
        decoded = base64.b64decode(DATA_B64).decode("utf-8")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(decoded)
        print(f"OK: Da luu code vao {filename}")
    except Exception as e:
        print(f"LOI: {e}")
