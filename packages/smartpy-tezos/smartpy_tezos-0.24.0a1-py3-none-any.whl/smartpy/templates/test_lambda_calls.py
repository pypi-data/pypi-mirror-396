import smartpy as sp
from pytest import mark, raises


@sp.module
def main():
    def f(x: sp.int, y: sp.int):
        return x + y

    class C(sp.Contract):
        @sp.entrypoint
        def f(self):
            _ = f(sp.record(x=1, y=2, z=3))


@mark.skip_mockup
def test_supplementary_fields(scenario, snapshot):
    with raises(sp.TypeError_) as exc_info:
        scenario.add_module(main)
    assert str(exc_info.value) == snapshot
