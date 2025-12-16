import pytest
from debuglens.lens import DebugLens

def test_trace_decorator(capsys):
    lens = DebugLens()
    
    @lens.trace
    def add(a, b):
        return a + b

    result = add(2, 3)
    captured = capsys.readouterr()
    assert "Calling add" in captured.out
    assert "returned 5" in captured.out
    assert result == 5