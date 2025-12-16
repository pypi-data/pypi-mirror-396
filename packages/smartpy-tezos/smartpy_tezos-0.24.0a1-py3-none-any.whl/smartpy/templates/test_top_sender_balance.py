import smartpy as sp


@sp.module
def main():
    class MyContract(sp.Contract):
        @sp.entrypoint()
        def pay(self):
            pass

        @sp.entrypoint()
        def request(self):
            sp.send(sp.sender, sp.tez(1))

    class Wallet(sp.Contract):
        @sp.entrypoint
        def default(self):
            pass


sc = sp.test_scenario("Test")
wallet = main.Wallet()
wallet.set_initial_balance(sp.tez(2))
c1 = main.MyContract()
sc += c1
sc += wallet

sc.verify(wallet.balance == sp.tez(2))
c1.pay(_sender=wallet.address, _amount=sp.tez(1))
sc.verify(wallet.balance == sp.tez(1))
c1.request(_sender=wallet.address)
sc.verify(wallet.balance == sp.tez(2))

# Sender, no source
try:
    c1.pay(_sender=wallet.address, _amount=sp.tez(3))
except sp.RuntimeException as e:
    print(e)
else:
    raise Exception("Expected error")

# Source, no sender
try:
    c1.pay(_source=wallet.address, _amount=sp.tez(3))
except sp.RuntimeException as e:
    print(e)
else:
    raise Exception("Expected error")

# Same source and sender
try:
    c1.pay(_source=wallet.address, _sender=wallet.address, _amount=sp.tez(3))
except sp.RuntimeException as e:
    print(e)
else:
    raise Exception("Expected error")

# Different source and sender
alice = sp.test_account("alice")
try:
    c1.pay(_source=alice.address, _sender=wallet.address, _amount=sp.tez(3))
except sp.RuntimeException as e:
    print(e)
else:
    raise Exception("Expected error")

# No source nor sender
c1.pay(_amount=sp.tez(3))
