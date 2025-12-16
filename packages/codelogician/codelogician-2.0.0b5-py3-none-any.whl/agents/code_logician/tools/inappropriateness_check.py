import ast

from langsmith import traceable

from utils.fdb.fdb import FDB


def check_function_usage(code_string: str, package_path: str) -> bool:
    """
    Check if a specific attribute path is used in the given code string.
    """
    try:
        tree = ast.parse(code_string)
        path_parts = package_path.split(".")

        class AttributeVisitor(ast.NodeVisitor):
            def __init__(self):
                self.found = False
                self.direct_imports = {}  # Maps names to their original paths

            def visit_Import(self, node):
                # Handle: import sys as s
                for alias in node.names:
                    imported_name = alias.name.split(".")
                    alias_name = alias.asname or alias.name
                    self.direct_imports[alias_name] = imported_name

            def visit_ImportFrom(self, node):
                # Handle: from sys import float_info as fi
                if node.module:
                    module_parts = node.module.split(".")
                    for alias in node.names:
                        imported_name = alias.name
                        alias_name = alias.asname or alias.name
                        self.direct_imports[alias_name] = [*module_parts, imported_name]

            def check_path_match(self, parts):
                return parts == path_parts

            def visit_Name(self, node):
                # Check for direct name matches (from imports)
                if node.id in self.direct_imports:
                    imported_path = self.direct_imports[node.id]
                    if self.check_path_match(imported_path):
                        self.found = True

            def visit_Attribute(self, node):
                parts = []
                current = node

                # Build the path from right to left
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value

                if isinstance(current, ast.Name):
                    base_name = current.id
                    if base_name in self.direct_imports:
                        # If the base is an import, use its full path
                        full_path = self.direct_imports[base_name] + list(
                            reversed(parts)
                        )
                        if self.check_path_match(full_path):
                            self.found = True
                    else:
                        # Direct attribute access
                        full_path = [base_name, *reversed(parts)]
                        if self.check_path_match(full_path):
                            self.found = True

        visitor = AttributeVisitor()
        visitor.visit(tree)
        return visitor.found

    except SyntaxError as e:
        print(f"Error: Invalid Python code - {e!s}")
        return False


@traceable
async def find_missing_func(
    fdb: FDB,
    src_code: str,
    src_lang: str,
) -> list[FDB.MissingFunc]:
    """
    Find inappropriate functions/operators in source code that are not supported by
    Imandra.

    Args:
        fdb: Formalism database instance
        src_code: Source code to analyze
        src_lang: Source code language

    Returns:
        List of inappropriate function/operator names found in the source code

    Example:
        >>> src_code = "def foo(x): return x ^ 2 + math.sqrt(x)"
        >>> missing_func = find_missing_func(fdb, src_code, "python")
        >>> for mf in missing_func:
            print(mf['src_code'])
        int.__xor__
        math.sqrt
    """
    if src_lang.lower() != "python":
        return []
    all_missing_func: list[FDB.MissingFunc] = await fdb.get_all_missing_func()

    # TODO: this should be retrieved from the database
    operator_override = {
        "int.__xor__": "^",
    }

    # Filter missing func
    missing_func: list[FDB.MissingFunc] = []
    for mf in all_missing_func:
        mf_in_src: str = mf.src_code
        if operator := operator_override.get(mf_in_src):
            if operator in src_code:
                missing_func.append(mf)
        else:
            if check_function_usage(src_code, mf_in_src):
                missing_func.append(mf)
    return missing_func


if __name__ == "__main__":
    # Test cases
    test_cases = [
        # Direct usage
        "import sys\nx = sys.float_info.max",
        # Using alias
        "import sys as s\nx = s.float_info.max",
        # From import
        "from sys import float_info\nx = float_info.max",
        # From import with alias
        "from sys import float_info as fi\nx = fi.max",
        # Nested from import
        "from sys.float_info import max\nx = max",
        # Nested from import with alias
        "from sys.float_info import max as maximum\nx = maximum",
        # No usage
        "import sys\nx = sys.float_info.min",
        # Different attribute
        "import math\nx = math.sqrt(16)",
    ]

    print("Testing sys.float_info.max:")
    for i, code in enumerate(test_cases, 1):
        result = check_function_usage(code, "sys.float_info.max")
        print(f"Test case {i}: {result}")

    print("\nTesting math.sqrt:")
    for i, code in enumerate(test_cases, 1):
        result = check_function_usage(code, "math.sqrt")
        print(f"Test case {i}: {result}")
