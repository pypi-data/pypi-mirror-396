"""
Datacenter Route Exception Classes

This module contains all exception classes used by datacenter route functions.

Exception Classes:
    SearchDatacenter_NoResultsFound: Raised when datacenter search returns no results
    Datacenter_GET_Error: Raised when datacenter retrieval operations fail
    ShareResource_Error: Raised when resource sharing operations fail
"""

from ...base.exceptions import RouteError


class SearchDatacenterNoResultsFoundError(RouteError):
    """Raised when datacenter search operations return no results."""

    def __init__(self, res=None, message: str | None = None, **kwargs):
        super().__init__(
            res=res,
            entity_id=(
                getattr(getattr(res, "auth", None), "domo_instance", None)
                if res
                else None
            ),
            message=message or "No results for query parameters",
            **kwargs,
        )


class DatacenterGetError(RouteError):
    """Raised when datacenter retrieval operations fail."""

    def __init__(self, res=None, message: str | None = None, **kwargs):
        super().__init__(
            res=res,
            entity_id=(
                getattr(getattr(res, "auth", None), "domo_instance", None)
                if res
                else None
            ),
            message=message or "Datacenter retrieval failed",
            **kwargs,
        )


class ShareResourceError(RouteError):
    """Raised when resource sharing operations fail."""

    def __init__(
        self,
        message: str | None = None,
        domo_instance: str | None = None,
        parent_class: str | None = None,
        function_name: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or "Resource sharing operation failed",
            domo_instance=domo_instance,
            parent_class=parent_class,
            function_name=function_name,
            res=res,
            **kwargs,
        )
