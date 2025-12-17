from functools import cached_property

from dyngle.model.expression import expression, yaml_structure_expression
from dyngle.model.context import Context
from dyngle.model.operation import Operation


class Dyngleverse:
    """Represents the entire set of definitions for operations, expressions,
    and values.

    The Dyngleverse acts as a registry/index for all operations and global
    constants (values and expressions). It maintains:

    - operations: A dict of Operation objects indexed by name
    - global_constants: A Context containing global values and expressions

    When operations are created, they receive a reference to global_constants
    and merge them with their own local constants, establishing the proper
    scoping hierarchy:

    1. Global constants (lowest precedence)
    2. Local operation constants (higher precedence)
    3. Live data from execution (highest precedence, shared across operations)
    """

    def __init__(self):
        self.operations = {}
        self.global_constants = Context()

    def load_constants(self, config: dict):
        """
        Load only the constants (values and expressions) from a config.
        This allows for two-phase loading where all constants are loaded first,
        then all operations are created with access to all constants.
        """
        self.global_constants |= Dyngleverse.parse_constants(config)

    def load_operations(self, config: dict):
        """
        Load only the operations from a config.
        Should be called after all constants have been loaded.
        """
        ops_defs = config.get("operations") or {}
        for key, op_def in ops_defs.items():
            operation = Operation(self, op_def, key)
            self.operations[key] = operation

    @staticmethod
    def parse_constants(definition: dict) -> Context:
        """
        At either the global (dyngleverse) or local (within an operation)
        level, we might find values and expressions.
        
        Expressions can be either:
        - Strings (traditional Python expression syntax)
        - Dicts/lists (YAML structure syntax)
        """

        expr_defs = definition.get("expressions") or {}
        expressions = {}
        for k, v in expr_defs.items():
            if isinstance(v, str):
                # Traditional string expression
                expressions[k] = expression(v)
            elif isinstance(v, (dict, list)):
                # YAML structure expression
                expressions[k] = yaml_structure_expression(v)
            else:
                # Other types (shouldn't happen, but handle gracefully)
                expressions[k] = expression(str(v))
        
        values = definition.get("values") or {}
        return Context(expressions) | values
