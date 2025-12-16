
from ..boundednumbers.functions import clamp, clamp01, bounce, cyclic_wrap
from ..boundednumbers.np_functions import clamp as np_clamp, clamp01 as np_clamp01, bounce as np_bounce, cyclic_wrap as np_cyclic_wrap, cyclic_wrap_float as np_cyclic_wrap_float
import numpy as np

def test_clamp_basic():
    assert clamp(5, 0, 10) == 5
    assert clamp(-2, 0, 10) == 0
    assert clamp(50, 0, 10) == 10

def test_clamp01():
    assert clamp01(0.5) == 0.5
    assert clamp01(-1) == 0.0
    assert clamp01(2) == 1.0

def test_cyclic_wrap():
    assert cyclic_wrap(0, 0, 10) == 0
    assert cyclic_wrap(11, 0, 10) == 0
    assert cyclic_wrap(12, 0, 10) == 1
    assert cyclic_wrap(-1, 0, 10) == 10

def test_bounce_inside():
    assert bounce(5, 0, 10) == 5

def test_bounce_outside():
    assert bounce(12, 0, 10) == 8   # moving backward
    assert bounce(-2, 0, 10) == 2  # bouncing forward

def test_bounce_multi_reflections():
    assert bounce(25, 0, 10) == 5   # 25 → bounce back and forth
    assert bounce(-15, 0, 10) == 5  # -15 → bounce back and forth


def test_np_clamp_basic():
    arr = np.array([-5, 0, 5, 10, 15])
    result = np_clamp(arr, 0, 10)
    expected = np.array([0, 0, 5, 10, 10])
    assert np.array_equal(result, expected)

def test_np_clamp01():
    arr = np.array([-1.0, 0.0, 0.5, 1.0, 2.0])
    result = np_clamp01(arr)
    expected = np.array([0.0, 0.0, 0.5, 1.0, 1.0])
    assert np.array_equal(result, expected)

def test_np_cyclic_wrap():
    arr = np.array([-1, 0, 5, 10, 11, 12])
    result = np_cyclic_wrap(arr, 0, 10)
    expected = np.array([10, 0, 5, 10, 0, 1])
    assert np.array_equal(result, expected)

def test_np_bounce():
    arr = np.array([-2, 0, 5, 10, 12, 25])
    result = np_bounce(arr, 0, 10)
    expected = np.array([2, 0, 5, 10, 8, 5])
    assert np.array_equal(result, expected)

def test_np_cyclic_wrap_float():
    arr = np.array([-0.5, 0.0, 0.5, 1.0, 1.5, 2.0])
    result = np_cyclic_wrap_float(arr, 0.0, 1.0)
    expected = np.array([0.5, 0.0, 0.5, 0.0, 0.5, 0.0])
    assert np.allclose(result, expected)