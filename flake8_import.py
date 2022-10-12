import ast
from dataclasses import dataclass


@dataclass
class NameRule:
    name: str
    asnames: list[str]


@dataclass
class Rule:
    # e.g. defusedxml.ElementTree, bs4
    module_name: str
    use_from: bool
    name_rules: list[NameRule]


default_rules = [
    Rule(
        module_name="datetime",
        use_from=False,
        name_rules=[
            NameRule(
                name="date",
                asnames=["d"],
            )
        ],
    )
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
            return self._process_import_from(node)
        return []

    def _process_import(self, node: ast.Import) -> list[Flake8Error]:
        """import のチェック"""
        errors: list[Flake8Error] = []
        for rule in self.rules:
            for aliases in node.names:
                if rule.module_name == aliases.name:
                    if rule.use_from:
                        error = Flake8Error(
                            code="X100",
                            message=f"`import {rule.module_name}` is detected. use `from {node.module} import ...` instead.",
                            lineno=aliases.lineno,
                            col_offset=aliases.col_offset,
                        )
                        errors.append(error)
                    else:
                        for name_rule in rule.name_rules:
                            if aliases.asname is not None:
                                if aliases.asname not in name_rule.asnames:
                                    error = Flake8Error(
                                        code="X300",
                                        message=f"`import {aliases.name} as {aliases.asname}` is not allowed.",
                                        lineno=aliases.lineno,
                                        col_offset=aliases.col_offset,
                                    )
                                    errors.append(error)
        return errors

    def _process_import_from(self, node: ast.ImportFrom) -> list[Flake8Error]:
        """import ... from のチェック"""
        errors: list[Flake8Error] = []
        for rule in self.rules:
            if rule.module_name == node.module:
                if rule.use_from:
                    for name_rule in rule.name_rules:
                        for aliases in node.names:
                            if name_rule.name == aliases:
                                if aliases.asname is not None:
                                    if aliases.asname not in name_rule.asnames:
                                        error = Flake8Error(
                                            code="X300",
                                            message=f"`import {aliases.name} as {aliases.asname}` is not allowed.",
                                            lineno=aliases.lineno,
                                            col_offset=aliases.col_offset,
                                        )
                                        errors.append(error)
                else:
                    error = Flake8Error(
                        code="X200",
                        message=f"`from {node.module} import ...` is detected. use `import {node.module}` instead.",
                        lineno=node.lineno,
                        col_offset=node.col_offset,
                    )
                    errors.append(error)
        return errors
