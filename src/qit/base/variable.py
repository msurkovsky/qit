
from qit.base.expression import Expression


class Variable(Expression):

    def __init__(self, type, name):
        super().__init__(type)
        self.name = name

    def is_variable(self):
        return True

    def build(self, builder):
        return "qit_freevar_" + self.name

    def get_variables(self):
        return frozenset((self,))

    def __add__(self, other):
        if not (self.type.is_python_instance(other) or
               (isinstance(other, self.__class__) and self.type == other.type)):

            if isinstance(other, self.__class__):
                raise IncompatibleTypesException(self.type, other.type)
            raise IncompatibleTypesException(self.type, type(other))

        f = Function().takes(self.type, "a").takes(self.type, "b")
        f.returns(self.type)
        f.code("return a + b;")
        return f(self, other)

    def __radd__(self, other):
        return self.__add__(other)

    def __repr__(self):
        return "Variable({}, {})".format(self.type, repr(self.name))

from qit.base.function import Function
from qit.base.type import IncompatibleTypesException
