import os

import pytest
import smartpy as sp


@sp.module
def main():
    class MC(sp.Contract):
        def __init__(self):
            self.data.res = 0

        @sp.entrypoint
        def incr(self, x):
            self.data.res += x


is_mockup = os.environ.get("SMARTPY_FLAGS") and "--mode mockup" in os.environ.get(
    "SMARTPY_FLAGS"
)


def test_unnamed_scenario(snapshot):
    if is_mockup:
        with pytest.raises(Exception) as exc_info:
            sc = sp.test_scenario()
        assert snapshot == str(exc_info.value)
        return
    sc = sp.test_scenario()
    c = main.MC()
    sc += c
    c.incr(1)
    sc.verify(c.data.res == 1)
