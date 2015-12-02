from qit.base.function import Function
from qit.base.int import Int

def multiplication_n(size):
     f = Function().returns(Int())
     for i in range(size):
        f.takes(Int())
     code = "*".join(p[1] for p in f.params)
     f.code("return {};".format(code))
     return f

# Naive way of making power, but it is sufficient for now
power = Function().takes(Int(), "base").takes(Int(), "power").returns(Int())
power.code("""
    int result = 1;
    int p = power;
    while(p > 0) {
        result *= base;
        p--;
    }
    return result;
""")
