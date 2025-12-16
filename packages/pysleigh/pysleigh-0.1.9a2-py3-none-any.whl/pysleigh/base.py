"""Base class for Advent of Code solutions powered by PySleigh."""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Generic, Tuple, TypeVar

from pysleigh.context import get_context
from pysleigh.paths import PathConfig

T = TypeVar("T")
RawAnswer = Any
Answer = str | None
Answers = Tuple[Answer, Answer]


class PartValueError(Exception):
    """Raised when a caller requests an unsupported puzzle part."""


class Base(ABC, Generic[T]):
    """Base class that every Advent of Code solution should subclass."""

    def __init__(self, year: int, day: int, input_text: str | None = None) -> None:
        """Initialize the solution with metadata and parsed input."""
        self.year = year
        self.day = day
        self._input_override = input_text
        self.data: T = self.parse_input()

    @cached_property
    def _path_config(self) -> PathConfig:
        return get_context().paths

    @cached_property
    def _raw_input(self) -> str:
        if self._input_override is not None:
            return self._input_override

        path = self._path_config.input_path(self.year, self.day)
        return path.read_text()

    @cached_property
    def _title(self) -> str:
        path = self._path_config.article_path(self.year, self.day)
        if not path.exists():
            return f"Day {self.day:02d}"

        with path.open("r") as file:
            first_line = file.readline().strip()
        if ":" not in first_line:
            raise ValueError(f"Article header line is not in expected format: {first_line!r}")
        _, remainder = first_line.split(":", 1)
        return remainder.replace("---", "").strip()

    def run(
        self,
        part: int | None = None,
        output: bool = True,
        timing: bool = False,
    ) -> Answers:
        """Execute the requested part(s) and optionally display output."""
        if part not in (1, 2, None):
            raise PartValueError(f"Invalid part argument {part!r}. Valid values are 1, 2 or None.")

        part_1: Answer = None
        part_2: Answer = None

        if output:
            print(f"--- Year {self.year} Day {self.day:02d}: {self._title} ---")

        import time

        if part in (1, None):
            start = time.perf_counter()
            part_1 = str(self.solve_part_one())
            elapsed = time.perf_counter() - start
            if output:
                print(f"Part One: {part_1}")
                if timing:
                    print(f"  (took {elapsed * 1000:.3f} ms)")

        if part in (2, None):
            start = time.perf_counter()
            part_2 = str(self.solve_part_two())
            elapsed = time.perf_counter() - start
            if output:
                print(f"Part Two: {part_2}")
                if timing:
                    print(f"  (took {elapsed * 1000:.3f} ms)")

        return part_1, part_2

    @abstractmethod
    def parse_input(self) -> T:
        """Parse the raw input into the subtype-specific representation."""
        ...

    @abstractmethod
    def solve_part_one(self) -> RawAnswer:
        """Return the raw answer value for part one."""
        ...

    @abstractmethod
    def solve_part_two(self) -> RawAnswer:
        """Return the raw answer value for part two."""
        ...

    def __str__(self) -> str:
        """Return a concise identifier for this solution."""
        return f"Solution({self.year},{self.day},{self._title})"
