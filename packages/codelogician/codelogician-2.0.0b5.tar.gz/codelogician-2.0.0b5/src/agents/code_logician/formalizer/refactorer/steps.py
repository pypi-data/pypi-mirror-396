from .utils import FunctionalRefactoringData, RefactoringExample

script_to_program_example1 = RefactoringExample(
    before="""def max_sum(arr):
    curr_sum = max_sum = 0
    for num in arr:
        curr_sum = max(0, curr_sum + num)
        max_sum = max(max_sum, curr_sum)
    return max_sum

n = int(input())
numbers = list(map(int, input().split()))
result = max_sum(numbers)
print(result)""",
    after="""def max_sum(arr):
    curr_sum = max_sum = 0
    for num in arr:
        curr_sum = max(0, curr_sum + num)
        max_sum = max(max_sum, curr_sum)
    return max_sum

def main():
    n = int(input())
    numbers = list(map(int, input().split()))
    result = max_sum(numbers)
    print(result)

if __name__ == "__main__":
    main()""",
)

script_to_program_example2 = RefactoringExample(
    before="""n = int(input("Enter n: "))
primes = []
sieve = [True] * (n + 1)
sieve[0] = sieve[1] = False

for i in range(2, int(n**0.5) + 1):
    if sieve[i]:
        for j in range(i*i, n + 1, i):
            sieve[j] = False

primes = [i for i in range(n + 1) if sieve[i]]
print(f"Found {len(primes)} primes: {primes}")""",
    after="""def get_primes(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    
    return [i for i in range(n + 1) if sieve[i]]

def main():
    n = int(input("Enter n: "))
    primes = get_primes(n)
    print(f"Found {len(primes)} primes: {primes}")

if __name__ == "__main__":
    main()""",
)

# script_to_program_example3 = RefactoringExample(
#     before="""import re

# def count_words(text):
#     words = re.findall(r'\w+', text.lower())
#     freq = {}
#     for word in words:
#         freq[word] = freq.get(word, 0) + 1
#     return freq

# filename = input("Enter filename: ")
# with open(filename, 'r') as f:
#     content = f.read()

# word_counts = count_words(content)
# for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
#     print(f"{word}: {count}")""",
#     after="""import re

# def count_words(text):
#     words = re.findall(r'\w+', text.lower())
#     freq = {}
#     for word in words:
#         freq[word] = freq.get(word, 0) + 1
#     return freq

# def get_top_words(word_counts, n=10):
#     return sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:n]

# def main():
#     filename = input("Enter filename: ")
#     with open(filename, 'r') as f:
#         content = f.read()

#     word_counts = count_words(content)
#     top_words = get_top_words(word_counts)

#     for word, count in top_words:
#         print(f"{word}: {count}")

# if __name__ == "__main__":
#     main()""",
# )


type_hint_refactoring_example = RefactoringExample(
    before="def add(x, y): return x + y",
    after="def add(x: float, y: float) -> float: return x + y",
)

complex_function_refactoring_example = RefactoringExample(
    before="def process_data(data): # 20 lines of complex logic",
    after="""def validate_data(data: Data) -> ValidatedData: ...
def transform_data(data: ValidatedData) -> TransformedData: ...
def aggregate_data(data: TransformedData) -> Result: ...
def process_data(data: Data) -> Result:
    return aggregate_data(transform_data(validate_data(data)))""",
)

function_purification_example = RefactoringExample(
    before="""counter = 0

def increment_and_double(x: int) -> int:
    global counter
    counter += 1
    x += counter
    return x * 2""",
    after="""def increment_and_double(x: int, counter: int) -> tuple[int, int]:
    new_counter = counter + 1
    result = (x + new_counter) * 2
    return result, new_counter""",
)

function_totalization_example = RefactoringExample(
    before="""def get_average(numbers: list[float]) -> float:
    return sum(numbers) / len(numbers)""",
    after="""def get_average(numbers: list[float]) -> float | None:
    if not numbers:
        return None
    return sum(numbers) / len(numbers)""",
)

recursion_transformation_example = RefactoringExample(
    before="""def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result""",
    after="""def factorial(n):
    def helper(result, i):
        if i > n:
            return result
        else:
            return helper(result * i, i + 1)""",
)

stream_processing_example = RefactoringExample(
    before="""result = []
for x in numbers:
    if x > 0:
        result.append(x * 2)""",
    after="""result = list(map(lambda x: x * 2, filter(lambda x: x > 0, numbers)))""",
)

type_system_enhancement_example = RefactoringExample(
    # TODO: improve this example
    before="""class Result:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error""",
    after="""from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar('T')

@dataclass(frozen=True)
class Success(Generic[T]):
    value: T

@dataclass(frozen=True)
class Error:
    message: str

Result = Union[Success[T], Error]""",
)

exhaustive_pattern_matching_example = RefactoringExample(
    before="""def process(x: int) -> str:
    if x > 0:
        return "positive"
    else:
        return "non-positive"
""",
    after="""def process(x: int) -> str:
    match x > 0:
        case True: return "positive"
        case False: return "non-positive"
""",
)

function_composition_example = RefactoringExample(
    before="""def clean_and_split(text: str) -> list[str]:
    text = text.lower()
    text = text.strip()
    words = text.split()
    return [w for w in words if len(w) > 2]""",
    after="""from functools import partial, compose
from typing import Callable

def clean_and_split(text: str) -> list[str]:
    process_text: Callable[[str], list[str]] = compose(
        lambda words: [w for w in words if len(w) > 2],
        str.split,
        str.strip,
        str.lower
    )
    return process_text(text)""",
)

script_to_program_refactoring = FunctionalRefactoringData(
    name="ScriptToProgramRefactoring",
    description=(
        "Transform script-like code with direct I/O operations into a structured "
        "program with a main function and explicit I/O handling"
    ),
    non_functional_patterns=[
        "Top-level I/O operations (print, input)",
        "Global state and variables",
        "Direct execution flow without a main function",
        "Mixing I/O with computation logic",
        "Lack of clear program entry point",
    ],
    desired_patterns=[
        "All I/O operations contained within main function",
        "Pure computational logic separated from I/O operations",
        "Clear program structure with entry point",
        "Explicit passing of inputs and outputs",
        "No global state modifications outside main",
        "Use of __name__ == '__main__' guard for entry point",
    ],
    reference_transformation_steps=[
        "Keep existing pure functions unchanged",
        "Move script logic into a solve function",
        "Create a main function for I/O operations",
        "Ensure data flows explicitly through function parameters",
        "Add proper if __name__ == '__main__' guard",
    ],
    example=[
        script_to_program_example1,
        script_to_program_example2,
        # script_to_program_example3,
    ],
)

type_hint_refactoring = FunctionalRefactoringData(
    name="TypeHintRefactoring",
    description=(
        "Add type hints to function arguments and return values. "
        "MUST be used for untyped Python code."
    ),
    non_functional_patterns=[
        "Missing type hints for function arguments",
        "Missing return type hint",
        "Unclear nullable type annotations",
    ],
    desired_patterns=[
        "All function arguments must have type hints",
        "Return type must be specified",
        "Nullable types should use union syntax (e.g. str | None)",
    ],
    reference_transformation_steps=[
        "Identify all function definitions",
        "Add type hints for each function parameter",
        "Add return type annotations",
        "Use union syntax (Type | None) for nullable types",
        (
            "Use modern type hint syntax (PEP 585) for generic types (e.g. `list[str]` "
            "instead of `List[str]`), union types (PEP 604) for type alternatives "
            "(e.g. `int | str` instead of `Union[int, str]`), and optional types "
            "(e.g. `str | None` instead of `Optional[str]`), unless: there is python "
            "version specified. (support Python < 3.9 for generic types, < 3.10 for "
            "union types)"
        ),
    ],
    example=[type_hint_refactoring_example],
)

complex_function_refactoring = FunctionalRefactoringData(
    name="ComplexFunctionRefactoring",
    description=(
        "For a large, complex function, extract multiple smaller, more focused \
        functions from its body. The original function name and the order and default \
        values of parameters must be preserved (type hints are allowed to be changed)."
    ),
    non_functional_patterns=[
        "Functions with unclear data flow between operations",
        "Functions with high cyclomatic complexity (many branches/loops)",
        "Functions with multiple levels of nesting",
        "Functions with multiple responsibilities",
        "Functions with multiple return points",
        "Functions that use many local variables",
        "Functions longer than 20 lines (except for the main function)",
    ],
    desired_patterns=[
        "Clear data flow between functions",
        "Each function should have a single responsibility",
        "Function names should clearly describe their operation",
        "Keep original function as composition of smaller functions",
        (
            "Local variables needed by multiple extracted functions should become "
            "parameters"
        ),
        "Maintain the same overall behavior",
        "Maximum function length of 20 lines (except for the main function)",
    ],
    reference_transformation_steps=[
        "Identify distinct logical operations in the complex function",
        "Extract each operation into a pure function with explicit inputs/outputs",
        "Create meaningful names that describe each function's purpose",
        "Compose the extracted functions in the body of the original function",
    ],
    example=[complex_function_refactoring_example],
)

function_purification_refactoring = FunctionalRefactoringData(
    name="FunctionPurificationRefactoring",
    description=(
        "Transform functions to be pure by making all dependencies explicit and \
            removing side effects."
    ),
    non_functional_patterns=[
        "Functions that modify input parameters",
        "Functions that access global state",
        "Functions with side effects (I/O, logging, etc.)",
        "Functions that depend on external state",
        "Functions that modify shared/external state",
        "Functions with non-deterministic behavior",
    ],
    desired_patterns=[
        "All dependencies must be passed as parameters",
        "No modification of input parameters",
        "No global state access",
        "Return new values instead of modifying existing ones",
        "Function output should only depend on inputs",
    ],
    reference_transformation_steps=[
        "Make all dependencies explicit as parameters",
        "Replace global state access with parameters",
        "Create new objects instead of modifying existing ones",
        "Return multiple values if needed instead of having side effects",
        "Ensure consistent output for same inputs",
    ],
    example=[function_purification_example],
)

function_totalization_refactoring = FunctionalRefactoringData(
    name="FunctionTotalizationRefactoring",
    description=(
        "Convert partial functions (those that may fail for certain inputs) into total \
functions that handle all possible inputs explicitly."
    ),
    non_functional_patterns=[
        "Dictionary access without .get() or key checking",
        "List indexing without bounds checking",
        "Division operations without zero checks",
        "Type-dependent operations without type checking",
        "Uncaught exceptions in function bodies",
        "Other operations that may fail for certain inputs",
    ],
    desired_patterns=[
        "All potential failure points must be explicitly handled",
        "Use Option/Maybe pattern for potentially missing values",
        "Prefer returning values (default values, None, or other sentinel values) over \
raising exceptions",
        "Preconditions are documented in type hints and docstrings",
    ],
    reference_transformation_steps=[
        "Identify potential failure points in the function",
        "Add explicit checks for each failure condition",
        "Modify return type to include None/Optional where appropriate",
        "Add error handling for unavoidable exceptions",
        "Document preconditions in type hints and docstrings",
    ],
    example=[function_totalization_example],
)

recursion_transformation_refactoring = FunctionalRefactoringData(
    name="RecursionTransformationRefactoring",
    description=(
        "Convert imperative loops into recursive functions with clear base cases and \
recursive steps."
    ),
    non_functional_patterns=[
        "For loops with accumulation",
        "While loops",
        "Nested loops",
        "Loops with multiple exit conditions",
        "Loops with state mutations",
    ],
    desired_patterns=[
        "Clear base case and recursive case",
        "Tail recursion where possible",
        "No mutable state in recursive calls",
        "Each recursive call must move toward base case",
    ],
    reference_transformation_steps=[
        "Identify loop invariants and accumulator variables",
        "Define helper function with accumulator parameter",
        "Convert loop body to recursive case",
        "Define base case from loop termination condition",
    ],
    example=[recursion_transformation_example],
)

stream_processing_refactoring = FunctionalRefactoringData(
    name="StreamProcessingRefactoring",
    description=(
        "Convert iterative data processing into stream operations using higher-order \
functions."
    ),
    non_functional_patterns=[
        "Loops for data transformation",
        "Filtering operations in loops",
        "Accumulation operations",
        "Multiple passes over data",
        "Nested loops for data processing",
    ],
    desired_patterns=[
        "Use map/filter/reduce operations",
        "Compose operations with function pipelines",
        "Lazy evaluation where possible",
        "No side effects in stream operations",
    ],
    reference_transformation_steps=[
        "Identify data processing patterns",
        "Convert loops to stream operations",
        "Use map/filter/reduce operations",
        "Compose operations with function pipelines",
        "Prefer lazy evaluation",
        "Avoid side effects in stream operations",
    ],
    example=[stream_processing_example],
)

type_system_enhancement_refactoring = FunctionalRefactoringData(
    name="TypeSystemEnhancementRefactoring",
    description=(
        "Enhance Python's type system to more closely align with OCaml's algebraic \
data types (ADTs) and advanced type features."
    ),
    non_functional_patterns=[
        "Classes used primarily for data storage",
        "Inheritance hierarchies",
        "Union types without clear sum type structure",
        "Generic types without constraints",
        "Classes with mixed data and behavior",
        "Enums that could be ADTs",
        "Type aliases that could be more specific",
    ],
    desired_patterns=[
        "Each type should be either a product type (record) or sum type (variant)",
        "No inheritance (favor composition)",
        "All type parameters must be explicit and constrained",
        "Types should be as specific as possible",
        "Pattern matching should be exhaustive over ADTs",
    ],
    reference_transformation_steps=[
        "Convert classes to immutable dataclasses or NamedTuples",
        "Replace inheritance with tagged unions",
        "Make type parameters explicit and bounded",
        "Add literal types for discriminated unions",
        "Ensure all types are properly constrained",
    ],
    example=[type_system_enhancement_example],
)

exhaustive_pattern_matching_refactoring = FunctionalRefactoringData(
    name="ExhaustivePatternMatchingRefactoring",
    description=(
        "Transform conditional logic into exhaustive pattern matching that can be \
statically verified."
    ),
    non_functional_patterns=[
        "If-elif chains",
        "Type checking with isinstance",
        "Dictionary-based dispatch",
        "Try-except blocks for control flow",
        "Switch-case statements",
        "Object-oriented polymorphism",
    ],
    desired_patterns=[
        "All patterns must be exhaustive",
        "Pattern order must be unambiguous",
        "No fallthrough between patterns",
        "Guard conditions should be pure",
        "Type narrowing must be explicit",
    ],
    reference_transformation_steps=[
        "Identify all possible input types and patterns",
        "Define explicit union types for inputs",
        "Convert conditionals to match statements",
        "Add exhaustiveness checking",
        "Make guard conditions explicit and pure",
    ],
    example=[exhaustive_pattern_matching_example],
)

function_composition_refactoring = FunctionalRefactoringData(
    name="FunctionCompositionRefactoring",
    description=(
        "Transform sequential data transformations into elegant function compositions "
        "that clearly express data flow."
    ),
    non_functional_patterns=[
        "Excessive reassignment of the same variable for sequential transformations",
        "Clear data pipelines with 4+ steps implemented as separate statements",
        "Deeply nested function calls that obscure the transformation sequence",
        "Linear data transformations that could be more clearly expressed as "
        "compositions",
    ],
    desired_patterns=[
        "Clean data flow expressed through function composition",
        "Elimination of unnecessary intermediate variables",
        "Named function compositions that clearly express intent",
        "Type annotations that reinforce the composition flow",
    ],
    reference_transformation_steps=[
        "Identify clear data transformation sequences",
        "Extract pure functions for each transformation step",
        "Use method chaining or functional composition techniques where appropriate",
        "Name composed functions to express high-level operations",
    ],
    # example=[function_composition_example],
    example=[],
)


functional_refactorings: list[FunctionalRefactoringData] = [
    script_to_program_refactoring,
    type_hint_refactoring,
    complex_function_refactoring,
    function_purification_refactoring,
    function_totalization_refactoring,
    function_composition_refactoring,
    recursion_transformation_refactoring,
    stream_processing_refactoring,
    type_system_enhancement_refactoring,
    exhaustive_pattern_matching_refactoring,
]
