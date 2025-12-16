"""
Data Conversion Utilities

This module provides comprehensive utilities for converting between different data formats,
types, and structures. Includes datetime conversions, string formatting, data validation,
and dataframe operations.

Functions:
    # Display utilities
    print_md: Display markdown in Jupyter notebooks

    # Datetime conversions
    convert_epoch_millisecond_to_datetime: Convert epoch milliseconds to datetime
    convert_datetime_to_epoch_millisecond: Convert datetime to epoch milliseconds
    convert_string_to_datetime: Parse string to datetime object

    # Code analysis utilities
    convert_python_to_ast_module: Parse Python code to AST module
    extract_ast_functions: Extract function definitions from AST

    # String formatting utilities
    convert_programming_text_to_title_case: Convert code names to title case
    convert_snake_to_pascal: Convert snake_case to camelCase
    convert_str_to_snake_case: Convert strings to snake_case

    # Validation utilities
    is_valid_email: Validate email format
    convert_string_to_bool: Convert string to boolean

    # Data structure utilities
    concat_list_dataframe: Concatenate list of DataFrames
    merge_dict: Deep merge dictionaries

Exception Classes:
    InvalidEmail: Raised when email validation fails
    ConcatDataframeInvalidElementError: Raised when dataframe concat fails

Example:
    >>> # Datetime conversions
    >>> epoch = convert_datetime_to_epoch_millisecond(datetime.now())
    >>> dt = convert_epoch_millisecond_to_datetime(epoch)

    >>> # String formatting
    >>> title = convert_programming_text_to_title_case("get_user_data")
    >>> # Returns: "Get User Data"

    >>> # Email validation
    >>> try:
    ...     is_valid_email("user@example.com")  # Returns True
    ... except InvalidEmail:
    ...     print("Invalid email")
"""

__all__ = [
    "print_md",
    "convert_epoch_millisecond_to_datetime",
    "convert_datetime_to_epoch_millisecond",
    "convert_string_to_datetime",
    "convert_python_to_ast_module",
    "extract_ast_functions",
    "convert_programming_text_to_title_case",
    "convert_snake_to_pascal",
    "convert_str_to_snake_case",
    "InvalidEmailError",
    "is_valid_email",
    "convert_string_to_bool",
    "ConcatDataframeError",
    "concat_list_dataframe",
    "merge_dict",
]


import ast
import datetime as dt
import re

# Optional dependencies with fallbacks
import pandas as pd
from dateutil import parser as date_parser
from IPython.display import display_markdown

# Import custom exceptions
from .exceptions import ConcatDataframeError, InvalidEmailError


## Legacy exception aliases removed for N818 compliance
def print_md(md_str: str) -> None:
    """
    Display markdown string in Jupyter notebook environment.

    Args:
        md_str (str): Markdown string to display

    Raises:
        ImportError: If IPython is not available

    Example:
        >>> print_md("# Header\\n**Bold text**")

    Note:
        This function only works in Jupyter notebook environments where
        IPython.display is available.
    """
    display_markdown(md_str, raw=True)


def convert_epoch_millisecond_to_datetime(
    epoch: int | None,
) -> dt.datetime | None:
    """
    Convert Epoch time with milliseconds to datetime object.

    Args:
        epoch (int, optional): Epoch time in milliseconds. If None, returns None.

    Returns:
        datetime, optional: Corresponding datetime object, or None if input is None

    Example:
        >>> epoch_time = 1609459200000  # 2021-01-01 00:00:00 UTC
        >>> dt_obj = convert_epoch_millisecond_to_datetime(epoch_time)
        >>> print(dt_obj)  # 2021-01-01 00:00:00
    """
    return dt.datetime.fromtimestamp(epoch / 1000.0) if epoch else None


def convert_datetime_to_epoch_millisecond(
    datetime: dt.datetime | None,
) -> int | None:
    """
    Convert datetime object to Epoch time with milliseconds.

    Args:
        datetime (datetime, optional): Datetime object to convert. If None, returns None.

    Returns:
        int, optional: Epoch time in milliseconds, or None if input is None

    Example:
        >>> import datetime as dt
        >>> dt_obj = dt.datetime(2021, 1, 1)
        >>> epoch = convert_datetime_to_epoch_millisecond(dt_obj)
        >>> print(epoch)  # 1609459200000
    """
    return int(datetime.timestamp() * 1000) if datetime else None


def convert_string_to_datetime(datestr: str | None) -> dt.datetime | None:
    """
    Convert a date string to datetime object using flexible parsing.

    Args:
        datestr (str, optional): Date string to parse. If None or empty, returns None.

    Returns:
        datetime, optional: Parsed datetime object, or None if input is None/empty

    Raises:
        ImportError: If dateutil is not available
        ValueError: If the date string cannot be parsed

    Example:
        >>> dt_obj = convert_string_to_datetime("2021-01-01 12:30:00")
        >>> dt_obj = convert_string_to_datetime("Jan 1, 2021")
        >>> dt_obj = convert_string_to_datetime("2021/01/01")
    """
    if not datestr:
        return None

    return date_parser.parse(datestr)


def convert_python_to_ast_module(
    python_str: str | None = None,
    python_file_path: str | None = None,
    return_str: bool = False,
) -> ast.Module | str:
    """
    Parse Python code string or file and return its AST module.

    Args:
        python_str (str, optional): Python code string to parse
        python_file_path (str, optional): Path to Python file to parse
        return_str (bool): If True, return the source string instead of AST

    Returns:
        ast.Module or str: AST module of the parsed code, or source string if return_str=True

    Raises:
        ValueError: If neither python_str nor python_file_path is provided
        FileNotFoundError: If python_file_path doesn't exist
        SyntaxError: If the Python code has syntax errors

    Example:
        >>> code = "def hello(): return 'world'"
        >>> ast_module = convert_python_to_ast_module(python_str=code)
        >>> functions = extract_ast_functions(ast_module)
    """
    if not python_str and python_file_path:
        try:
            with open(python_file_path, encoding="utf-8") as source:
                python_str = source.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Python file not found: {python_file_path}")

    if not python_str:
        raise ValueError("Must provide either python_str or python_file_path")

    if return_str:
        return python_str

    return ast.parse(python_str)


def extract_ast_functions(ast_module: ast.Module) -> list[ast.FunctionDef]:
    """
    Extract all function definitions from an AST module.

    Args:
        ast_module (ast.Module): AST module to extract functions from

    Returns:
        list[ast.FunctionDef]: list of function definition nodes

    Example:
        >>> code = '''
        ... def func1():
        ...     pass
        ...
        ... class MyClass:
        ...     def method1(self):
        ...         pass
        ...
        ... def func2():
        ...     pass
        ... '''
        >>> ast_module = convert_python_to_ast_module(python_str=code)
        >>> functions = extract_ast_functions(ast_module)
        >>> print(len(functions))  # 2 (only top-level functions)

    Note:
        This only extracts top-level function definitions, not methods
        inside classes.
    """
    return [node for node in ast_module.body if isinstance(node, ast.FunctionDef)]


def convert_programming_text_to_title_case(clean_str: str) -> str:
    """
    Convert function names from programming conventions to human-readable display format.

    Transforms snake_case and camelCase function names into Title Case format suitable
    for user interfaces. Preserves leading underscores as spaces to maintain private
    function indicators.

    Args:
        clean_str (str): The original function name in snake_case or camelCase

    Returns:
        str: The formatted display name in Title Case

    Examples:
        >>> convert_programming_text_to_title_case('getUserData')
        'Get User Data'
        >>> convert_programming_text_to_title_case('calculate_total_sum')
        'Calculate Total Sum'
        >>> convert_programming_text_to_title_case('_private_method')
        ' Private Method'

    Note:
        Leading underscores are converted to spaces to preserve the indication
        that these are private/internal methods.
    """
    leading_underscores = ""
    working_str = clean_str

    # Extract leading underscores and convert to spaces
    while working_str.startswith("_"):
        leading_underscores += " "
        working_str = working_str[1:]

    # Convert camelCase to spaced format
    spaced_name = re.sub(r"([a-z])([A-Z])", r"\1 \2", working_str)
    # Convert snake_case to spaced format
    spaced_name = spaced_name.replace("_", " ")

    # Capitalize each word and join
    return leading_underscores + " ".join(
        word.capitalize() for word in spaced_name.split()
    )


def convert_snake_to_pascal(clean_str: str) -> str:
    """
    Convert snake_case string to camelCase (pascal case with lowercase first letter).

    Args:
        clean_str (str): Snake case string to convert

    Returns:
        str: String in camelCase format

    Example:
        >>> convert_snake_to_pascal('user_name_field')
        'userNameField'
        >>> convert_snake_to_pascal('api_key')
        'apiKey'
    """
    clean_str = clean_str.replace("_", " ").title().replace(" ", "")
    return clean_str[0].lower() + clean_str[1:] if clean_str else ""


def convert_str_to_snake_case(
    text_str: str, is_only_alphanumeric: bool = False, is_pascal: bool = False
) -> str:
    """
    Convert various string formats to snake_case.

    Can handle conversion from PascalCase/camelCase to snake_case, and optionally
    filter to only alphanumeric characters.

    Args:
        text_str (str): String to convert to snake_case
        is_only_alphanumeric (bool): If True, remove non-alphanumeric characters
        is_pascal (bool): If True, treat input as PascalCase/camelCase

    Returns:
        str: String converted to snake_case format

    Example:
        >>> convert_str_to_snake_case('UserNameField', is_pascal=True)
        'user_name_field'
        >>> convert_str_to_snake_case('User Name Field')
        'user_name_field'
        >>> convert_str_to_snake_case('User-Name!Field', is_only_alphanumeric=True)
        'usernamefield'
    """
    if is_pascal:
        # Convert PascalCase/camelCase to snake_case
        text_str = re.sub(r"(?<!^)(?=[A-Z])", "_", text_str)

    # Replace spaces with underscores and convert to lowercase
    text_str = text_str.replace(" ", "_").lower()

    if is_only_alphanumeric:
        # Remove all non-alphanumeric characters
        text_str = re.sub(r"\W+", "", text_str)

    return text_str


def is_valid_email(email: str) -> bool:
    """
    Test if provided string is a valid email format.

    Uses regex pattern matching to validate email format according to
    standard email format requirements.

    Args:
        email (str): Email string to validate

    Returns:
        bool: True if email format is valid

    Raises:
        InvalidEmail: If email format is invalid

    Example:
        >>> is_valid_email("user@example.com")
        True
        >>> is_valid_email("invalid-email")
        InvalidEmail: Invalid email format: "invalid-email"
    """
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

    if re.fullmatch(pattern, email):
        return True
    else:
        raise InvalidEmailError(email=email)


def convert_string_to_bool(v: str | bool) -> bool:
    """
    Convert string representation to boolean value.

    Recognizes common string representations of boolean values and converts
    them to actual boolean type.

    Args:
        v (str or bool): Value to convert to boolean

    Returns:
        bool: Converted boolean value

    Example:
        >>> convert_string_to_bool("yes")
        True
        >>> convert_string_to_bool("false")
        False
        >>> convert_string_to_bool("1")
        True
        >>> convert_string_to_bool(True)
        True
    """
    if isinstance(v, bool):
        return v
    return str(v).lower() in ("yes", "true", "t", "1")


def concat_list_dataframe(df_ls: list[object]) -> object:
    """
    Take a list of DataFrames and concatenate them into one DataFrame.

    Args:
        df_ls (list[Any]): list of pandas DataFrames to concatenate

    Returns:
        Any: Concatenated DataFrame (returns Any due to optional pandas dependency)

    Raises:
        ImportError: If pandas is not available
        ConcatDataframe_InvalidElement: If any element is not a DataFrame

    Example:
        >>> df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
        >>> result = concat_list_dataframe([df1, df2])
        >>> print(len(result))  # 4 rows

    Note:
        Requires pandas to be installed. Uses inner join for concatenation
        and resets the index.
    """
    df = None
    for elem in df_ls:
        if not isinstance(elem, pd.DataFrame):
            raise ConcatDataframeError(elem)

        if len(elem.index) == 0:
            continue

        if df is None:
            df = elem
        else:
            df = pd.concat([df, elem], join="inner").reset_index(drop=True)

    return df


def merge_dict(
    source: dict[str, object], destination: dict[str, object]
) -> dict[str, object]:
    """
    Deep merge source dictionary into destination dictionary.

    Recursively merges nested dictionaries, with source values taking precedence
    over destination values for conflicts.

    Args:
        source (dict[str, Any]): Dictionary to merge from
        destination (dict[str, Any]): Dictionary to merge into (modified in place)

    Returns:
        dict[str, Any]: The merged destination dictionary

    Example:
        >>> dest = {"a": 1, "b": {"c": 2, "d": 3}}
        >>> src = {"b": {"d": 4, "e": 5}, "f": 6}
        >>> result = merge_dict(src, dest)
        >>> print(result)
        # {"a": 1, "b": {"c": 2, "d": 4, "e": 5}, "f": 6}

    Note:
        The destination dictionary is modified in place. For nested dictionaries,
        the merge is recursive.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # Get existing node or create empty dict
            node = destination.setdefault(key, {})
            merge_dict(value, node)
        else:
            destination[key] = value

    return destination
