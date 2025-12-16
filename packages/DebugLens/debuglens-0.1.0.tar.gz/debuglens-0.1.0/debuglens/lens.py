import inspect
import pprint

class DebugLens:
    """
    A simple inspection and debugging utility.
    """

    def __init__(self, verbose=True):
        self.verbose = verbose

    def view(self, obj, depth=2):
        """Pretty-print an object with inspection details."""
        print("🔍 DebugLens Inspection")
        print(f"Type: {type(obj)}")
        print("Attributes:")
        pprint.pprint(dir(obj), depth=depth)

    def trace(self, func):
        """Decorator to trace function calls and returns."""
        def wrapper(*args, **kwargs):
            print(f"➡️ Calling {func.__name__} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            print(f"⬅️ {func.__name__} returned {result}")
            return result
        return wrapper

    def info(self, obj):
        """Show source code if available."""
        try:
            source = inspect.getsource(obj)
            print("📜 Source Code:")
            print(source)
        except Exception:
            print("⚠️ Source not available.")