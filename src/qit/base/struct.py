
from qit.base.type import Type
from qit.base.function import Function


class Struct(Type):

    autoname_prefix = "Struct"

    def __init__(self, *args):
        self.name = None
        names = []
        types = []

        for arg in args:
            if isinstance(arg, tuple) and len(arg) == 2:
                types.append(arg[0].as_type())
                names.append(arg[1])
            else:
                types.append(arg.as_type())
                names.append("v{}".format(len(names)))

        assert len(set(names)) == len(names)
        self.names = tuple(names)
        self.types = tuple(types)

    @property
    def childs(self):
        return self.types

    def is_python_instance(self, obj):
        return isinstance(obj, tuple) and len(obj) == len(self.names)

    def transform_python_instance(self, obj):
        return tuple(t.value(v) for t, v in zip(self.types, obj))

    def childs_from_value(self, value):
        return value

    def declare(self, builder):
        builder.declare_struct(self)

    def read(self, f):
        if not self.names:
            return ()
        lst = []
        for t in self.types:
            element = t.read(f)
            if element is None:
                if not lst:
                    return None # First element
                else:
                    raise Exception("Incomplete struct")
            lst.append(element)
        return tuple(lst)

    @property
    def write_function(self):
        functions = tuple(t.write_function for t in self.types)
        f = self.prepare_write_function()
        f.code("""
        {%- for name, f in _names_and_functions %}
            {{b(f)}}(output, value.{{name}});
        {%- endfor %}
        """, _names_and_functions=zip(self.names, functions))
        f.uses(functions)
        return f

    def build_value(self, builder, value):
        assert len(value) == len(self.types)
        args = ",".join(v.build(builder)
                        for t, v in zip(self.types, value))
        return "{}({})".format(self.build(builder), args)

    def __mul__(self, other):
        args = list(zip(self.types, self.names))
        args.append(other)
        return Struct(*args)

    def __repr__(self):
        return "Struct({})".format(
                ", ".join("({}, {})".format(repr(t), repr(name))
                for t, name in zip(self.types, self.names)))


class KeyValue(Struct):

    def __init__(self, key_type, value_type):
        super().__init__((key_type, "key"), (value_type, "value"))

    @property
    def value_fn(self):
        f = Function().takes(self, "keyval").returns(self.types[1])
        f.code("return keyval.value;")
        return f

    @property
    def key_fn(self):
        f = Function().takes(self, "keyval").returns(self.types[0])
        f.code("return keyval.key;")
        return f

    @property
    def max_fn(self):
        f = Function().takes(self, "keyval1").takes(self, "keyval2")
        f.returns(self)
        f.code("return keyval1.value < keyval2.value ? keyval2 : keyval1;")
        return f

    @property
    def min_fn(self):
        f = Function().takes(self, "keyval1").takes(self, "keyval2")
        f.returns(self)
        f.code("return keyval1.value > keyval2.value ? keyval2 : keyval1;")
        return f
