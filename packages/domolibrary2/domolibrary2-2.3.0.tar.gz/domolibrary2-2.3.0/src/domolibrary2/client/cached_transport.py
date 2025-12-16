"""HTTP response caching with smart URL-based invalidation.

This module implements browser-style HTTP caching for Domo API requests with:
- Automatic cache invalidation on mutations (POST/PUT/DELETE/PATCH)
- Smart URL pattern matching to determine what to invalidate
- Collection-level caching for paginated results (looper)
- Configurable TTLs per endpoint pattern
- Optional custom invalidation rules

Example:
    >>> from domolibrary2.auth import DomoTokenAuth
    >>>
    >>> # Enable caching (default: SMART invalidation strategy)
    >>> auth = DomoTokenAuth(
    ...     domo_instance="mycompany",
    ...     domo_access_token="token",
    ...     use_cache=True,
    ... )
    >>>
    >>> # Automatic caching and invalidation
    >>> user = await get_user(id="123")      # Cached
    >>> await update_user(id="123")          # Auto-invalidates cache
    >>> user = await get_user(id="123")      # Fresh data (cache miss)
"""

import asyncio
import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from urllib.parse import urlencode, urlparse

import httpx


class InvalidationStrategy(Enum):
    """Cache invalidation strategies.

    Attributes:
        EXACT: Only invalidate exact URL that was mutated
        SMART: Invalidate exact URL + parent collections (DEFAULT)
        AGGRESSIVE: Invalidate exact + parents + children
        CUSTOM: Use custom invalidation rules only
    """

    EXACT = "exact"
    SMART = "smart"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"


@dataclass
class CacheEntry:
    """Cache entry for a single HTTP response.

    Attributes:
        response: The cached httpx.Response object
        cached_at: Timestamp when response was cached
        ttl: Time-to-live in seconds
        url: Original request URL
    """

    response: httpx.Response
    cached_at: datetime
    ttl: int
    url: str

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        age = datetime.now(UTC) - self.cached_at
        return age.total_seconds() > self.ttl


@dataclass
class CollectionCacheEntry:
    """Cache entry for complete paginated collections.

    Attributes:
        data: Complete aggregated result from looper
        cached_at: Timestamp when collection was cached
        ttl: Time-to-live in seconds
        total_records: Number of records in collection
        request_count: Number of HTTP requests made to fetch collection
    """

    data: list
    cached_at: datetime
    ttl: int
    total_records: int
    request_count: int

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        age = datetime.now(UTC) - self.cached_at
        return age.total_seconds() > self.ttl


class SmartInvalidator:
    """Smart URL-based cache invalidation without manual rules.

    Automatically determines what cache entries to invalidate based on
    the URL of a mutation request, using intelligent pattern matching.

    Args:
        strategy: Invalidation strategy to use
        custom_rules: Optional custom invalidation rules (only used with CUSTOM strategy)

    Example:
        >>> invalidator = SmartInvalidator(strategy=InvalidationStrategy.SMART)
        >>>
        >>> # Mutation: PUT /api/content/v1/users/123
        >>> patterns = invalidator.get_invalidation_patterns(
        ...     "https://domo.com/api/content/v1/users/123"
        ... )
        >>> # Returns: ['/api/content/v1/users/123', '/api/content/v1/users', ...]
    """

    def __init__(
        self,
        strategy: InvalidationStrategy = InvalidationStrategy.SMART,
        custom_rules: dict[str, list[str]] | None = None,
    ):
        self.strategy = strategy
        self.custom_rules = custom_rules or {}

    def get_invalidation_patterns(self, mutation_url: str) -> set[str]:
        """Generate cache invalidation patterns for a mutation URL.

        Args:
            mutation_url: Full URL of the mutation request

        Returns:
            Set of regex patterns that should be invalidated
        """
        parsed = urlparse(mutation_url)
        path = parsed.path

        patterns = set()

        # Strategy 1: Exact match (always included)
        patterns.add(self._escape_pattern(path))

        if self.strategy == InvalidationStrategy.EXACT:
            return patterns

        # Strategy 2: Smart (exact + parent collections)
        if self.strategy in (
            InvalidationStrategy.SMART,
            InvalidationStrategy.AGGRESSIVE,
        ):
            parent_patterns = self._extract_parent_patterns(path)
            patterns.update(parent_patterns)

        # Strategy 3: Aggressive (exact + parent + children)
        if self.strategy == InvalidationStrategy.AGGRESSIVE:
            child_pattern = self._escape_pattern(path) + r"/.*"
            patterns.add(child_pattern)

        # Strategy 4: Custom rules (if provided)
        if self.strategy == InvalidationStrategy.CUSTOM and self.custom_rules:
            custom = self._apply_custom_rules(path)
            patterns.update(custom)

        return patterns

    def _escape_pattern(self, path: str) -> str:
        """Escape special regex characters in path."""
        return re.escape(path)

    def _extract_parent_patterns(self, path: str) -> set[str]:
        r"""Extract parent resource patterns from path.

        Examples:
            /api/content/v1/users/123
            → /api/content/v1/users (list endpoint)
            → /api/content/v1/users\?.* (list with query params)
        """
        patterns = set()

        # Split path into segments
        segments = [s for s in path.split("/") if s]

        # Generate parent paths
        for i in range(len(segments)):
            parent_path = "/" + "/".join(segments[: i + 1])

            # Skip if it's the full path (already in exact match)
            if parent_path == path:
                continue

            # Add parent path pattern
            escaped = self._escape_pattern(parent_path)
            patterns.add(escaped)

            # Add parent with query params (list endpoints)
            patterns.add(escaped + r"\?.*")

        return patterns

    def _apply_custom_rules(self, path: str) -> set[str]:
        """Apply custom invalidation rules if they match."""
        patterns = set()

        for rule_pattern, invalidate_patterns in self.custom_rules.items():
            if re.match(rule_pattern, path):
                for inv_pattern in invalidate_patterns:
                    # Support capture group replacement
                    actual_pattern = re.sub(rule_pattern, inv_pattern, path)
                    patterns.add(actual_pattern)

        return patterns


# Default TTL configuration by endpoint pattern
DEFAULT_TTL_CONFIG = {
    # Static data - cache aggressively
    r"/api/data/v1/[\w-]+/schema": 3600,  # Schema rarely changes
    r"/api/content/v1/users/\d+": 1800,  # User profiles
    r"/api/content/v2/groups/\d+": 1800,  # Groups
    # Semi-static - moderate caching
    r"/api/data/v3/datasources/[\w-]+": 300,  # Dataset metadata
    r"/api/content/v1/pages": 300,  # Pages/dashboards
    r"/api/content/v6/cards": 300,  # Cards
    # Dynamic - short cache
    r"/api/query/v1/execute": 60,  # Query results
    r"/api/data/v2/dataflows/.*/executions": 30,  # Execution history
    # Never cache
    r"/api/auth/.*": 0,  # Auth tokens
}

DEFAULT_TTL = 300  # 5 minutes

# Collection cache TTLs (longer than individual resources)
COLLECTION_TTL_CONFIG = {
    r"/api/content/v1/users": 600,  # 10 minutes
    r"/api/content/v1/groups": 600,  # 10 minutes
    r"/api/data/v3/datasources": 300,  # 5 minutes
    r"/api/content/v6/cards": 300,  # 5 minutes
    r"/api/activity/v1/audit": 60,  # 1 minute (changes frequently)
}

DEFAULT_COLLECTION_TTL = 300  # 5 minutes


class CachedAsyncHTTPTransport(httpx.AsyncHTTPTransport):
    """HTTP transport with response caching and smart invalidation.

    This transport layer adds caching to httpx AsyncHTTPTransport with:
    - Automatic cache invalidation on mutations
    - Smart URL pattern matching
    - Separate collection cache for paginated results
    - Configurable TTLs per endpoint

    Args:
        cache_size: Maximum number of cached responses
        default_ttl: Default TTL in seconds for cached responses
        invalidation_strategy: Strategy for cache invalidation
        custom_invalidation_rules: Optional custom rules for CUSTOM strategy
        collection_cache_size: Maximum number of cached collections
        collection_cache_max_records: Maximum records per collection cache entry
        ttl_config: Optional TTL configuration by URL pattern
        collection_ttl_config: Optional collection TTL configuration
        **kwargs: Additional arguments passed to AsyncHTTPTransport

    Example:
        >>> transport = CachedAsyncHTTPTransport(
        ...     cache_size=1000,
        ...     default_ttl=300,
        ...     invalidation_strategy=InvalidationStrategy.SMART,
        ... )
        >>> client = httpx.AsyncClient(transport=transport)
    """

    def __init__(
        self,
        *args,
        cache_size: int = 1000,
        default_ttl: int = DEFAULT_TTL,
        invalidation_strategy: InvalidationStrategy = InvalidationStrategy.SMART,
        custom_invalidation_rules: dict[str, list[str]] | None = None,
        collection_cache_size: int = 100,
        collection_cache_max_records: int = 10_000,
        ttl_config: dict[str, int] | None = None,
        collection_ttl_config: dict[str, int] | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Request cache
        self.cache: dict[str, CacheEntry] = {}
        self.cache_size = cache_size
        self.default_ttl = default_ttl
        self.ttl_config = ttl_config or DEFAULT_TTL_CONFIG

        # Collection cache
        self.collection_cache: dict[str, CollectionCacheEntry] = {}
        self.collection_cache_size = collection_cache_size
        self.collection_cache_max_records = collection_cache_max_records
        self.collection_ttl_config = collection_ttl_config or COLLECTION_TTL_CONFIG

        # Invalidator
        self.invalidator = SmartInvalidator(
            strategy=invalidation_strategy,
            custom_rules=custom_invalidation_rules,
        )

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
            "bypasses": 0,
            "collection_hits": 0,
            "collection_misses": 0,
        }

        self._lock = asyncio.Lock()

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Handle HTTP request with caching.

        Args:
            request: The HTTP request to handle

        Returns:
            HTTP response (from cache or server)
        """
        # Check for cache bypass in extensions
        use_cache = request.extensions.get("use_cache", True)
        invalidate_first = request.extensions.get("invalidate_cache", False)

        # 1. Handle mutations - invalidate related caches BEFORE making request
        if request.method in {"POST", "PUT", "DELETE", "PATCH"}:
            await self._smart_invalidate(request.url)
            use_cache = False  # Never cache mutation responses

        # 2. Manual invalidation
        if invalidate_first:
            await self._invalidate_by_url(str(request.url))

        # 3. Try cache for GET requests
        if use_cache and request.method == "GET":
            cache_key = self._get_cache_key(request)
            if cache_key:
                cached_response = await self._get_from_cache(cache_key)
                if cached_response:
                    async with self._lock:
                        self.stats["hits"] += 1
                    return cached_response

                async with self._lock:
                    self.stats["misses"] += 1
        elif not use_cache:
            async with self._lock:
                self.stats["bypasses"] += 1

        # 4. Make real HTTP request
        response = await super().handle_async_request(request)

        # 5. Cache successful GET responses
        if use_cache and request.method == "GET" and 200 <= response.status_code < 300:
            cache_key = self._get_cache_key(request)
            if cache_key:
                await self._store_in_cache(cache_key, response, str(request.url))

        return response

    def _get_cache_key(self, request: httpx.Request) -> str | None:
        """Generate cache key from request.

        Args:
            request: HTTP request

        Returns:
            Cache key string or None if request shouldn't be cached
        """
        # Only cache GET requests
        if request.method != "GET":
            return None

        # Build cache key from method, path, params, and auth
        method = request.method
        url = str(request.url)

        # Include auth instance in key (from headers)
        auth_header = request.headers.get("x-domo-authentication", "")
        instance = auth_header.split(":")[0] if ":" in auth_header else ""

        # Create unique key
        key_parts = [method, url, instance]
        key_string = ":".join(key_parts)

        return hashlib.md5(key_string.encode(), usedforsecurity=False).hexdigest()

    async def _get_from_cache(self, cache_key: str) -> httpx.Response | None:
        """Retrieve response from cache if not expired.

        Args:
            cache_key: Cache key

        Returns:
            Cached response or None if not found/expired
        """
        async with self._lock:
            entry = self.cache.get(cache_key)

            if entry:
                if not entry.is_expired():
                    # Read the content to ensure it's decompressed
                    # This is necessary because accessing .content decompresses gzip responses
                    content = entry.response.content

                    # Create new headers without Content-Encoding since content is already decompressed
                    # This prevents httpx from trying to decompress again
                    headers = dict(entry.response.headers)
                    headers.pop("Content-Encoding", None)
                    headers.pop("content-encoding", None)

                    # Return a copy of the cached response
                    return httpx.Response(
                        status_code=entry.response.status_code,
                        headers=headers,
                        content=content,
                        request=entry.response.request,
                    )
                else:
                    # Remove expired entry
                    del self.cache[cache_key]

        return None

    async def _store_in_cache(self, cache_key: str, response: httpx.Response, url: str):
        """Store response in cache.

        Args:
            cache_key: Cache key
            response: HTTP response to cache
            url: Request URL (for TTL lookup)
        """
        ttl = self._get_ttl(url)

        if ttl == 0:
            # Don't cache if TTL is 0
            return

        async with self._lock:
            # Evict oldest if at capacity
            if len(self.cache) >= self.cache_size:
                oldest_key = min(
                    self.cache.keys(), key=lambda k: self.cache[k].cached_at
                )
                del self.cache[oldest_key]

            # Read the response content to ensure it's decompressed before caching
            # This ensures that when we reconstruct the response, we don't have
            # compression issues. We need to read it first if it hasn't been read.
            try:
                _ = response.content  # Force read/decompression if not already read
            except (RuntimeError, httpx.StreamConsumed, httpx.ResponseNotRead):
                # Response might already be read or might be streaming
                # Try to read it explicitly
                await response.aread()

            self.cache[cache_key] = CacheEntry(
                response=response,
                cached_at=datetime.now(UTC),
                ttl=ttl,
                url=url,
            )

    def _get_ttl(self, url: str) -> int:
        """Get TTL for URL based on pattern matching.

        Args:
            url: Request URL

        Returns:
            TTL in seconds
        """
        parsed = urlparse(url)
        path = parsed.path

        for pattern, ttl in self.ttl_config.items():
            if re.match(pattern, path):
                return ttl

        return self.default_ttl

    async def _smart_invalidate(self, url: httpx.URL):
        """Smart invalidation based on mutation URL.

        Args:
            url: URL of the mutation request
        """
        url_str = str(url)

        # Get invalidation patterns
        patterns = self.invalidator.get_invalidation_patterns(url_str)

        # Invalidate matching cache entries
        async with self._lock:
            keys_to_delete = []

            for cache_key, entry in self.cache.items():
                cached_url = entry.url

                # Check if any pattern matches
                for pattern in patterns:
                    parsed = urlparse(cached_url)
                    if re.search(pattern, parsed.path):
                        keys_to_delete.append(cache_key)
                        break

            # Delete matched keys
            for key in keys_to_delete:
                del self.cache[key]

            if keys_to_delete:
                self.stats["invalidations"] += len(keys_to_delete)

        # Also invalidate related collection caches
        await self._invalidate_collection_by_url(url_str)

    async def _invalidate_by_url(self, url: str):
        """Manually invalidate cache entries matching URL.

        Args:
            url: URL pattern to invalidate
        """
        async with self._lock:
            keys_to_delete = []

            for cache_key, entry in self.cache.items():
                if url in entry.url:
                    keys_to_delete.append(cache_key)

            for key in keys_to_delete:
                del self.cache[key]

            if keys_to_delete:
                self.stats["invalidations"] += len(keys_to_delete)

    async def _invalidate_collection_by_url(self, url: str):
        """Invalidate collection caches related to a mutation URL.

        Args:
            url: URL of the mutation
        """
        parsed = urlparse(url)
        path = parsed.path

        # Extract base path (remove ID segments)
        # e.g., /api/users/123 → /api/users
        segments = [s for s in path.split("/") if s]
        base_segments = [s for s in segments if not s.isdigit() and "-" not in s]
        base_path = "/" + "/".join(base_segments)

        async with self._lock:
            keys_to_delete = []

            for collection_key in self.collection_cache.keys():
                # Collection keys are like "collection:/api/users:instance"
                if base_path in collection_key:
                    keys_to_delete.append(collection_key)

            for key in keys_to_delete:
                del self.collection_cache[key]

    # Collection cache methods

    def get_collection_cache_key(
        self, base_url: str, params: dict | None, auth_instance: str
    ) -> str:
        """Generate collection cache key (ignoring pagination params).

        Args:
            base_url: Base URL
            params: Query parameters
            auth_instance: Authentication instance

        Returns:
            Collection cache key
        """
        parsed = urlparse(base_url)
        path = parsed.path

        # Filter out pagination parameters
        pagination_params = {"offset", "limit", "skip", "top", "page"}
        non_page_params = {}

        if params:
            non_page_params = {
                k: v for k, v in params.items() if k.lower() not in pagination_params
            }

        # Create collection key
        params_str = (
            urlencode(sorted(non_page_params.items())) if non_page_params else ""
        )
        return f"collection:{path}?{params_str}:{auth_instance}"

    async def get_collection_cache(
        self, base_url: str, params: dict | None, auth_instance: str
    ) -> CollectionCacheEntry | None:
        """Retrieve cached collection if not expired.

        Args:
            base_url: Base URL
            params: Query parameters
            auth_instance: Authentication instance

        Returns:
            Cached collection or None
        """
        key = self.get_collection_cache_key(base_url, params, auth_instance)

        async with self._lock:
            entry = self.collection_cache.get(key)

            if entry:
                if not entry.is_expired():
                    self.stats["collection_hits"] += 1
                    return entry
                else:
                    # Remove expired entry
                    del self.collection_cache[key]
                    self.stats["collection_misses"] += 1

        return None

    async def store_collection_cache(
        self,
        base_url: str,
        params: dict | None,
        auth_instance: str,
        data: list,
        request_count: int,
        ttl: int | None = None,
    ):
        """Store collection in cache.

        Args:
            base_url: Base URL
            params: Query parameters
            auth_instance: Authentication instance
            data: Collection data
            request_count: Number of requests made to fetch collection
            ttl: Optional TTL override
        """
        # Don't cache if collection is too large
        if len(data) > self.collection_cache_max_records:
            return

        key = self.get_collection_cache_key(base_url, params, auth_instance)

        if ttl is None:
            # Get TTL from config
            parsed = urlparse(base_url)
            path = parsed.path

            ttl = DEFAULT_COLLECTION_TTL
            for pattern, config_ttl in self.collection_ttl_config.items():
                if re.match(pattern, path):
                    ttl = config_ttl
                    break

        async with self._lock:
            # Evict oldest if at capacity
            if len(self.collection_cache) >= self.collection_cache_size:
                oldest_key = min(
                    self.collection_cache.keys(),
                    key=lambda k: self.collection_cache[k].cached_at,
                )
                del self.collection_cache[oldest_key]

            self.collection_cache[key] = CollectionCacheEntry(
                data=data,
                cached_at=datetime.now(UTC),
                ttl=ttl,
                total_records=len(data),
                request_count=request_count,
            )

    def clear_cache(self):
        """Clear all caches."""
        self.cache.clear()
        self.collection_cache.clear()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
            "bypasses": 0,
            "collection_hits": 0,
            "collection_misses": 0,
        }

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0.0

        total_collection_requests = (
            self.stats["collection_hits"] + self.stats["collection_misses"]
        )
        collection_hit_rate = (
            self.stats["collection_hits"] / total_collection_requests
            if total_collection_requests > 0
            else 0.0
        )

        return {
            "request_cache": {
                "total_entries": len(self.cache),
                "max_size": self.cache_size,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": hit_rate,
                "invalidations": self.stats["invalidations"],
                "bypasses": self.stats["bypasses"],
            },
            "collection_cache": {
                "total_entries": len(self.collection_cache),
                "max_size": self.collection_cache_size,
                "hits": self.stats["collection_hits"],
                "misses": self.stats["collection_misses"],
                "hit_rate": collection_hit_rate,
            },
        }
