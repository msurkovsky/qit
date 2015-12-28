
from qit.base.qitobject import QitObject

class Expression(QitObject):

    def __init__(self, type):
        self.type = type

    @property
    def childs(self):
        return (self.type,)

    def is_expression(self):
        return True

    def is_constructor(self):
        return False

    def write_into_variable(self, builder):
        return builder.write_expression_into_variable(self)

    def make_function(self, params=None):
        from qit.base.function import FunctionFromExpression
        return FunctionFromExpression(self, params)

    def get_expression(self):
        return self

    def __add__(self, other):
        if not (self.type.is_python_instance(other) or
               (isinstance(other, self.__class__) and self.type == other.type)):

            from qit.base.type import IncompatibleTypesException
            if isinstance(other, self.__class__):
                raise IncompatibleTypesException(self.type, other.type)
            raise IncompatibleTypesException(self.type, type(other))

        from qit.base.function import Function
        f = Function().takes(self.type, "a").takes(self.type, "b")
        f.returns(self.type)
        f.code("return a + b;")
        return f(self, other)

    def __radd__(self, other):
        return self.__add__(other)
