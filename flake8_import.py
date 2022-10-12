import ast
from dataclasses import dataclass


@dataclass
class ImportRule:
    enabled: bool
    allowed_asnames: list[str]


@dataclass
class ImportFromRule:
    enabled: bool


@dataclass
class Rule:
    # e.g. defusedxml.ElementTree, bs4
    module_name: str
    # from xxx import ...
    import_rule: ImportRule
    import_from_rule: ImportFromRule


default_rules = [
    Rule(
        module_name="datetime",
        import_rule=ImportRule(
            enabled=True,
            allowed_asnames=["dt"],
        ),
        import_from_rule=ImportFromRule(
            enabled=False,
        ),
    ),
    Rule(
        module_name="ast",
        import_rule=ImportRule(
            enabled=True,
            allowed_asnames=["a"],
        ),
        import_from_rule=ImportFromRule(
            enabled=False,
        ),
    ),
    Rule(
        module_name="dataclasses",
        import_rule=ImportRule(
            enabled=False,
            allowed_asnames=[],
        ),
        import_from_rule=ImportFromRule(
            enabled=True,
        ),
    ),
]

__version__ = "0.0.1"


@dataclass
class Flake8Error:
    code: str
    message: str
    lineno: int
    col_offset: int

    @property
    def error_message(self) -> str:
        return f"{self.code} {self.message}"


class ImportChecker(object):
    name = "import"
    version = __version__

    def __init__(self, tree: ast.Module, filename: str):
        self.tree = tree
        self.rules = default_rules

    def run(self):
        for child in ast.iter_child_nodes(self.tree):
            for err in self._check_node(child):
                yield err.lineno, err.col_offset, err.error_message, type(self)

    def _check_node(self, node: ast.AST) -> list[Flake8Error]:
        if isinstance(node, ast.Import):
            return self._process_import(node)
        if isinstance(node, ast.ImportFrom):
            return self._process_from_import(node)
        return []

    def _process_import(self, node: ast.Import) -> list[Flake8Error]:
        """import のチェック"""
        errors: list[Flake8Error] = []
        for rule in self.rules:
            for alias in node.names:
                if rule.module_name == alias.name:
                    if not rule.import_rule.enabled:
                        error = Flake8Error(
                            code="X100",
                            message=f"`import {rule.module_name}` is detected. use `from {rule.module_name} import ...` instead.",
                            lineno=alias.lineno,
                            col_offset=alias.col_offset,
                        )
                        errors.append(error)

                    if alias.asname is None:
                        continue
                    if len(rule.import_rule.allowed_asnames) == 0:
                        continue
                    if alias.asname not in rule.import_rule.allowed_asnames:
                        error = Flake8Error(
                            code="X300",
                            message=f"`import {alias.name} as {alias.asname}` is not allowed.",
                            lineno=alias.lineno,
                            col_offset=alias.col_offset,
                        )
                        errors.append(error)
        return errors

    def _process_from_import(self, node: ast.ImportFrom) -> list[Flake8Error]:
        """from ... import のチェック"""
        errors: list[Flake8Error] = []
        for rule in self.rules:
            if rule.module_name == node.module:
                if not rule.import_from_rule.enabled:
                    error = Flake8Error(
                        code="X200",
                        message=f"`from {node.module} import ...` is detected. use `import {node.module}` instead.",
                        lineno=node.lineno,
                        col_offset=node.col_offset,
                    )
                    errors.append(error)
        return errors
