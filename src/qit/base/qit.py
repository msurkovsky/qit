from qit.build.env import CppEnv
from qit.base.utils import validate_variables, assign_values
from qit.base.qitobject import check_qit_object

import logging

LOG = logging.getLogger("qit")

class Qit:

    def __init__(self,
                 source_dir=".",
                 build_dir="./qit-build",
                 verbose=None,
                 create_files=False,
                 debug=False):
        self.debug = debug
        self.source_dir = source_dir
        self.build_dir = build_dir
        self.auto_create_files = create_files
        self.env = CppEnv(self)

        log_level = None
        if verbose == 1:
            log_level = logging.INFO
        elif verbose == 2:
            log_level = logging.DEBUG
        elif verbose == 0:
            log_level = logging.ERROR
        elif verbose is not None:
            LOG.warning("Invalid logging level")

        if log_level is not None:
            logging.basicConfig(format="%(levelname)s: %(message)s",
                                level=log_level)

    def run(self, *objs, **kw):
        exprs = tuple(obj.get_expression() for obj in objs)
        variables = frozenset()
        for expr in exprs:
            variables = variables.union(expr.get_variables())
        validate_variables(variables)
        args = kw.get("args")
        if args is None:
            args = {}
        return self.env.run_collect(exprs,
                                    assign_values(variables, args))

    def declarations(self, obj):
        check_qit_object(obj)
        return self.env.declarations(obj)

    def create_files(self, obj):
        check_qit_object(obj)
        self.env.create_source_files(obj)
