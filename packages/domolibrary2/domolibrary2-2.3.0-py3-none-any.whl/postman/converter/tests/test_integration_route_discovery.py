"""Tests for route discovery functionality."""

from __future__ import annotations

import pytest

from ..integration.route_discovery import (
    RouteInfo,
    RouteRegistry,
    discover_routes,
)


class TestRouteInfo:
    """Tests for RouteInfo dataclass."""

    def test_to_dict(self):
        """Test converting RouteInfo to dictionary."""
        info = RouteInfo(
            function_name="get_accounts",
            module="domolibrary2.routes.account.core",
            url="/api/v1/accounts",
            method="GET",
            file_path="routes/account/core.py",
            line_number=42,
            docstring="Get all accounts",
            signature="async def get_accounts(auth: DomoAuth) -> rgd.ResponseGetData",
        )

        result = info.to_dict()

        assert result["function_name"] == "get_accounts"
        assert result["module"] == "domolibrary2.routes.account.core"
        assert result["url"] == "/api/v1/accounts"
        assert result["method"] == "GET"


class TestRouteRegistry:
    """Tests for RouteRegistry class."""

    def test_add_route(self):
        """Test adding a route to registry."""
        registry = RouteRegistry()
        route = RouteInfo(
            function_name="test_route",
            module="test.module",
            url="/test",
            method="GET",
        )

        registry.add_route(route)

        assert len(registry.routes) == 1
        assert registry.routes["test_route"] == route

    def test_get_route(self):
        """Test getting a route from registry."""
        registry = RouteRegistry()
        route = RouteInfo(
            function_name="test_route",
            module="test.module",
            url="/test",
            method="GET",
        )

        registry.add_route(route)

        result = registry.get_route("test_route")
        assert result == route

        result = registry.get_route("nonexistent")
        assert result is None

    def test_get_routes_by_module(self):
        """Test getting routes by module."""
        registry = RouteRegistry()
        route1 = RouteInfo(
            function_name="route1",
            module="test.module1",
            url="/test1",
            method="GET",
        )
        route2 = RouteInfo(
            function_name="route2",
            module="test.module1",
            url="/test2",
            method="POST",
        )
        route3 = RouteInfo(
            function_name="route3",
            module="test.module2",
            url="/test3",
            method="GET",
        )

        registry.add_route(route1)
        registry.add_route(route2)
        registry.add_route(route3)

        module1_routes = registry.get_routes_by_module("test.module1")
        assert len(module1_routes) == 2
        assert route1 in module1_routes
        assert route2 in module1_routes

    def test_to_dict(self):
        """Test converting registry to dictionary."""
        registry = RouteRegistry()
        route = RouteInfo(
            function_name="test_route",
            module="test.module",
            url="/test",
            method="GET",
        )

        registry.add_route(route)

        result = registry.to_dict()
        assert "test_route" in result
        assert result["test_route"]["function_name"] == "test_route"


class TestDiscoverRoutes:
    """Tests for discover_routes function."""

    @pytest.fixture
    def sample_routes_dir(self, tmp_path):
        """Create a sample routes directory structure."""
        routes_dir = tmp_path / "routes"
        routes_dir.mkdir()

        # Create a module directory
        account_dir = routes_dir / "account"
        account_dir.mkdir()

        # Create a route file with @gd.route_function decorator
        route_file = account_dir / "core.py"
        route_file.write_text(
            '''"""Account routes."""
from domolibrary2.auth import DomoAuth
from domolibrary2.client import get_data
import domolibrary2.routes.get_data as gd
import domolibrary2.response_objects.get_data as rgd

@gd.route_function
async def get_accounts(
    auth: DomoAuth,
    debug: bool = False,
    session: object = None
) -> rgd.ResponseGetData:
    """Get all accounts.

    Args:
        auth: DomoAuth instance
        debug: Debug flag
        session: Session object

    Returns:
        ResponseGetData
    """
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts"
    return await get_data(auth=auth, url=url, debug=debug, session=session)
'''
        )

        # Create __init__.py
        (account_dir / "__init__.py").write_text("")

        return str(routes_dir)

    def test_discover_routes(self, sample_routes_dir):
        """Test discovering routes in a directory."""
        registry = discover_routes(sample_routes_dir)

        assert len(registry.routes) >= 1
        assert "get_accounts" in registry.routes

        route = registry.routes["get_accounts"]
        assert route.function_name == "get_accounts"
        assert "account" in route.module.lower()

    def test_discover_routes_nonexistent_dir(self):
        """Test discovering routes in nonexistent directory."""
        with pytest.raises(FileNotFoundError):
            discover_routes("nonexistent/directory")

    def test_discover_routes_skips_init(self, tmp_path):
        """Test that __init__.py files are skipped."""
        routes_dir = tmp_path / "routes"
        routes_dir.mkdir()

        # Create __init__.py (should be skipped)
        (routes_dir / "__init__.py").write_text(
            """@gd.route_function
async def should_be_skipped():
    pass
"""
        )

        registry = discover_routes(str(routes_dir))

        # __init__.py should be skipped
        assert "should_be_skipped" not in registry.routes

    def test_discover_routes_handles_async_functions(self, tmp_path):
        """Test that async functions are discovered."""
        routes_dir = tmp_path / "routes"
        routes_dir.mkdir()
        module_dir = routes_dir / "test_module"
        module_dir.mkdir()

        route_file = module_dir / "routes.py"
        route_file.write_text(
            '''import domolibrary2.routes.get_data as gd

@gd.route_function
async def async_route():
    """Async route."""
    pass
'''
        )

        registry = discover_routes(str(routes_dir))

        assert "async_route" in registry.routes
