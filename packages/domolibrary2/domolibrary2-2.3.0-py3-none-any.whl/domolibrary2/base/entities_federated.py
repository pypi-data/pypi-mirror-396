import abc
from collections.abc import Callable
from dataclasses import dataclass

from .entities import DomoEntity_w_Lineage


@dataclass
class DomoFederatedEntity(DomoEntity_w_Lineage):
    """Entity that can be federated across multiple Domo instances.

    This class extends lineage-enabled entities to support federation,
    allowing entities to maintain relationships across different Domo
    instances in federated environments.
    """

    __skip_lineage_registration__ = True  # Abstract intermediate class, not registered

    @abc.abstractmethod
    async def get_federated_parent(
        self, parent_auth=None, parent_auth_retrieval_fn: Callable | None = None
    ):
        """Retrieve the parent entity from a federated Domo instance.

        Args:
            parent_auth: Authentication object for the parent instance
            parent_auth_retrieval_fn (Callable | None): Function to retrieve parent auth

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
