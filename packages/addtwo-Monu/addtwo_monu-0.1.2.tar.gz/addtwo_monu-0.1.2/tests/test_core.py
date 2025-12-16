from addtwo import add
import pytest

def test_add_ints():
    assert add(1, 2) == 3

def test_add_floats():
    assert add(1.5, 0.5) == 2.0

def test_bad_types():
    with pytest.raises(TypeError):
        add("1", 2)
