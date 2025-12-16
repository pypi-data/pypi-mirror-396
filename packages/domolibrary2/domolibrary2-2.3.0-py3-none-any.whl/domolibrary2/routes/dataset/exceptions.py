"""Dataset route exceptions."""

from ...base.exceptions import RouteError
from ...client import response as rgd


class DatasetNotFoundError(RouteError):
    def __init__(
        self, dataset_id, res: rgd.ResponseGetData, message: str | None = None
    ):
        message = message or f"dataset - {dataset_id} not found"

        super().__init__(message=message, res=res, entity_id=dataset_id)


class Dataset_GET_Error(RouteError):
    def __init__(
        self,
        res: rgd.ResponseGetData,
        dataset_id=None,
        message=None,
    ):
        super().__init__(message=message, res=res, entity_id=dataset_id)


class Dataset_CRUD_Error(RouteError):
    def __init__(
        self,
        res: rgd.ResponseGetData,
        dataset_id=None,
        message=None,
    ):
        super().__init__(message=message, res=res, entity_id=dataset_id)


class QueryRequestError(RouteError):
    def __init__(
        self,
        res: rgd.ResponseGetData,
        sql,
        dataset_id,
        message=None,
    ):
        message = message or f"{res.response} - Check your SQL \n {sql}"

        super().__init__(message=message, res=res, entity_id=dataset_id)


class UploadDataError(RouteError):
    """raise if unable to upload data to Domo"""

    def __init__(
        self,
        stage_num: int,
        dataset_id: str,
        res: rgd.ResponseGetData,
        message: str | None = None,
    ):
        message = f"error uploading data during Stage {stage_num} - {message}"

        super().__init__(entity_id=dataset_id, message=message, res=res)


class ShareDataset_Error(RouteError):
    def __init__(
        self, dataset_id, res: rgd.ResponseGetData, message: str | None = None
    ):
        message = message or str(res.response)

        super().__init__(res=res, message=message, entity_id=dataset_id)
