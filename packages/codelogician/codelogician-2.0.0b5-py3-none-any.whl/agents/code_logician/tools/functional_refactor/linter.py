import os
import subprocess
import tempfile
from abc import ABC, abstractmethod

import structlog
from ruff.__main__ import find_ruff_bin

logger = structlog.get_logger()


class LinterError(Exception):
    """Raised when the linter fails."""


class Linter(ABC):
    """We mean both the linter and the formatter."""

    @abstractmethod
    def lint(self, code: str) -> str:
        """Lint the code and return the linted code."""
        pass

    @abstractmethod
    def format(self, code: str) -> str:
        """Format the code and return the formatted code."""
        pass


class Ruff(Linter):
    def __init__(self):
        self.ruff_bin_path = os.fsdecode(find_ruff_bin())
        self.setup_linting_args()

    def setup_linting_args(self) -> None:
        self.linting_rules = {
            "select": [
                "E",  # pycodestyle errors
                "F",  # pyflakes
                "I",  # isort
                "N",  # pep8-naming
                "UP",  # pyupgrade
                "RUF",  # ruff-specific rules
                "B",  # flake8-bugbear
                "C4",  # flake8-comprehensions
                "PTH",  # flake8-use-pathlib
                "SIM",  # flake8-simplify
            ],
            "ignore": [
                "SIM108",  # if-else-block-instead-of-if-exp
                "N801",  # Class name should use CapWords
                "PTH123",  # `open()` should be replaced by `Path.open()`
                "C417",  # Unnecessary `map()` usage (rewrite using a generator
                # expression)
            ],
        }

        def format_rules(rules: list[str]) -> str:
            return ",".join(rules)

        select_rule = format_rules(self.linting_rules["select"])
        ignore_rule = format_rules(self.linting_rules["ignore"])
        self.linting_args = [
            "--select",
            select_rule,
            "--ignore",
            ignore_rule,
            "--unsafe-fixes",
            # "--fix",
        ]

    def run(self, *args):
        result = subprocess.run(
            [self.ruff_bin_path, *args],
            capture_output=True,  # capture the output and error streams
            text=True,  # return the output as a string
            check=False,  # don't raise an exception if command fails
        )
        if result.returncode == 1:
            return result.stdout
        elif result.returncode != 0:
            raise LinterError(result.stderr)
        return result.stdout

    def format(self, code: str) -> str:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py") as f:
            f.write(code)
            f.flush()
            logger.debug("formatting_file", filename=f.name)
            self.run("format", f.name)
            f.seek(0)
            return f.read()

    def lint(self, code: str) -> str:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py") as f:
            f.write(code)
            f.flush()
            logger.debug("linting_file", file=f.name, args=self.linting_args)
            self.run("check", f.name, *self.linting_args)
            f.seek(0)
            return f.read()
