import sys
from .lens import DebugLens

def main():
    lens = DebugLens()
    if len(sys.argv) > 1:
        expr = sys.argv[1]
        try:
            obj = eval(expr)
            lens.view(obj)
        except Exception as e:
            print(f"⚠️ Could not evaluate expression: {e}")
    else:
        print("Usage: python -m debuglens '<expression>'")

if __name__ == "__main__":
    main()
