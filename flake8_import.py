import ast
from dataclasses import dataclass

import astpretty


@dataclass
class NameRule:
    name: str
    allow_asnames: list[str]


@dataclass
class Rule:
    module_name: str
    allow_from_import: bool
    name_rules: list[NameRule]


default_rules = [
    Rule(
        module_name="datetime",
        allow_from_import=False,
        name_rules=[
            NameRule(
                name="date",
                allow_asnames=["d"],
            )
        ],
    )
]

__version__ = "0.0.1"


class Flake8Error:
    def __init__(self, *, code: str, message: str):
        self._code = code
        self._message = message

    @property
    def error_message(self) -> str:
        return f"{self._code} {self._message}"


class ImportChecker(object):
    name = "import"
    version = __version__

    def __init__(self, tree: ast.Module, filename: str):
        self.tree = tree
        self.rules = default_rules

    def run(self):
        for child in ast.iter_child_nodes(self.tree):
            if err := self._check_node(child):
                yield child.lineno, child.col_offset, err.error_message, type(self)

    def _check_node(self, node: ast.AST) -> Flake8Error | None:
        if isinstance(node, ast.Import):
            return self._process_import(node)
        if isinstance(node, ast.ImportFrom):
            return self._process_import_from(node)
        return None

    def _process_import(self, node: ast.Import) -> Flake8Error | None:
        astpretty.pprint(ast.parse(node))
        return Flake8Error(code="X100", message="found import")

    def _process_import_from(self, node: ast.ImportFrom) -> Flake8Error | None:
        """import ... from のチェック"""
        astpretty.pprint(ast.parse(node))
        for rule in self.rules:
            if rule.module_name == node.module:
                if rule.allow_from_import:
                    for name_rule in rule.name_rules:
                        for node_name in node.names:
                            if name_rule.name == node_name:
                                if node_name.asname not in name_rule.allow_asnames:
                                    return Flake8Error(
                                        code="X201",
                                        message="not allowed as name is detected.",
                                    )
                else:
                    return Flake8Error(
                        code="X200", message="import from statement is not allowed."
                    )
