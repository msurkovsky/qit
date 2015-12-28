from testutils import Qit, init
init()

from qit import Int, Variable

def test_variable():
    c = Qit()

    x = Variable(Int(), "x")
    assert c.run(x, args={x: 3}) == 3

def test_add_variables():
    c = Qit()

    x = Variable(Int(), "x")
    y = Variable(Int(), "y")
    assert c.run(x + y, args={x: 4, y: 6}) == 10

def test_add_constant():
    c = Qit()

    x = Variable(Int(), "x")
    assert c.run(x + 3, args={x: 4}) == 7
    assert c.run(3 + x, args={x: 5}) == 8
