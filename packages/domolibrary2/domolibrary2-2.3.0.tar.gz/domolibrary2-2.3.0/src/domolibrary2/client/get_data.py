import asyncio
from collections.abc import Callable
from contextlib import asynccontextmanager
from functools import wraps
from pprint import pprint
from typing import Any

import httpx

from ..auth import (
    base as dmda,
)
from ..base.exceptions import DomoError
from ..utils import chunk_execution as dmce
from ..utils.logging import (
    LogDecoratorConfig,
    ResponseGetDataProcessor,
    get_colored_logger,
    log_call,
)
from . import response as rgd
from .context import RouteContext

__all__ = [
    "GetDataError",
    "get_data",
    "get_data_stream",
    "LooperError",
    "looper",
    "RouteFunctionResponseTypeError",
    "route_function",
    "httpx_session_context",
]

# Initialize colored logger
logger = get_colored_logger()

# Constants
DEFAULT_TIMEOUT = 20
DEFAULT_STREAM_TIMEOUT = 10


class GetDataError(DomoError):
    def __init__(self, message, url):
        super().__init__(message=message, domo_instance=url)


def create_headers(
    auth: "dmda.DomoAuth" = None,  # The authentication object containing the Domo API token.
    content_type: (
        str | None
    ) = None,  # The content type for the request. Defaults to None.
    headers: dict = None,  # Any additional headers for the request. Defaults to None.
) -> dict:  # The headers for the request.
    """
    Creates default headers for interacting with Domo APIs.
    """

    if headers is None:
        headers = {}

    headers = {
        "Content-Type": content_type or "application/json",
        "Connection": "keep-alive",
        "accept": "application/json, text/plain",
        **headers,
    }
    if auth:
        headers.update(**auth.auth_header)
    return headers


@asynccontextmanager
async def httpx_session_context(
    session: httpx.AsyncClient | None = None,
    is_verify: bool = False,
    use_cache: bool = True,
    cache_config: dict | None = None,
):
    """Context manager for httpx session lifecycle with optional caching.

    Provides automatic session cleanup and supports HTTP response caching
    via CachedAsyncHTTPTransport. If a session is provided, it's reused
    and the caller manages its lifecycle. Otherwise, a new session is
    created and automatically closed when exiting the context.

    Args:
        session: Optional existing session to reuse (caller manages lifecycle)
        is_verify: SSL verification flag
        use_cache: Enable HTTP response caching (default: True)
        cache_config: Optional cache configuration dict. Valid keys:
            - cache_size: Maximum number of cached responses
            - default_ttl: Default TTL in seconds for cached responses
            - invalidation_strategy: Strategy for cache invalidation
            - custom_invalidation_rules: Optional custom rules for CUSTOM strategy
            - collection_cache_size: Maximum number of cached collections
            - collection_cache_max_records: Maximum records per collection cache entry
            - ttl_config: Optional TTL configuration by URL pattern
            - collection_ttl_config: Optional collection TTL configuration

    Yields:
        httpx.AsyncClient session

    Example:
        >>> # Basic usage with caching enabled
        >>> async with httpx_session_context(use_cache=True) as session:
        ...     response = await session.get("https://api.example.com")
        ...
        >>> # Reuse existing session
        >>> async with httpx_session_context(session=existing_session) as session:
        ...     response = await session.get("https://api.example.com")
        ...
        >>> # Custom cache configuration
        >>> cache_config = {"cache_size": 2000, "default_ttl": 600}
        >>> async with httpx_session_context(use_cache=True, cache_config=cache_config) as session:
        ...     response = await session.get("https://api.example.com")
    """
    if session is not None:
        # Reuse provided session (caller manages lifecycle)
        yield session
    else:
        # Create new session with optional caching
        if use_cache:
            from .cached_transport import CachedAsyncHTTPTransport

            # Filter cache_config to only include valid CachedAsyncHTTPTransport parameters
            valid_transport_params = {
                "cache_size",
                "default_ttl",
                "invalidation_strategy",
                "custom_invalidation_rules",
                "collection_cache_size",
                "collection_cache_max_records",
                "ttl_config",
                "collection_ttl_config",
            }

            filtered_config = (
                {k: v for k, v in cache_config.items() if k in valid_transport_params}
                if cache_config
                else {}
            )

            transport = CachedAsyncHTTPTransport(verify=is_verify, **filtered_config)
            session = httpx.AsyncClient(transport=transport)
        else:
            session = httpx.AsyncClient(verify=is_verify)

        try:
            yield session
        finally:
            await session.aclose()


def create_httpx_session(
    session: httpx.AsyncClient = None,
    is_verify: bool = False,
    use_cache: bool = False,
    cache_config: dict | None = None,
) -> tuple[httpx.AsyncClient, bool]:
    """Creates or reuses an asynchronous HTTPX session.

    DEPRECATED: Use httpx_session_context() instead for proper lifecycle management.

    Args:
        session: An optional existing HTTPX AsyncClient session.
        is_verify: Boolean flag for SSL verification.
        use_cache: Enable HTTP response caching.
        cache_config: Optional cache configuration dict.

    Returns:
        A tuple containing the HTTPX session and a boolean indicating if the session should be closed.
    """
    is_close_session = False

    if session is None:
        is_close_session = True

        if use_cache:
            from .cached_transport import CachedAsyncHTTPTransport

            # Filter cache_config to only include valid CachedAsyncHTTPTransport parameters
            valid_transport_params = {
                "cache_size",
                "default_ttl",
                "invalidation_strategy",
                "custom_invalidation_rules",
                "collection_cache_size",
                "collection_cache_max_records",
                "ttl_config",
                "collection_ttl_config",
            }

            filtered_config = (
                {k: v for k, v in cache_config.items() if k in valid_transport_params}
                if cache_config
                else {}
            )

            transport = CachedAsyncHTTPTransport(verify=is_verify, **filtered_config)
            session = httpx.AsyncClient(transport=transport)
        else:
            session = httpx.AsyncClient(verify=is_verify)

    return session, is_close_session


@dmce.run_with_retry()
@log_call(
    action_name="get_data",
    level_name="client",
    log_level="DEBUG",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
    color="light_blue",
)
async def get_data(
    url: str,
    method: str,
    auth: "dmda.DomoAuth" = None,
    content_type: str = None,
    headers: dict = None,
    body: dict | list | str | None = None,
    params: dict = None,
    context: RouteContext | None = None,
    debug_api: bool = None,
    session: httpx.AsyncClient | None = None,
    return_raw: bool = None,
    is_follow_redirects: bool = None,
    timeout: int = None,
    parent_class: str | None = None,
    debug_num_stacks_to_drop: int = None,
    is_verify: bool = None,
    dry_run: bool = None,
    **kwargs,
) -> rgd.ResponseGetData:
    """Asynchronously performs an HTTP request to retrieve data from a Domo API endpoint.

    Args:
        url: API endpoint URL
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        auth: Authentication object containing credentials
        content_type: Optional content type header
        headers: Additional HTTP headers
        body: Request body (dict, list, or string)
        params: Query parameters
        context: Optional RouteContext with debug/session settings (takes precedence over individual params)
        debug_api: Enable API debugging (overridden by context if provided)
        session: Optional httpx client session (overridden by context if provided)
        return_raw: Return raw httpx response
        is_follow_redirects: Follow HTTP redirects
        timeout: Request timeout in seconds
        parent_class: Optional parent class name for debugging (overridden by context if provided)
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output (overridden by context if provided)
        is_verify: SSL verification flag
        dry_run: If True, return request parameters without executing

    Returns:
        ResponseGetData object containing the response
    """

    # Build context from individual parameters (manual params override context)
    context = RouteContext.build_context(
        context=context,
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        is_follow_redirects=is_follow_redirects,
        is_verify=is_verify,
        dry_run=dry_run,
    )

    # Set defaults for params not in RouteContext
    timeout = timeout or DEFAULT_TIMEOUT
    return_raw = return_raw if return_raw is not None else False

    if context.debug_api:
        print(f"[DEBUG] get_data: {method} {url}", flush=True)
        await logger.debug(f"🐛 Debugging get_data: {method} {url}")

    # Create headers and session
    headers = create_headers(
        auth=auth, content_type=content_type, headers=headers or {}
    )

    # Automatically use auth's cached session if available and caching is enabled
    # This allows users to simply enable caching on auth without managing sessions
    session_from_auth = None
    if (
        context.session is None
        and context.use_cache
        and auth
        and hasattr(auth, "_cached_session")
        and auth._cached_session is not None
    ):
        session_from_auth = auth._cached_session

    # Create session with cache support from context
    session, is_close_session = create_httpx_session(
        session=session_from_auth or context.session,
        is_verify=context.is_verify,
        use_cache=context.use_cache,
        cache_config=context.cache_config,
    )

    # Store the session in auth if caching is enabled and session was created
    # This ensures subsequent requests reuse the same cached session
    # Don't close sessions that are stored in auth (user manages lifecycle)
    if (
        context.use_cache
        and auth
        and hasattr(auth, "_cached_session")
        and auth._cached_session is None
        and is_close_session  # Session was just created
    ):
        auth._cached_session = session
        context.session = session  # Update context to reference cached session
        is_close_session = False  # Don't close it, user will manage lifecycle
    elif (
        context.use_cache
        and auth
        and hasattr(auth, "_cached_session")
        and auth._cached_session is not None
        and context.session != auth._cached_session
    ):
        # If auth has a cached session but context doesn't reference it, update context
        context.session = auth._cached_session

    # Build metadata and additional information
    request_metadata = rgd.RequestMetadata(
        url=url, headers=headers, body=body, params=params
    )

    additional_information = {}
    if context.parent_class:
        additional_information["parent_class"] = context.parent_class

    if context.debug_api:
        message = f"[DEBUG] Request Metadata: {request_metadata.to_dict()}"
        print(message, flush=True)
        await logger.debug(message)

    # Handle dry run mode
    if context.dry_run:
        message = "[DEBUG] Dry run mode enabled. Request not sent."
        print(message, flush=True)
        await logger.debug(message)

        additional_information["dry_run"] = True
        return rgd.ResponseGetData(
            status=200,
            response={
                "dry_run": True,
                "method": method,
                "url": url,
                "headers": headers,
                "body": body,
                "params": params,
                "auth": {
                    "domo_instance": auth.domo_instance if auth else None,
                    "auth_type": type(auth).__name__ if auth else None,
                },
            },
            is_success=True,
            request_metadata=request_metadata,
            additional_information=additional_information,
        )

    try:
        # Build and execute request
        request_kwargs = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "follow_redirects": context.is_follow_redirects,
            "timeout": timeout,
        }

        if isinstance(body, dict | list):
            request_kwargs["json"] = body
        elif isinstance(body, str):
            request_kwargs["content"] = body

        response = await session.request(**request_kwargs)

        if context.debug_api:
            print(f"[DEBUG] Response Status: {response.status_code}", flush=True)
            print(f"[DEBUG] Response Text: {response.text[:500]}", flush=True)
            await logger.debug(f"Response Status: {response.status_code}")

        # Handle special response cases
        if "<title>Domo - Blocked</title>" in response.text:
            ip_address = rgd.find_ip(response.text)
            raise GetDataError(url=url, message=f"Blocked by VPN: {ip_address}")

        if response.status_code == 303 and "whitelist/blocked" in response.text:
            ip_address = rgd.find_ip(response.text)
            raise GetDataError(url=url, message=f"Blocked by Allowlist: {ip_address}")

        if return_raw:
            # Return ResponseGetData with raw_response field populated
            return rgd.ResponseGetData.from_httpx_response(
                res=response,
                request_metadata=request_metadata,
                additional_information=additional_information,
                raw_response=response,
            )

        # Process normal response
        return rgd.ResponseGetData.from_httpx_response(
            res=response,
            request_metadata=request_metadata,
            additional_information=additional_information,
        )

    finally:
        if is_close_session:
            await session.aclose()


@dmce.run_with_retry()
@log_call(
    action_name="get_data_stream",
    level_name="client",
    log_level="DEBUG",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_data_stream(
    url: str,
    auth: dmda.DomoAuth,
    method: str = "GET",
    content_type: str | None = "application/json",
    headers: dict | None = None,
    params: dict | None = None,
    context: RouteContext | None = None,
    debug_api: bool = None,
    timeout: int = DEFAULT_STREAM_TIMEOUT,
    parent_class: str | None = None,
    session: httpx.AsyncClient | None = None,
    is_verify: bool = None,
    is_follow_redirects: bool = None,
) -> rgd.ResponseGetData:
    """Asynchronously streams data from a Domo API endpoint.

    Args:
        url: API endpoint URL.
        auth: Authentication object for Domo APIs.
        method: HTTP method to use, default is GET.
        content_type: Optional content type header.
        headers: Additional HTTP headers.
        params: Query parameters for the request.
        context: Optional RouteContext with debug/session settings (takes precedence over individual params)
        debug_api: Enable debugging information (overridden by context if provided).
        timeout: Maximum time to wait for a response (in seconds).
        parent_class: (Optional) Name of the calling class (overridden by context if provided).
        session: Optional HTTPX session to be used (overridden by context if provided).
        is_verify: SSL verification flag.
        is_follow_redirects: Follow HTTP redirects if True.

    Returns:
        An instance of ResponseGetData containing the streamed response data.
    """
    # Extract parameters from context if provided
    if isinstance(context, RouteContext):
        session = context.session or session
        parent_class = context.parent_class or parent_class
        debug_api = context.debug_api if context.debug_api is not None else debug_api

    if debug_api:
        message = f"[DEBUG] get_data_stream: {method} {url}"
        print(message, flush=True)
        await logger.debug(message)

    if auth and not auth.token:
        await auth.get_auth_token()

    headers = headers or {}
    headers.update({"Connection": "keep-alive"})
    headers = create_headers(headers=headers, content_type=content_type, auth=auth)

    # Create request metadata
    request_metadata = rgd.RequestMetadata(
        url=url,
        headers=headers,
        body=None,
        params=params,
    )

    # Create additional information with parent_class
    additional_information = {}
    if parent_class:
        additional_information["parent_class"] = parent_class

    if debug_api:
        pprint(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "params": params,
            }
        )

    session, is_close_session = create_httpx_session(
        session=session, is_verify=is_verify
    )

    try:
        async with session.stream(
            method,
            url=url,
            headers=headers,
            follow_redirects=is_follow_redirects,
            timeout=timeout,
        ) as res:
            if res.status_code != 200:
                response_text = (
                    res.text if hasattr(res, "text") else str(await res.aread())
                )
                res_obj = rgd.ResponseGetData(
                    status=res.status_code,
                    response=response_text,
                    is_success=False,
                    request_metadata=request_metadata,
                    additional_information=additional_information,
                )
                return res_obj

            content = bytearray()
            async for chunk in res.aiter_bytes():
                content += chunk

            res_obj = rgd.ResponseGetData(
                status=res.status_code,
                response=content,  # type: ignore
                is_success=True,
                request_metadata=request_metadata,
                additional_information=additional_information,
            )
            return res_obj

    except httpx.TransportError as e:
        raise GetDataError(url=url, message=str(e)) from e

    finally:
        if is_close_session:
            await session.aclose()


class LooperError(DomoError):
    def __init__(self, loop_stage: str, message):
        super().__init__(message=f"{loop_stage} - {message}")


@log_call(action_name="looper", level_name="client", log_level="DEBUG")
async def looper(
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient | None = None,
    url: str = None,
    offset_params: dict = None,
    arr_fn: Callable = None,
    loop_until_end: bool = False,  # usually you'll set this to true.  it will override maximum
    method="POST",
    body: dict | None = None,
    fixed_params: dict | None = None,
    offset_params_in_body: bool = False,
    body_fn=None,
    limit=1000,
    skip=0,
    maximum=0,
    context: RouteContext | None = None,
    debug_api: bool = False,
    debug_loop: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str | None = None,
    timeout: int = 10,
    wait_sleep: int = 0,
    is_verify: bool = False,
    return_raw: bool = False,
    # NEW: Collection cache parameters
    use_collection_cache: bool = True,
    collection_cache_ttl: int | None = None,
    invalidate_collection_cache: bool = False,
) -> rgd.ResponseGetData:
    """Iteratively retrieves paginated data from a Domo API endpoint with optional collection caching.

    Args:
        auth: Authentication object for Domo APIs.
        session: HTTPX AsyncClient session used for making requests (overridden by context if provided).
        url: API endpoint URL for data retrieval.
        offset_params: Dictionary specifying the pagination keys (e.g., 'offset', 'limit').
        arr_fn: Function to extract records from the API response.
        loop_until_end: If True, continues fetching until no new records are returned.
        method: HTTP method to use (default is POST).
        body: Request payload (if required).
        fixed_params: Fixed query parameters to include in every request.
        offset_params_in_body: Whether to include pagination parameters inside the request body.
        body_fn: Function to modify the request body before each request.
        limit: Number of records to retrieve per request.
        skip: Initial offset value.
        maximum: Maximum number of records to retrieve.
        context: Optional RouteContext with debug/session settings (takes precedence over individual params)
        debug_api: Enable debugging output for API calls.
        debug_loop: Enable debugging output for the looping process.
        debug_num_stacks_to_drop: Number of stack frames to drop in traceback for debugging (overridden by context if provided).
        parent_class: (Optional) Name of the calling class (overridden by context if provided).
        timeout: Request timeout value.
        wait_sleep: Time to wait between consecutive requests (in seconds).
        is_verify: SSL verification flag.
        return_raw: Flag to return the raw response instead of processed data.
        use_collection_cache: Enable collection-level caching (caches complete paginated results).
        collection_cache_ttl: TTL in seconds for collection cache (None = use transport default).
        invalidate_collection_cache: Force invalidation of collection cache before fetching.

    Returns:
        An instance of ResponseGetData containing the aggregated data and pagination metadata.
    """
    # Extract parameters from context if provided (manual params take precedence)
    if isinstance(context, RouteContext):
        session = session or context.session
        debug_num_stacks_to_drop = (
            context.debug_num_stacks_to_drop
            if context.debug_num_stacks_to_drop is not None
            else debug_num_stacks_to_drop
        )
        parent_class = context.parent_class or parent_class
        # Only use context.debug_api if manual param is False (default)
        debug_api = debug_api or (context.debug_api if context.debug_api else False)

    is_close_session = False

    session, is_close_session = create_httpx_session(session, is_verify=is_verify)

    # Phase 2: Collection Cache Check
    if use_collection_cache and hasattr(session, "_transport"):
        transport = session._transport

        if hasattr(transport, "get_collection_cache"):
            auth_instance = auth.domo_instance

            # Manual invalidation if requested
            if invalidate_collection_cache:
                if hasattr(transport, "invalidate_collection_by_url"):
                    await transport.invalidate_collection_by_url(url)
                    if debug_loop:
                        print(
                            f"[DEBUG] Collection cache invalidated for {url}",
                            flush=True,
                        )
                        await logger.debug(f"Collection cache invalidated for {url}")

            # Try collection cache
            cached = await transport.get_collection_cache(
                base_url=url,
                params=fixed_params or {},
                auth_instance=auth_instance,
            )

            if cached:
                if debug_loop:
                    print(
                        f"[CACHE HIT] Retrieved {cached.total_records} records from collection cache",
                        flush=True,
                    )
                    await logger.info(
                        f"Collection cache hit: {cached.total_records} records, "
                        f"cached_at={cached.cached_at.isoformat()}, "
                        f"saved {cached.request_count} API calls"
                    )

                # Return cached data
                return rgd.ResponseGetData(
                    status=200,
                    response=cached.data,
                    is_success=True,
                    additional_information={
                        "cache_hit": True,
                        "from_collection_cache": True,
                        "cached_at": cached.cached_at.isoformat(),
                        "total_records": cached.total_records,
                        "original_request_count": cached.request_count,
                    },
                )

    all_rows = []
    is_loop = True
    request_count = 0  # Track number of API calls made

    res: rgd.ResponseGetData | None = None

    if maximum and maximum <= limit and not loop_until_end:
        limit = maximum

    while is_loop:
        params = fixed_params or {}

        if offset_params_in_body:
            if body is None:
                body = {}
            body.update(
                {offset_params.get("offset"): skip, offset_params.get("limit"): limit}
            )

        else:
            params.update(
                {offset_params.get("offset"): skip, offset_params.get("limit"): limit}
            )

        if body_fn:
            body = body_fn(skip, limit, body)

        if debug_loop:
            print(f"\n🚀 Retrieving records {skip} through {skip + limit} via {url}")
            await logger.debug(
                f"\n🚀 Retrieving records {skip} through {skip + limit} via {url}"
            )
            # pprint(params)

            message = {
                "action": "looper_request",
                "params": params,
                "body": body,
                "skip": skip,
                "limit": limit,
            }

        res = await get_data(
            auth=auth,
            url=url,
            method=method,
            params=params,
            body=body,
            timeout=timeout,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
            context=context,
            return_raw=return_raw,
        )
        request_count += 1  # Track number of API calls

        if not res or not res.is_success:
            if is_close_session:
                await session.aclose()

            return res or rgd.ResponseGetData(
                status=500, response="No response", is_success=False
            )

        if return_raw:
            return res

        new_records = arr_fn(res)

        all_rows += new_records

        if len(new_records) == 0:
            is_loop = False

        if maximum and len(all_rows) >= maximum and not loop_until_end:
            is_loop = False

        message = f"🐛 Looper iteration complete: {{'all_rows': {len(all_rows)}, 'new_records': {len(new_records)}, 'skip': {skip}, 'limit': {limit}}}"

        if debug_loop:
            print(message, flush=True)
            await logger.debug(message)

        if maximum and skip + limit > maximum and not loop_until_end:
            limit = maximum - len(all_rows)

        skip += len(new_records)
        await asyncio.sleep(wait_sleep)

    if debug_loop:
        message = f"\n🎉 Success - {len(all_rows)} records retrieved from {url} in query looper (made {request_count} API calls)\n"
        print(message, flush=True)
        await logger.info(message)

    # Phase 2: Store Collection Cache
    if (
        use_collection_cache
        and hasattr(session, "_transport")
        and all_rows
        and request_count > 0
    ):
        transport = session._transport

        if hasattr(transport, "store_collection_cache"):
            auth_instance = auth.domo_instance

            await transport.store_collection_cache(
                base_url=url,
                params=fixed_params or {},
                auth_instance=auth_instance,
                data=all_rows,
                request_count=request_count,
                ttl=collection_cache_ttl,
            )

            if debug_loop:
                print(
                    f"[CACHE STORE] Cached {len(all_rows)} records ({request_count} API calls saved for future)",
                    flush=True,
                )
                await logger.info(
                    f"Collection cached: {len(all_rows)} records, {request_count} requests"
                )

    if is_close_session:
        await session.aclose()

    if not res:
        return rgd.ResponseGetData(
            status=500, response="No response received", is_success=False
        )

    return await rgd.ResponseGetData.from_looper(res=res, array=all_rows)


class RouteFunctionResponseTypeError(TypeError):
    def __init__(self, result):
        super().__init__(
            f"Expected function to return an instance of ResponseGetData got {type(result)} instead.  Refactor function to return ResponseGetData class"
        )


def route_function(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for route functions to ensure they receive a built RouteContext.

    This decorator automatically builds a RouteContext from individual parameters
    or a pre-built context, eliminating the need for route functions to manually
    call RouteContext.build_context().

    ⚠️ IMPORTANT: Route functions decorated with @route_function MUST NOT call
    RouteContext.build_context() inside their function body. The decorator handles
    context building automatically. Route functions should only accept
    `context: RouteContext | None = None` as a parameter and pass it through to
    get_data/looper.

    Args:
        func (Callable[..., Any]): The function to decorate.

    Returns:
        Callable[..., Any]: The decorated function.

    The decorated function takes the following arguments:
        *args (Any): Positional arguments for the decorated function.
        parent_class (str, optional): The parent class. Defaults to None.
        debug_num_stacks_to_drop (int, optional): The number of stacks to drop for debugging. Defaults to 1.
        debug_api (bool, optional): Whether to debug the API. Defaults to False.
        session (httpx.AsyncClient, optional): The HTTPX client session. Defaults to None.
        log_level (LogLevel | str, optional): The log level. Defaults to LogLevel.INFO.
        dry_run (bool, optional): If True, return request parameters without executing. Defaults to False.
        context (RouteContext, optional): A pre-built route context object. Defaults to None.
        **kwargs (Any): Additional keyword arguments for the decorated function.
    """
    import inspect

    # Check if the function accepts 'context' parameter
    sig = inspect.signature(func)
    is_accepts_context = "context" in sig.parameters or any(
        param.kind == inspect.Parameter.VAR_KEYWORD for param in sig.parameters.values()
    )

    @wraps(func)
    async def wrapper(
        *args: Any,
        parent_class: str | None = None,
        debug_num_stacks_to_drop: int = 1,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        log_level: str | None = None,
        dry_run: bool = False,
        context: RouteContext | None = None,
        **kwargs: Any,
    ) -> Any:
        # Build context from parameters using RouteContext.build_context()
        # Only pass parameters that are not None to avoid overwriting with defaults
        context_params = {}
        if session is not None:
            context_params["session"] = session
        if debug_api is not False:  # Only pass if explicitly True
            context_params["debug_api"] = debug_api
        if debug_num_stacks_to_drop != 1:  # Only pass if not default
            context_params["debug_num_stacks_to_drop"] = debug_num_stacks_to_drop
        if parent_class is not None:
            context_params["parent_class"] = parent_class
        if log_level is not None:
            context_params["log_level"] = log_level
        if dry_run is not False:  # Only pass if explicitly True
            context_params["dry_run"] = dry_run

        context = RouteContext.build_context(context, **context_params)

        # Build kwargs for the function call
        call_kwargs = {**kwargs}

        # Only pass context if the function accepts it
        if is_accepts_context:
            call_kwargs["context"] = context
        else:
            # Pass individual parameters if function doesn't accept context
            if "debug_api" in sig.parameters:
                call_kwargs["debug_api"] = debug_api
            if "session" in sig.parameters:
                call_kwargs["session"] = session
            if "parent_class" in sig.parameters:
                call_kwargs["parent_class"] = parent_class
            if "debug_num_stacks_to_drop" in sig.parameters:
                call_kwargs["debug_num_stacks_to_drop"] = debug_num_stacks_to_drop
            if "dry_run" in sig.parameters:
                call_kwargs["dry_run"] = dry_run

        result = await func(*args, **call_kwargs)

        if not isinstance(result, rgd.ResponseGetData):
            raise RouteFunctionResponseTypeError(result)

        return result

    return wrapper
