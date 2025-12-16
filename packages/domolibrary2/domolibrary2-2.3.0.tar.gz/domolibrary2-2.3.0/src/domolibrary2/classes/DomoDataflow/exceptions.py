"""
DomoDataflow Exceptions

Dataflow-specific exception classes.
"""

from ...base.exceptions import ClassError

__all__ = [
    "SearchDataflowNotFoundError",
]


class SearchDataflowNotFoundError(ClassError):
    """Exception raised when dataflow search operations return no results."""

    def __init__(self, cls_instance, search_name: str):
        message = f"No dataflow found matching '{search_name}'"
        super().__init__(cls_instance=cls_instance, message=message)
