import json
from enum import Enum
from typing import TypedDict

from ..auth import DomoAuth
from ..base.base import DomoEnumMixin
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)
from ..client.context import RouteContext
from ..utils import enums as dmue
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

__all__ = [
    "AIGETError",
    "AICRUDError",
    "DataDictionary_ColumnsDict",
    "ColumnsDict",
    "generate_chat_body",
    "AIGETError",
    "AICRUDError",
    "generate_summarize_body",
    "llm_summarize_text",
    "get_dataset_ai_readiness",
    "create_dataset_ai_readiness",
    "update_dataset_ai_readiness",
]


class AIGETError(RouteError):
    """Raised when AI service retrieval operations fail."""

    def __init__(self, message: str | None = None, res=None, **kwargs):
        super().__init__(
            message=message or "AI service retrieval failed",
            res=res,
            **kwargs,
        )


class AICRUDError(RouteError):
    """Raised when AI service create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"AI service {operation} failed",
            res=res,
            **kwargs,
        )


def generate_chat_body(
    text_input: str, model: str = "domo.domo_ai.domogpt-chat-medium-v1.1:anthropic"
) -> dict:
    return {
        "input": text_input,
        "promptTemplate": {"template": "${input}"},
        "model": model,
    }


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def llm_generate_text(
    text_input: str,
    auth: DomoAuth,
    chat_body: dict | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/ai/v1/text/generation"

    body = chat_body or generate_chat_body(text_input=text_input)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AICRUDError(operation="generate text", res=res)

    res.response["output"] = res.response["choices"][0]["output"]

    return res


class OutputStyleEnum(DomoEnumMixin, Enum):
    BULLETED = "BULLETED"
    NUMBERED = "Numbered"
    PARAGRAPH = "PARAGRAPH"


def generate_summarize_body(
    text_input: str,
    summary_length: int = 100,
    output_style: str = "BULLETED",
    system_prompt: str = "You are a helpful assistant that writes concise summaries",
    model: str = "domo.domo_ai.domogpt-summarize-v1:anthropic",
) -> dict:
    text_input = text_input if isinstance(text_input, str) else json.dumps(text_input)

    return {
        "input": text_input,
        "system": system_prompt,
        "promptTemplate": {
            "template": f"Write a {summary_length} summary of the following text. With {output_style} output.  Do not include a preamble. \nTEXT_TO_SUMMARIZE: {text_input} \nCONCISE SUMMARY:",
        },
        "model": model,
        "outputStyle": output_style,
        "outputWordLength": {"max": summary_length},
    }


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def llm_summarize_text(
    text_input: str,
    auth: DomoAuth,
    system_prompt: str | None = None,
    summary_length: int = 100,
    output_style: OutputStyleEnum = OutputStyleEnum.BULLETED,
    summary_body: dict | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    output_style = dmue.normalize_enum(output_style)

    url = f"https://{auth.domo_instance}.domo.com/api/ai/v1/text/summarize"

    body = summary_body or generate_summarize_body(
        text_input=text_input,
        system_prompt=system_prompt,
        output_style=output_style,
        summary_length=summary_length,
    )

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AICRUDError(operation="summarize text", res=res)

    res.response["ouptput"] = res.response["choices"][0]["output"]

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataset_ai_readiness(
    auth: DomoAuth,
    dataset_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/ai/readiness/v1/data-dictionary/dataset/{dataset_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AIGETError(res=res, entity_id=dataset_id)

    return res


class DataDictionary_ColumnsDict(TypedDict):
    name: str
    description: str
    synonyms: list[str]
    subType: str
    agentEnabled: bool
    beastmodeId: str


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_dataset_ai_readiness(
    auth: DomoAuth,
    dataset_id: str,
    dictionary_name: str,
    description: str | None = None,
    columns: list[DataDictionary_ColumnsDict] | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    body = {
        "datasetId": dataset_id,
        "name": dictionary_name,
        "description": description,
        "unitOfAnalysis": "",
        "columns": columns or [],
    }

    url = f"https://{auth.domo_instance}.domo.com/api/ai/readiness/v1/data-dictionary/dataset/{dataset_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AICRUDError(operation="create", res=res, entity_id=dataset_id)

    return res


class ColumnsDict(TypedDict):
    name: str
    description: str
    synonyms: list[str]
    subType: str
    agentEnabled: bool
    beastmodeId: str


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_dataset_ai_readiness(
    auth: DomoAuth,
    dataset_id: str,
    dictionary_id: str | None = None,
    dictionary_name: str | None = None,
    columns: list[ColumnsDict] | None = None,
    description: str | None = None,
    body: dict | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    body = body or {
        "id": dictionary_id,
        "name": dictionary_name,
        "description": description,
        "columns": columns,
    }

    body.update({"datasetId": dataset_id})

    url = f"https://{auth.domo_instance}.domo.com/api/ai/readiness/v1/data-dictionary/dataset/{dataset_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AICRUDError(operation="update", res=res, entity_id=dataset_id)

    return res
