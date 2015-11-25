from testutils import Qit, init
init()

from qit import Range, Variable, Int, Function

def test_range_iterate():
    expr = Range(10).iterate()
    c = Qit()
    assert list(range(10)) == c.run(expr)

def test_range_generate():
    expr = Range(10).generate().take(10)
    c = Qit()
    lst = c.run(expr)
    assert len(lst) == 10
    assert all(i >= 0 and i < 10 for i in lst)

def test_range_variable_iterate():
    c = Qit()
    x = Variable(Int(), "x")
    r = Range(x).iterate()
    assert list(range(10)) == c.run(r, { "x": 10 })

def test_range_variable_generate():
    c = Qit()
    x = Variable(Int(), "x")
    r = Range(x).generate().take(30)
    result = c.run(r, { "x": 3 })
    for i in result:
        assert 0 <= i < 3

def test_range_function_iterate():
    c = Qit()

    x = Variable(Int(), "x")
    r = Range(x).iterate()
    f = r.make_function()
    assert [[], [0], [0,1], [0,1,2]] == c.run(Range(4).iterate().map(f))

def test_range_function_generate():
    f = Function().takes(Int(), "a").returns(Int()).code("return a + 1;")
    c = Qit()

    x = Variable(Int(), "x")
    r = Range(f(x)).generate().take(2)
    f = r.make_function()
    result = c.run(Range(10).iterate().map(f))

    assert len(result) == 10
    for i, r in enumerate(result):
        assert len(r) == 2
        assert 0 <= r[0] < i+1
