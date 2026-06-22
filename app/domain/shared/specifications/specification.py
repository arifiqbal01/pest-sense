from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """
    Base domain specification contract.

    Encapsulates reusable business/scientific rule evaluation.
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        raise NotImplementedError

    def __call__(self, candidate: T) -> bool:
        return self.is_satisfied_by(candidate)

    def __and__(self, other: "Specification[T]") -> "AndSpecification[T]":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification[T]") -> "OrSpecification[T]":
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification[T]":
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left(candidate) and self.right(candidate)


class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left(candidate) or self.right(candidate)


class NotSpecification(Specification[T]):
    def __init__(self, wrapped: Specification[T]):
        self.wrapped = wrapped

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.wrapped(candidate)