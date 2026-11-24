"""Tests that the demonstration code follows the rules written for it.

The rules exist so a beginner can read every line: standard library only, no
classes where a function will do, no decorators, type hints and a docstring on
every function, short modules, and no long comprehensions. Every function
docstring also names the invariant it serves.
"""
import ast
import re
import sys
from pathlib import Path

import pytest

DEMO = Path(__file__).resolve().parents[1] / "demo" / "supplier_demo"
MODULES = sorted(DEMO.glob("*.py"))
MAX_LINES = 105


def parse(path):
    """Return the syntax tree of a module."""
    return ast.parse(path.read_text())


def functions(tree):
    """Return every function definition in a tree."""
    return [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


@pytest.mark.parametrize("path", MODULES, ids=lambda p: p.name)
def test_module_is_short_enough_to_read_in_one_sitting(path):
    assert len(path.read_text().splitlines()) <= MAX_LINES


@pytest.mark.parametrize("path", MODULES, ids=lambda p: p.name)
def test_module_imports_only_the_standard_library_and_the_demo_itself(path):
    allowed = set(sys.stdlib_module_names) | {"supplier_demo"}
    for node in ast.walk(parse(path)):
        if isinstance(node, ast.Import):
            names = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module.split(".")[0]]
        else:
            continue
        for name in names:
            assert name in allowed, path.name + " imports " + name


@pytest.mark.parametrize("path", MODULES, ids=lambda p: p.name)
def test_module_has_no_classes_decorators_or_lambdas(path):
    for node in ast.walk(parse(path)):
        assert not isinstance(node, ast.ClassDef), "a class in " + path.name
        assert not isinstance(node, ast.Lambda), "a lambda in " + path.name
        if isinstance(node, ast.FunctionDef):
            assert node.decorator_list == [], node.name + " has a decorator"


@pytest.mark.parametrize("path", MODULES, ids=lambda p: p.name)
def test_every_function_has_type_hints(path):
    for function in functions(parse(path)):
        assert function.returns is not None, function.name + " has no return type"
        for argument in function.args.args:
            assert argument.annotation is not None, function.name + "(" + argument.arg + ") has no type"


@pytest.mark.parametrize("path", MODULES, ids=lambda p: p.name)
def test_every_function_docstring_names_the_invariant_it_serves(path):
    for function in functions(parse(path)):
        docstring = ast.get_docstring(function)
        assert docstring, function.name + " has no docstring"
        assert re.search(r"INV-\d+", docstring), function.name + " does not name an invariant"


@pytest.mark.parametrize("path", MODULES, ids=lambda p: p.name)
def test_no_comprehension_is_longer_than_one_clause(path):
    kinds = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
    for node in ast.walk(parse(path)):
        if isinstance(node, kinds):
            assert len(node.generators) == 1, "nested comprehension in " + path.name
            assert node.generators[0].ifs == [], "filtered comprehension in " + path.name


def test_the_demo_has_the_three_modules_the_walkthrough_explains():
    assert {path.name for path in MODULES} >= {"ledger.py", "outbound.py", "rules.py"}
