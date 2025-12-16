"""
Dictionary Dot Notation Access

This module provides utilities for accessing dictionary data using dot notation,
making it easier to work with nested dictionary structures.

Classes:
    DictDot: A utility class that converts dictionaries to objects with dot notation access

Functions:
    split_str_to_obj: Convert pipe-separated strings to DictDot objects

Example:
    >>> data = {"user": {"name": "John", "details": {"age": 30}}}
    >>> obj = DictDot(data)
    >>> print(obj.user.name)  # "John"
    >>> print(obj.user.details.age)  # 30

    >>> # Graceful handling of missing attributes
    >>> print(obj.user.missing_field)  # None

    >>> # Convert pipe-separated data
    >>> creds = split_str_to_obj(
    ...     "instance|user@example.com|password",
    ...     ["domo_instance", "username", "password"]
    ... )
    >>> print(creds.domo_instance)  # "instance"
"""

__all__ = ["DictDot", "split_str_to_obj"]

from types import SimpleNamespace


class DictDot(SimpleNamespace):
    """
    A utility class that converts dictionaries to objects supporting dot notation access.

    This class recursively converts nested dictionaries and lists to enable
    convenient dot notation access to nested data structures. Missing attributes
    return None instead of raising AttributeError.

    Args:
        dictionary (dict[str, Any]): Dictionary to convert to dot notation object
        **kwargs: Additional keyword arguments passed to SimpleNamespace

    Attributes:
        All keys from the input dictionary become attributes accessible via dot notation

    Example:
        >>> data = {
        ...     "user": {
        ...         "name": "John Doe",
        ...         "preferences": {
        ...             "theme": "dark",
        ...             "notifications": True
        ...         }
        ...     },
        ...     "posts": [
        ...         {"title": "Post 1", "likes": 10},
        ...         {"title": "Post 2", "likes": 5}
        ...     ]
        ... }
        >>> obj = DictDot(data)
        >>> print(obj.user.name)  # "John Doe"
        >>> print(obj.user.preferences.theme)  # "dark"
        >>> print(obj.posts[0].title)  # "Post 1"
        >>> print(obj.user.missing)  # None (no AttributeError)

    Note:
        - Nested dictionaries are recursively converted to DictDot objects
        - Lists containing dictionaries have their dict elements converted to DictDot
        - Non-dictionary values are preserved as-is
        - Missing attributes return None instead of raising exceptions
    """

    def __init__(self, dictionary: dict[str, object], **kwargs):
        super().__init__(**kwargs)

        for key, value in dictionary.items():
            if isinstance(value, dict):
                # Recursively convert nested dictionaries
                self.__setattr__(key, DictDot(value))
            elif isinstance(value, list):
                # Convert list items that are dictionaries
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        new_list.append(DictDot(item))
                    else:
                        new_list.append(item)
                self.__setattr__(key, new_list)
            else:
                # Store primitive values directly
                self.__setattr__(key, value)

    def __getattr__(self, item: str) -> object:
        """
        Return None for missing attributes instead of raising AttributeError.

        Args:
            item (str): Attribute name being accessed

        Returns:
            Any: None for missing attributes

        Note:
            This method is only called when the attribute doesn't exist,
            providing graceful handling of missing data.
        """
        return None

    def to_dict(self) -> dict[str, object]:
        """
        Convert the DictDot object back to a regular dictionary.

        Returns:
            dict[str, Any]: Regular dictionary representation

        Example:
            >>> obj = DictDot({"user": {"name": "John"}})
            >>> original = obj.to_dict()
            >>> print(original)  # {"user": {"name": "John"}}
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, DictDot):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if isinstance(item, DictDot) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def get(self, key: str, default: object = None) -> object:
        """
        Get an attribute value with a default fallback.

        Args:
            key (str): Attribute name to retrieve
            default (Any): Default value if attribute doesn't exist

        Returns:
            Any: Attribute value or default

        Example:
            >>> obj = DictDot({"name": "John"})
            >>> print(obj.get("name"))  # "John"
            >>> print(obj.get("age", 25))  # 25
        """
        return getattr(self, key, default)


def split_str_to_obj(piped_str: str, key_ls: list[str]) -> DictDot:
    """
    Convert a pipe-separated string to a DictDot object with specified keys.

    Takes a string with pipe-separated values and converts it to a DictDot object
    using the provided list of keys. Useful for parsing configuration strings
    or credential strings.

    Args:
        piped_str (str): Pipe-separated string to parse
        key_ls (list[str]): list of keys to assign to each value

    Returns:
        DictDot: Object with keys from key_ls and values from piped_str

    Raises:
        ValueError: If the number of values doesn't match the number of keys

    Example:
        >>> creds_str = "test_instance|myemail@example.com|sample_password"
        >>> keys = ["domo_instance", "domo_username", "domo_password"]
        >>> creds = split_str_to_obj(creds_str, keys)
        >>> print(creds.domo_instance)  # "test_instance"
        >>> print(creds.domo_username)  # "myemail@example.com"
        >>> print(creds.domo_password)  # "sample_password"

        >>> # Convert back to dictionary if needed
        >>> creds_dict = creds.to_dict()
        >>> print(creds_dict)
        # {
        #     "domo_instance": "test_instance",
        #     "domo_username": "myemail@example.com",
        #     "domo_password": "sample_password"
        # }
    """
    str_ls = piped_str.split("|")

    if len(str_ls) != len(key_ls):
        raise ValueError(
            f"Number of values ({len(str_ls)}) doesn't match number of keys ({len(key_ls)}). "
            f"Values: {str_ls}, Keys: {key_ls}"
        )

    obj_dict = dict(zip(key_ls, str_ls))
    return DictDot(obj_dict)
