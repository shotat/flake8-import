import ast

import astpretty


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
        astpretty.pprint(ast.parse(node))
        module_name = node.module
        name = node.names[0].name
        return Flake8Error(code="X200", message="found import from")
