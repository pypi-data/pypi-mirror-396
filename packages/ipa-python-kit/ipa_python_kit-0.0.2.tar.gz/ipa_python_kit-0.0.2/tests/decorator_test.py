import pytest

from sdk.decorator import catch


def test_catch():
    @catch(includes=(ValueError), excludes=(KeyError,), on_catch=print)
    def func1(a, b):
        raise ValueError(f"value error: a={a}, b={b}")

    @catch(includes=(ValueError), excludes=(KeyError,))
    def func2(a, b):
        raise KeyError(f"key error: a={a}, b={b}")

    func1(a=1, b=2)

    with pytest.raises(KeyError):
        func2(1, 2)
