"""Page-related exception classes."""

__all__ = ["DomoPage_GetRecursive", "Page_NoAccess"]

from ...auth import DomoAuth
from ...base import exceptions as dmde


class DomoPage_GetRecursive(dmde.ClassError):
    def __init__(
        self,
        cls,
        entity_id,
        auth: DomoAuth,
        include_recursive_children,
        include_recursive_parents,
    ):
        super().__init__(
            auth=auth,
            cls=cls,
            entity_id=entity_id,
            message=f"can only trace parents OR children recursively but not both. include_recursive_children : {include_recursive_children}, include_recursive_parents: {include_recursive_parents}",
        )


class Page_NoAccess(dmde.ClassError):
    def __init__(self, page_id, page_title, domo_instance, function_name, parent_class):
        super().__init__(
            function_name=function_name,
            parent_class=parent_class,
            domo_instance=domo_instance,
            message=f'authenticated user doesn\'t have access to {page_id} - "{page_title}" contact owners to share access',
        )
