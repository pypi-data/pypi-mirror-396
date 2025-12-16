import pytest
import smartpy as sp


@sp.module
def main():
    class MC(sp.Contract):
        @sp.entrypoint
        def ep(self):
            raise "error"


def test_syrupy(scenario, snapshot):
    c = main.MC()
    scenario += c

    with pytest.raises(sp.FailwithException) as exc_info:
        c.ep()

    assert snapshot == exc_info.value.value
