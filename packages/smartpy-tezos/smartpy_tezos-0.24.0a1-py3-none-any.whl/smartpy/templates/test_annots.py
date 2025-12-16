import smartpy as sp


@sp.module
def main():
    class C(sp.Contract):
        def __init__(self):
            self.data.x = sp.cast(
                {}, sp.map[sp.record(a=sp.nat, b=sp.address, c=sp.nat), sp.unit]
            )

        @sp.entrypoint
        def ep(self):
            assert sp.record(a=0, b=sp.sender, c=0) in self.data.x


@sp.add_test()
def test():
    scenario = sp.test_scenario("annots")
    scenario += main.C()
