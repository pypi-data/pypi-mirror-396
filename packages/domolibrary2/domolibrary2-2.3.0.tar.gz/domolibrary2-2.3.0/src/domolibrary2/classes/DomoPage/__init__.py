"""Page classes and functionality.

This module provides comprehensive page management functionality for Domo pages,
organized into focused submodules:

- exceptions: Page-related exception classes
- core: Main DomoPage entity classes with basic operations (DomoPage_Default, FederatedDomoPage, DomoPublishPage, DomoPage factory)
- pages: DomoPages collection and hierarchy operations
- access: Access control and sharing functionality
- content: Content management and data operations

Classes:
    DomoPage: Factory class that returns appropriate page type
    DomoPage_Default: Default page implementation
    FederatedDomoPage: Federated page implementation
    DomoPublishPage: Published page with subscription support
    DomoPages: Collection class for managing multiple pages
    DomoPage_GetRecursive: Exception for recursive operation conflicts
    Page_NoAccess: Exception for page access denial

Example:
    Basic page usage:

        >>> from domolibrary2.classes.DomoPage import DomoPage
        >>> page = await DomoPage.get_by_id(page_id="123", auth=auth)
        >>> print(page.display_url)

    Check if page is published:

        >>> page = await DomoPage.get_by_id(page_id="123", auth=auth, check_if_published=True)
        >>> if isinstance(page, DomoPublishPage):
        >>>     subscription = await page.get_subscription(parent_auth_retrieval_fn=get_auth)

    Managing page collections:

        >>> from domolibrary2.classes.DomoPage import DomoPages
        >>> pages = await DomoPages(auth=auth).get()
        >>> print(f"Found {len(pages)} pages")

    Access control:

        >>> access_info = await page.get_accesslist()
        >>> await page.share(domo_users=[user1, user2])
"""

__all__ = [
    "DomoPage_GetRecursive",
    "DomoPage",
    "DomoPage_Default",
    "FederatedDomoPage",
    "DomoPublishPage",
    "DomoPages",
    "Page_NoAccess",
    "access",
    "content",
]

# Import and attach functionality modules
from . import access, content

# Import core classes
from .core import DomoPage, DomoPage_Default, DomoPublishPage, FederatedDomoPage

# Import exceptions
from .exceptions import DomoPage_GetRecursive, Page_NoAccess
from .pages import DomoPages

# Attach methods to DomoPage_Default class (all page types inherit from it)
DomoPage_Default.test_page_access = access.test_page_access
DomoPage_Default.get_accesslist = access.get_accesslist
DomoPage_Default.share = access.share

DomoPage_Default.get_cards = content.get_cards
DomoPage_Default.get_datasets = content.get_datasets
DomoPage_Default.update_layout = content.update_layout
DomoPage_Default.add_owner = content.add_owner
