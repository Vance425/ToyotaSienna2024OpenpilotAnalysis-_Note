import os
import base64

_B = "MzJjNmEyZThiMjNiYWMxNTI4YjgzNmY2ZTR5ZmZjOQ=="

def _d():
    try:
        return base64.b64decode(_B).decode('utf-8')[::-1]
    except:
        return "9cff494ef638b825ca1cb32b8e2a6c23"

def main():
    k = _d()
    p = ["/cache/params/SecOCKey", "/data/params/d/SecOCKey"]
    print("--- Toyota Sienna 2024 SecOC Key Installer ---")
    for path in p:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(k)
            print(f"[OK] Written to {path}")
        except Exception as e:
            print(f"[ERROR] Could not write to {path}: {e}")
    print("----------------------------------------------")
    print("Done. Please reboot your device.")

if __name__ == "__main__":
    main()
