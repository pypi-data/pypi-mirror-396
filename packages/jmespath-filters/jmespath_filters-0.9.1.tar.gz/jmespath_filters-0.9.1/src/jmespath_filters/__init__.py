from __future__ import annotations

import typing
from abc import ABC, abstractmethod

import jmespath


__author__ = "Giovanni Bronzini"
__version__ = "0.9.1"


try:
    from typing import override
except ImportError:
    override = lambda _func: _func


if typing.TYPE_CHECKING:
    Rules = "str | dict[str, Expression] | Expression | list[Expression]"
    Payload = dict | str | None


class BaseExpression(ABC):
    """Parent class for expressions."""

    def __init__(self, rules: Rules) -> None:
        key = None
        if not rules:
            raise ValueError("Expression must be a non-empty string or dictionary")
        if isinstance(rules, dict):
            key = list(rules.keys())[0]
            if key not in ("AND", "OR", "NOT"):
                raise ValueError(
                    f"Rule dictionary may only contain one key for the following list: AND, OR, NOT. Found '{key}'"
                )
            if key in ("AND", "OR") and len(rules[key]) < 2:
                raise ValueError(f"{key} needs at least 2 expressions")
            if key == 'NOT' and not isinstance(rules[key], str) and len(rules[key]) != 1:
                raise ValueError("NOT needs 1 expression only")

        self._match: typing.Callable[[typing.Any], bool] | None = None
        self._rules = rules
        self._compile()

    @abstractmethod
    def _compile(self) -> None:
        """Abstract method to compile the expression and set the matcher function in self._match."""
        ...

    def match(self, data: Payload) -> bool:
        """Invoke the matcher against data."""
        return self._match(data)


class Composite(BaseExpression):
    """A composite expression is a single-element dict.

    The key is on of AND, OR, NOT and the value is either a Simple or Not expression or a list of Simple
    or Composite expression.
    """

    def __init__(self, rules: Rules) -> None:
        super().__init__(rules)
        self._rules = [Expression(rule) for rule in self._rules]


class Simple(BaseExpression):
    """Simple string expression."""

    def _compile(self) -> None:
        self._match = lambda data: bool(jmespath.search(self._rules, data))


class Not(BaseExpression):
    """Negate expression."""

    def _compile(self) -> None:
        self._match = lambda data: not Simple(self._rules).match(data)


class Expression(BaseExpression):
    """Expression.

    An Expression is either a Simple or Not expression or dictionary of either:
    - a NOT key and an expression as value
    - a dict with a key which value can be either "AND" or "OR" and a list of expressions
    """

    expression: BaseExpression | None = None

    def _compile(self) -> None:
        if isinstance(self._rules, str):
            self.expression = Simple(self._rules)
        else:
            key, rules = list(self._rules.items())[0]

            self.expression = {"NOT": Not, "AND": And, "OR": Or}[key](rules)

    def match(self, data: Payload) -> bool:
        """Match the expression against data."""
        return self.expression.match(data)


class Or(Composite):
    """Match all expressions in list."""

    def _compile(self) -> None:
        self._match = lambda data: any(rule.match(data) for rule in self._rules)


class And(Composite):
    """Match all expressions in list."""

    def _compile(self) -> None:
        self._match = lambda data: all(rule.match(data) for rule in self._rules)


class Filter:
    """Jmespath composite expressions filter."""

    def __init__(self, rules: Rules) -> None:
        self._expression = Expression(rules)

    # def from_yaml(self, rules: str) -> dict:
    #     return {}
    #
    # def from_json(self, rules: str) -> dict:
    #     return {}

    def match(self, data: Payload) -> bool:
        """Match the filter expression against data."""
        return self._expression.match(data)
