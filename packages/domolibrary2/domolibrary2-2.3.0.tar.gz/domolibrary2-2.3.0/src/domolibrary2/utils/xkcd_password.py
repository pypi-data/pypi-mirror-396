"""
XKCD-Style Password Generation Utilities

This module provides utilities for generating secure, memorable passwords
using the XKCD approach of combining random words. Includes various
customization options and processing functions.

Constants:
    LEET: Dictionary mapping characters to leet speak equivalents
    PADDING: String of padding characters for password enhancement

Functions:
    add_leet_to_string: Apply leet speak transformations to text
    add_padding_characters_fn: Add random padding characters
    process_add_leet: Process password with leet speak
    process_pad_suffix_fn: Add padding suffix to password
    process_random_capitalization_fn: Apply random capitalization
    process_first_capitalization_fn: Capitalize first word only
    process_caps_first_word_add_year_and_add_suffix: Comprehensive processing
    generate_xkcd_password: Generate basic XKCD-style password
    process_domo_password_fn: Specific processing for Domo-style passwords
    generate_domo_password: Generate Domo-style password

Example:
    >>> # Generate basic XKCD password
    >>> password = generate_xkcd_password()
    >>> print(password)  # "word1-word2-word3"

    >>> # Generate Domo-style password
    >>> password = generate_domo_password()
    >>> print(password)  # "Word1-word2-word32024!"

    >>> # Custom processing
    >>> password = generate_xkcd_password()
    >>> leet_password, _ = process_add_leet(password)
    >>> final_password, _ = process_pad_suffix_fn(leet_password)
"""

__all__ = [
    "LEET",
    "PADDING",
    "add_leet_to_string",
    "add_padding_characters_fn",
    "process_add_leet",
    "process_pad_suffix_fn",
    "process_random_capitalization_fn",
    "process_first_capitalization_fn",
    "process_caps_first_word_add_year_and_add_suffix",
    "generate_xkcd_password",
    "process_domo_password_fn",
    "generate_domo_password",
]

import datetime as dt
import random
from collections.abc import Callable

# Optional dependency with fallback
try:
    from xkcdpass import xkcd_password as xp

    _XKCDPASS_AVAILABLE = True
except ImportError:
    xp = None
    _XKCDPASS_AVAILABLE = False

# Leet speak character mappings
LEET = {"a": "@", "i": "!", "A": "@", "I": "!", "e": "3", "E": "3"}

# Padding characters for password enhancement
PADDING = ".!?"


def add_leet_to_string(text: str, leet: dict | None = None) -> str:
    """
    Apply leet speak transformations to text.

    Replaces characters in the text with their leet speak equivalents
    based on the provided mapping dictionary.

    Args:
        text (str): Text to transform
        leet (dict, optional): Character mapping. Defaults to global LEET constant.

    Returns:
        str: Text with leet speak transformations applied

    Example:
        >>> add_leet_to_string("hello")
        'h3llo'
        >>> add_leet_to_string("AMAZING")
        '@M@Z!NG'
    """
    if leet is None:
        leet = LEET
    return "".join(leet.get(char, char) for char in text)


def add_padding_characters_fn(
    text: str,
    padding: str | None = None,
    n: int = 1,
) -> str:
    """
    Add random padding characters to the end of text.

    Args:
        text (str): Text to add padding to
        padding (str, optional): Characters to choose from. Defaults to global PADDING.
        n (int): Number of padding characters to add (default: 1)

    Returns:
        str: Text with random padding characters appended

    Example:
        >>> add_padding_characters_fn("password")
        'password!'  # or 'password.' or 'password?'
        >>> add_padding_characters_fn("test", n=3)
        'test!?.'  # random combination
    """
    if padding is None:
        padding = PADDING
    text += "".join(random.choices(padding, k=n))
    return text


def process_add_leet(my_pass: str, **kwargs) -> tuple[str, bool]:
    """
    Process password to add leet speak if applicable characters are present.

    Args:
        my_pass (str): Password to process
        **kwargs: Additional keyword arguments (unused but maintains interface)

    Returns:
        Tuple[str, bool]: (processed_password, should_continue_loop)

    Example:
        >>> password, continue_loop = process_add_leet("hello")
        >>> print(password)  # "h3llo"
        >>> print(continue_loop)  # False

        >>> password, continue_loop = process_add_leet("xyz")
        >>> print(password)  # "xyz" (no leet characters)
        >>> print(continue_loop)  # True (continue processing)
    """
    leet = LEET
    keep_loop = False

    # Check if any characters can be converted to leet
    if not any(char in leet.keys() for char in my_pass):
        keep_loop = True
        return my_pass, keep_loop

    my_pass = add_leet_to_string(my_pass, leet=leet)
    return my_pass, keep_loop


def process_pad_suffix_fn(my_pass: str) -> tuple[str, bool]:
    """
    Add padding suffix to password.

    Args:
        my_pass (str): Password to add padding to

    Returns:
        Tuple[str, bool]: (password_with_padding, False)

    Example:
        >>> password, _ = process_pad_suffix_fn("mypassword")
        >>> print(password)  # "mypassword!" (or . or ?)
    """
    return add_padding_characters_fn(my_pass, padding=PADDING, n=1), False


def process_random_capitalization_fn(
    text: str, delimiter: str, **kwargs
) -> tuple[str, bool]:
    """
    Apply random capitalization to words separated by delimiter.

    Args:
        text (str): Text to process
        delimiter (str): Character separating words
        **kwargs: Additional keyword arguments (unused)

    Returns:
        Tuple[str, bool]: (processed_text, False)

    Example:
        >>> text, _ = process_random_capitalization_fn("word1-word2-word3", "-")
        >>> print(text)  # "WORD1-word2-WORD3" (random pattern)
    """
    if delimiter not in text:
        return text, False

    word_ls = text.split(delimiter)
    word_ls = [random.choice((str.upper, str.lower))(word) for word in word_ls]

    return delimiter.join(word_ls), False


def process_first_capitalization_fn(
    text: str, delimiter: str, **kwargs
) -> tuple[str, bool]:
    """
    Capitalize only the first word, lowercase the rest.

    Args:
        text (str): Text to process
        delimiter (str): Character separating words
        **kwargs: Additional keyword arguments (unused)

    Returns:
        Tuple[str, bool]: (processed_text, False)

    Example:
        >>> text, _ = process_first_capitalization_fn("WORD1-WORD2-WORD3", "-")
        >>> print(text)  # "WORD1-word2-word3"
    """
    if delimiter not in text:
        return text, False

    word_ls = text.split(delimiter)
    word_ls = [
        word.upper() if idx == 0 else word.lower() for idx, word in enumerate(word_ls)
    ]

    return delimiter.join(word_ls), False


def process_caps_first_word_add_year_and_add_suffix(
    my_pass: str, delimiter: str, **kwargs
) -> tuple[str, bool]:
    """
    Comprehensive password processing: capitalize first word, add year, add padding.

    Args:
        my_pass (str): Password to process
        delimiter (str): Character separating words
        **kwargs: Additional keyword arguments (unused)

    Returns:
        Tuple[str, bool]: (processed_password, False)

    Example:
        >>> password, _ = process_caps_first_word_add_year_and_add_suffix("word1-word2-word3", "-")
        >>> print(password)  # "WORD1-word2-word32024!" (current year)
    """
    word_ls = my_pass.split(delimiter)
    word_ls[0] = word_ls[0].upper()
    my_pass = delimiter.join(word_ls)

    my_pass += dt.date.today().strftime("%Y")
    my_pass, keep_loop = process_pad_suffix_fn(my_pass)

    return my_pass, keep_loop


def generate_xkcd_password(
    min_word_length: int = 5,
    max_word_length: int = 6,
    valid_chars: str = "[a-z]",
    delimiter: str = "-",
) -> str:
    """
    Generate a basic XKCD-style password using random words.

    Args:
        min_word_length (int): Minimum length of words to use (default: 5)
        max_word_length (int): Maximum length of words to use (default: 6)
        valid_chars (str): Regex pattern for valid characters (default: "[a-z]")
        delimiter (str): Character to separate words (default: "-")

    Returns:
        str: Generated XKCD-style password

    Raises:
        ImportError: If xkcdpass package is not available

    Example:
        >>> password = generate_xkcd_password()
        >>> print(password)  # "horse-battery-staple"

        >>> password = generate_xkcd_password(delimiter="_", min_word_length=4)
        >>> print(password)  # "word_pass_code"
    """
    if not _XKCDPASS_AVAILABLE or xp is None:
        raise ImportError(
            "xkcdpass package is required for password generation. "
            "Install with: pip install xkcdpass"
        )

    wordfile = xp.locate_wordfile()
    mywords = xp.generate_wordlist(
        wordfile=wordfile,
        min_length=min_word_length,
        max_length=max_word_length,
        valid_chars=valid_chars,
    )
    return xp.generate_xkcdpassword(mywords, numwords=3, delimiter=delimiter)


def process_domo_password_fn(my_pass: str, delimiter: str) -> tuple[str, bool]:
    """
    Process password using Domo-specific rules.

    Applies first word capitalization, adds current year, and adds padding.

    Args:
        my_pass (str): Password to process
        delimiter (str): Character separating words

    Returns:
        Tuple[str, bool]: (processed_password, False)

    Example:
        >>> password, _ = process_domo_password_fn("word1-word2-word3", "-")
        >>> print(password)  # "WORD1-word2-word32024!"
    """
    my_pass, keep_loop = process_first_capitalization_fn(my_pass, delimiter)
    my_pass += dt.date.today().strftime("%Y")
    my_pass, keep_loop = process_pad_suffix_fn(my_pass)

    return my_pass, keep_loop


def generate_domo_password(
    delimiter: str = "-", process_fn: Callable | None = None
) -> str:
    """
    Generate a Domo-style password with specific formatting rules.

    Creates an XKCD-style password and applies Domo-specific processing
    including capitalization, year addition, and padding.

    Args:
        delimiter (str): Character to separate words (default: "-")
        process_fn (Callable, optional): Custom processing function.
                                       Defaults to process_domo_password_fn.

    Returns:
        str: Generated Domo-style password

    Raises:
        ImportError: If xkcdpass package is not available

    Example:
        >>> password = generate_domo_password()
        >>> print(password)  # "HORSE-battery-staple2024!"

        >>> # Custom processing
        >>> def custom_process(pwd, delim):
        ...     return pwd.upper() + "123", False
        >>> password = generate_domo_password(process_fn=custom_process)
        >>> print(password)  # "HORSE-BATTERY-STAPLE123"
    """
    if not _XKCDPASS_AVAILABLE or xp is None:
        raise ImportError(
            "xkcdpass package is required for password generation. "
            "Install with: pip install xkcdpass"
        )

    # Use default Domo processing if none provided
    process_fn = process_fn or process_domo_password_fn

    wordfile = xp.locate_wordfile()
    mywords = xp.generate_wordlist(
        wordfile=wordfile, min_length=5, max_length=6, valid_chars="[a-z]"
    )

    my_pass = ""
    keep_loop = True

    while keep_loop:
        my_pass = xp.generate_xkcdpassword(mywords, numwords=3, delimiter=delimiter)
        keep_loop = False

        if process_fn:
            my_pass, keep_loop = process_fn(my_pass=my_pass, delimiter=delimiter)

    return my_pass
