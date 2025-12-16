"""Dataset route module - re-exports all dataset functionality."""

from .core import (
    create,
    create_dataset_enterprise_tookit,
    delete,
    delete_partition_stage_1,
    delete_partition_stage_2,
    generate_create_dataset_body,
    generate_enterprise_toolkit_body,
    generate_remote_domostats_body,
    get_dataset_by_id,
    search_datasets,
)
from .dataset_views import get_dataset_view_schema_indexed
from .exceptions import (
    Dataset_CRUD_Error,
    Dataset_GET_Error,
    DatasetNotFoundError,
    QueryRequestError,
    ShareDataset_Error,
    UploadDataError,
)
from .query import query_dataset_private, query_dataset_public
from .schema import (
    alter_schema,
    alter_schema_descriptions,
    get_schema,
    set_dataset_tags,
)
from .sharing import (
    ShareDataset_AccessLevelEnum,
    generate_share_dataset_payload,
    get_permissions,
    share_dataset,
)
from .upload import (
    generate_list_partitions_body,
    index_dataset,
    index_status,
    list_partitions,
    upload_dataset_stage_1,
    upload_dataset_stage_2_df,
    upload_dataset_stage_2_file,
    upload_dataset_stage_3,
)

__all__ = [
    # Exceptions
    "DatasetNotFoundError",
    "Dataset_GET_Error",
    "Dataset_CRUD_Error",
    "QueryRequestError",
    "UploadDataError",
    "ShareDataset_Error",
    # Query
    "query_dataset_public",
    "query_dataset_private",
    # Core
    "get_dataset_by_id",
    "search_datasets",
    "generate_create_dataset_body",
    "create",
    "generate_enterprise_toolkit_body",
    "generate_remote_domostats_body",
    "create_dataset_enterprise_tookit",
    "delete_partition_stage_1",
    "delete_partition_stage_2",
    "delete",
    # Schema
    "get_schema",
    "alter_schema",
    "alter_schema_descriptions",
    "set_dataset_tags",
    # Dataset Views
    "get_dataset_view_schema_indexed",
    # Upload
    "upload_dataset_stage_1",
    "upload_dataset_stage_2_file",
    "upload_dataset_stage_2_df",
    "upload_dataset_stage_3",
    "index_dataset",
    "index_status",
    "generate_list_partitions_body",
    "list_partitions",
    # Sharing
    "ShareDataset_AccessLevelEnum",
    "generate_share_dataset_payload",
    "share_dataset",
    "get_permissions",
]
