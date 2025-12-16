import smartpy as sp


@sp.module
def main():
    class C(sp.Contract):
        def __init__(self):
            self.data.index = None

        @sp.entrypoint
        def add_address(self, address):
            self.data.index = sp.Some(sp.index_address(address))

        @sp.onchain_view
        def get_address(self, address: sp.address) -> sp.option[sp.nat]:
            return sp.get_address_index(address)

        @sp.private(with_index_address=True)
        def f(self, address):
            return sp.index_address(address)

        @sp.entrypoint
        def add_address_f(self, address):
            self.data.index = sp.Some(self.f(address))


sc = sp.test_scenario("Test")
c1 = main.C()
sc += c1
alice = sp.test_account("Alice")
bob = sp.test_account("Bob")
eve = sp.test_account("Charlie")

sc.verify(c1.get_address(alice.address) == None)

c1.add_address(alice.address)
sc.verify(c1.data.index == sp.Some(1))
sc.verify(c1.get_address(alice.address) == sp.Some(1))

c1.add_address(alice.address)
sc.verify(c1.data.index == sp.Some(1))
sc.verify(c1.get_address(alice.address) == sp.Some(1))


c1.add_address(bob.address)
sc.verify(c1.data.index == sp.Some(2))
sc.verify(c1.get_address(bob.address) == sp.Some(2))


c1.add_address_f(alice.address)
sc.verify(c1.data.index == sp.Some(1))
sc.verify(c1.get_address(alice.address) == sp.Some(1))


c1.add_address(eve.address)
sc.verify(c1.data.index == sp.Some(3))
sc.verify(c1.get_address(eve.address) == sp.Some(3))

try:
    c1.add_address(bob.address)
    sc.verify(c1.data.index == sp.Some(0))
except Exception as e:
    print(e)
else:
    assert False

try:
    sc.verify(c1.get_address(eve.address) == sp.Some(0))
except Exception as e:
    print(e)
else:
    assert False


@sp.module
def bad():
    class C(sp.Contract):
        def __init__(self):
            self.data.index = None

        @sp.private(with_index_address=True)
        def f(self, address):
            return sp.index_address(address)

        @sp.onchain_view
        def wrong(self, address):
            return self.f(address)


try:
    sc = sp.test_scenario("TestBad")
    c1 = bad.C()
    sc += c1
except Exception as e:
    print(e)
else:
    assert False
