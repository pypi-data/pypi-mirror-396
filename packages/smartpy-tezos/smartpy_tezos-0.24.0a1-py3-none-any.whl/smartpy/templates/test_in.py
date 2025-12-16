import smartpy as sp


@sp.module
def main():
    class Test_in(sp.Contract):
        def __init__(self):
            self.data.my_set = {1, 2, 3, 5, 8, 13}
            self.data.my_map = {"alice": 100, "bob": 200, "charlie": 300}
            self.data.my_big_map = sp.cast(
                sp.big_map({"x": 10, "y": 20, "z": 30}), sp.big_map[sp.string, sp.int]
            )
            self.data.my_str = "hello"
            self.data.result = False

        @sp.entrypoint
        def test_in_set(self, value: sp.int):
            """Test if a value is in the set."""
            self.data.result = value in self.data.my_set

        @sp.entrypoint
        def test_in_map(self, key):
            """Test if a key is in the map."""
            self.data.result = key in self.data.my_map

        @sp.entrypoint
        def test_in_big_map(self, key):
            """Test if a key is in the big_map."""
            self.data.result = key in self.data.my_big_map

        @sp.entrypoint
        def test_contains_deprecation_msg(self, key):
            """Should produce a warning in the err file."""
            self.data.result = self.data.my_set.contains(key)


@sp.add_test()
def test():
    scenario = sp.test_scenario("Test")
    scenario.h1("Test 'in' operator")

    c = main.Test_in()
    scenario += c

    scenario.h2("Test 'in' with set")

    c.test_in_set(1)
    scenario.verify(c.data.result == True)

    c.test_in_set(2)
    scenario.verify(c.data.result == True)

    c.test_in_set(3)
    scenario.verify(c.data.result == True)

    c.test_in_set(5)
    scenario.verify(c.data.result == True)

    c.test_in_set(8)
    scenario.verify(c.data.result == True)

    c.test_in_set(13)
    scenario.verify(c.data.result == True)

    scenario.h2("Test 'not in' with set")

    c.test_in_set(4)
    scenario.verify(c.data.result == False)

    c.test_in_set(6)
    scenario.verify(c.data.result == False)

    c.test_in_set(7)
    scenario.verify(c.data.result == False)

    c.test_in_set(9)
    scenario.verify(c.data.result == False)

    c.test_in_set(10)
    scenario.verify(c.data.result == False)

    c.test_in_set(11)
    scenario.verify(c.data.result == False)

    c.test_in_set(12)
    scenario.verify(c.data.result == False)

    c.test_in_set(14)
    scenario.verify(c.data.result == False)

    scenario.h2("Test 'in' with map")

    c.test_in_map("alice")
    scenario.verify(c.data.result == True)

    c.test_in_map("bob")
    scenario.verify(c.data.result == True)

    c.test_in_map("charlie")
    scenario.verify(c.data.result == True)

    c.test_in_map("dave")
    scenario.verify(c.data.result == False)

    scenario.h2("Test 'not in' with map")

    c.test_in_map("eve")
    scenario.verify(c.data.result == False)

    c.test_in_map("frank")
    scenario.verify(c.data.result == False)

    scenario.h2("Test 'in' with big map")

    c.test_in_big_map("x")
    scenario.verify(c.data.result == True)

    c.test_in_big_map("y")
    scenario.verify(c.data.result == True)

    c.test_in_big_map("z")
    scenario.verify(c.data.result == True)

    scenario.h2("Test 'not in' with big map")

    c.test_in_big_map("w")
    scenario.verify(c.data.result == False)

    c.test_in_big_map("v")
    scenario.verify(c.data.result == False)

    c.test_in_big_map("u")
    scenario.verify(c.data.result == False)

    scenario.h2("Test deprecation message for contains")

    c.test_contains_deprecation_msg(13)
    scenario.verify(c.data.result == True)

    c.test_contains_deprecation_msg(4)
    scenario.verify(c.data.result == False)
