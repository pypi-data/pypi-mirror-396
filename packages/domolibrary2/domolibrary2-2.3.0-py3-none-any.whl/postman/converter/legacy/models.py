import json
from dataclasses import dataclass, field
from typing import Any, Optional, Union


@dataclass
class PostmanRequest_Header:
    """Represents an HTTP header in a request or response.

    Attributes:
        key (str): The name of the header (e.g., 'content-type', 'authorization')
        value (str): The value of the header
        disabled (bool): Whether the header is disabled
        description (str): Header description
        type (str): Type of header (e.g., 'text')
    """

    key: str
    value: str
    disabled: bool = False
    description: str | None = None
    type: str | None = None

    @classmethod
    def from_dict(cls, header_data: dict[str, Any]) -> "PostmanRequest_Header":
        """Create a PostmanRequest_Header from header data.

        Args:
            header_data (dict[str, Any]): Dictionary containing header key and value

        Returns:
            PostmanRequest_Header: A new header instance
        """
        return cls(
            key=header_data["key"].lower(),
            value=header_data["value"],
            disabled=header_data.get("disabled", False),
            description=header_data.get("description"),
            type=header_data.get("type"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"key": self.key, "value": self.value}
        if self.disabled:
            result["disabled"] = self.disabled
        if self.description:
            result["description"] = self.description
        if self.type:
            result["type"] = self.type
        return result


@dataclass
class PostmanQueryParam:
    """Represents a URL query parameter.

    Attributes:
        key (str): The parameter name
        value (str): The parameter value
        disabled (bool): Whether the parameter is disabled
        description (str): Parameter description
    """

    key: str
    value: str
    disabled: bool = False
    description: str | None = None

    @classmethod
    def from_dict(cls, param_data: dict[str, Any]) -> "PostmanQueryParam":
        """Create a PostmanQueryParam from parameter data.

        Args:
            param_data (dict[str, Any]): Dictionary containing parameter key and value

        Returns:
            PostmanQueryParam: A new query parameter instance
        """
        return cls(
            key=param_data["key"],
            value=param_data["value"],
            disabled=param_data.get("disabled", False),
            description=param_data.get("description"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"key": self.key, "value": self.value}
        if self.disabled:
            result["disabled"] = self.disabled
        if self.description:
            result["description"] = self.description
        return result


@dataclass
class PostmanVariable:
    """Represents a Postman variable.

    Attributes:
        key (str): The variable name
        value (str): The variable value
        type (str): The variable type (e.g., 'string', 'boolean')
    """

    key: str
    value: str = ""
    type: str = "string"

    @classmethod
    def from_dict(cls, var_data: dict[str, Any]) -> "PostmanVariable":
        """Create a PostmanVariable from variable data."""
        return cls(
            key=var_data["key"],
            value=var_data.get("value", ""),
            type=var_data.get("type", "string"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"key": self.key, "value": self.value}
        if self.type != "string":
            result["type"] = self.type
        return result


@dataclass
class PostmanScript:
    """Represents a Postman script (prerequest or test).

    Attributes:
        type (str): Script type (e.g., 'text/javascript')
        exec (list[str]): List of script lines
    """

    type: str = "text/javascript"
    exec: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, script_data: dict[str, Any]) -> "PostmanScript":
        """Create a PostmanScript from script data."""
        return cls(
            type=script_data.get("type", "text/javascript"),
            exec=script_data.get("exec", []),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {"type": self.type, "exec": self.exec}


@dataclass
class PostmanEvent:
    """Represents a Postman event (prerequest or test).

    Attributes:
        listen (str): Event type ('prerequest' or 'test')
        script (PostmanScript): The script to execute
    """

    listen: str
    script: PostmanScript

    @classmethod
    def from_dict(cls, event_data: dict[str, Any]) -> "PostmanEvent":
        """Create a PostmanEvent from event data."""
        return cls(
            listen=event_data["listen"],
            script=PostmanScript.from_dict(event_data.get("script", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {"listen": self.listen, "script": self.script.to_dict()}


@dataclass
class PostmanAuth:
    """Represents Postman authentication configuration.

    Attributes:
        type (str): Authentication type (e.g., 'bearer', 'basic', 'apikey')
        bearer (list[Dict]): Bearer token configuration
        basic (list[Dict]): Basic auth configuration
        apikey (list[Dict]): API key configuration
    """

    type: str | None = None
    bearer: list[dict[str, Any]] | None = None
    basic: list[dict[str, Any]] | None = None
    apikey: list[dict[str, Any]] | None = None

    @classmethod
    def from_dict(cls, auth_data: dict[str, Any] | None) -> Optional["PostmanAuth"]:
        """Create a PostmanAuth from auth data."""
        if not auth_data:
            return None

        return cls(
            type=auth_data.get("type"),
            bearer=auth_data.get("bearer"),
            basic=auth_data.get("basic"),
            apikey=auth_data.get("apikey"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {}
        if self.type:
            result["type"] = self.type
        if self.bearer:
            result["bearer"] = self.bearer
        if self.basic:
            result["basic"] = self.basic
        if self.apikey:
            result["apikey"] = self.apikey
        return result


@dataclass
class PostmanUrl:
    """Represents a complete URL with all its components.

    Attributes:
        raw (str): The complete URL as a string
        protocol (str): The protocol (e.g., 'http', 'https')
        host (list[str]): The host components (e.g., ['api', 'example', 'com'])
        path (list[str]): The path components
        query (Optional[list[PostmanQueryParam]]): List of query parameters, if any
        variable (Optional[list[PostmanVariable]]): List of URL variables
    """

    raw: str
    protocol: str | None = None
    host: list[str] | None = None
    path: list[str] | None = None
    query: list[PostmanQueryParam] | None = None
    variable: list[PostmanVariable] | None = None

    @classmethod
    def from_dict(cls, url_data: dict[str, Any]) -> "PostmanUrl":
        """Create a PostmanUrl from URL data.

        Args:
            url_data (dict[str, Any]): Dictionary containing URL components

        Returns:
            PostmanUrl: A new URL instance
        """
        return cls(
            raw=url_data["raw"],
            protocol=url_data.get("protocol"),
            host=url_data.get("host"),
            path=url_data.get("path"),
            query=(
                [PostmanQueryParam.from_dict(q) for q in url_data.get("query", [])]
                if url_data.get("query")
                else None
            ),
            variable=(
                [PostmanVariable.from_dict(v) for v in url_data.get("variable", [])]
                if url_data.get("variable")
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"raw": self.raw}
        if self.protocol:
            result["protocol"] = self.protocol
        if self.host:
            result["host"] = self.host
        if self.path:
            result["path"] = self.path
        if self.query:
            result["query"] = [q.to_dict() for q in self.query]
        if self.variable:
            result["variable"] = [v.to_dict() for v in self.variable]
        return result


@dataclass
class PostmanRequest_Body:
    """Represents the body of an HTTP request.

    Attributes:
        mode (str): The mode of the body (e.g., 'raw', 'formdata', 'urlencoded')
        raw (str): The actual content of the body
        options (Dict): Body options (e.g., raw language settings)
        formdata (List): Form data fields
        urlencoded (List): URL encoded fields
    """

    mode: str
    raw: str | None = None
    options: dict[str, Any] | None = None
    formdata: list[dict[str, Any]] | None = None
    urlencoded: list[dict[str, Any]] | None = None

    @classmethod
    def from_dict(
        cls, body_data: dict[str, Any] | None
    ) -> Optional["PostmanRequest_Body"]:
        """Create a PostmanRequest_Body from body data.

        Args:
            body_data (Optional[dict[str, Any]]): Dictionary containing body data

        Returns:
            Optional[PostmanRequest_Body]: A new body instance or None if no body data
        """
        if not body_data:
            return None
        return cls(
            mode=body_data["mode"],
            raw=body_data.get("raw"),
            options=body_data.get("options"),
            formdata=body_data.get("formdata"),
            urlencoded=body_data.get("urlencoded"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"mode": self.mode}
        if self.raw:
            result["raw"] = self.raw
        if self.options:
            result["options"] = self.options
        if self.formdata:
            result["formdata"] = self.formdata
        if self.urlencoded:
            result["urlencoded"] = self.urlencoded
        return result


@dataclass
class PostmanResponse:
    """Represents an HTTP response in a Postman collection.

    Attributes:
        name (str): Name of the response example
        originalRequest (Dict): The original request that generated this response
        status (str): HTTP status text (e.g., 'OK')
        code (int): HTTP status code (e.g., 200)
        header (list[PostmanRequest_Header]): Response headers
        cookie (List): Response cookies
        body (str): Response body content
        _postman_previewlanguage (str): Preview language (e.g., 'json', 'html')
    """

    name: str | None = None
    originalRequest: dict[str, Any] | None = None
    status: str | None = None
    code: int | None = None
    header: list[PostmanRequest_Header] | None = None
    cookie: list[dict[str, Any]] | None = None
    body: str | None = None
    _postman_previewlanguage: str | None = None

    @classmethod
    def from_dict(cls, response_data: dict[str, Any]) -> "PostmanResponse":
        """Create a PostmanResponse from response data."""
        headers = None
        if response_data.get("header"):
            headers = [
                PostmanRequest_Header.from_dict(h) for h in response_data["header"]
            ]

        return cls(
            name=response_data.get("name"),
            originalRequest=response_data.get("originalRequest"),
            status=response_data.get("status"),
            code=response_data.get("code"),
            header=headers,
            cookie=response_data.get("cookie"),
            body=response_data.get("body"),
            _postman_previewlanguage=response_data.get("_postman_previewlanguage"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {}
        if self.name:
            result["name"] = self.name
        if self.originalRequest:
            result["originalRequest"] = self.originalRequest
        if self.status:
            result["status"] = self.status
        if self.code:
            result["code"] = self.code
        if self.header:
            result["header"] = [h.to_dict() for h in self.header]
        if self.cookie:
            result["cookie"] = self.cookie
        if self.body:
            result["body"] = self.body
        if self._postman_previewlanguage:
            result["_postman_previewlanguage"] = self._postman_previewlanguage
        return result


@dataclass
class PostmanRequest:
    """Represents a single request in a Postman collection.

    A request typically represents a single API endpoint with its request
    and response details.

    Attributes:
        name (str): The name of the request
        method (str): The HTTP method (e.g., 'GET', 'POST', 'PUT')
        header (list[PostmanRequest_Header]): List of HTTP headers
        url (PostmanUrl): The request URL
        body (Optional[PostmanRequest_Body]): The request body, if any
        response (list[PostmanResponse]): List of example responses
        auth (Optional[PostmanAuth]): Authentication configuration
        event (Optional[list[PostmanEvent]]): Request-level events
        description (Optional[str]): Request description
        variable (Optional[list[PostmanVariable]]): Request-level variables
    """

    name: str
    method: str
    header: list[PostmanRequest_Header]
    url: PostmanUrl
    body: PostmanRequest_Body | None = None
    response: list[PostmanResponse] = field(default_factory=list)
    auth: PostmanAuth | None = None
    event: list[PostmanEvent] | None = None
    description: str | None = None
    variable: list[PostmanVariable] | None = None

    @classmethod
    def from_dict(cls, item_data: dict[str, Any]) -> "PostmanRequest":
        """Create a PostmanRequest from item data.

        Args:
            item_data (dict[str, Any]): Dictionary containing request data

        Returns:
            PostmanRequest: A new request instance
        """
        request_data = item_data["request"]

        # Handle responses
        responses = []
        if item_data.get("response"):
            responses = [PostmanResponse.from_dict(r) for r in item_data["response"]]

        # Handle events
        events = None
        if item_data.get("event"):
            events = [PostmanEvent.from_dict(e) for e in item_data["event"]]

        # Handle variables
        variables = None
        if item_data.get("variable"):
            variables = [PostmanVariable.from_dict(v) for v in item_data["variable"]]

        return cls(
            name=item_data["name"],
            method=request_data["method"],
            header=[
                PostmanRequest_Header.from_dict(h)
                for h in request_data.get("header", [])
            ],
            url=PostmanUrl.from_dict(request_data["url"]),
            body=PostmanRequest_Body.from_dict(request_data.get("body")),
            response=responses,
            auth=PostmanAuth.from_dict(request_data.get("auth")),
            event=events,
            description=item_data.get("description"),
            variable=variables,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation for validation."""
        request_data = {
            "method": self.method,
            "header": [h.to_dict() for h in self.header],
            "url": self.url.to_dict(),
        }

        if self.body:
            request_data["body"] = self.body.to_dict()
        if self.auth:
            request_data["auth"] = self.auth.to_dict()

        result = {"name": self.name, "request": request_data}

        if self.response:
            result["response"] = [r.to_dict() for r in self.response]
        if self.event:
            result["event"] = [e.to_dict() for e in self.event]
        if self.description:
            result["description"] = self.description
        if self.variable:
            result["variable"] = [v.to_dict() for v in self.variable]

        return result


@dataclass
class PostmanFolder:
    """Represents a folder in a Postman collection that can contain other items.

    Attributes:
        name (str): Name of the folder
        item (list[Union['PostmanFolder', 'PostmanRequest']]): Items in the folder
        description (Optional[str]): Folder description
        auth (Optional[PostmanAuth]): Folder-level authentication
        event (Optional[list[PostmanEvent]]): Folder-level events
        variable (Optional[list[PostmanVariable]]): Folder-level variables
    """

    name: str
    item: list[Union["PostmanFolder", "PostmanRequest"]] = field(default_factory=list)
    description: str | None = None
    auth: PostmanAuth | None = None
    event: list[PostmanEvent] | None = None
    variable: list[PostmanVariable] | None = None

    @classmethod
    def from_dict(cls, folder_data: dict[str, Any]) -> "PostmanFolder":
        """Create a PostmanFolder from folder data."""
        items = []
        for item_data in folder_data.get("item", []):
            if "request" in item_data:
                items.append(PostmanRequest.from_dict(item_data))
            else:
                items.append(PostmanFolder.from_dict(item_data))

        events = None
        if folder_data.get("event"):
            events = [PostmanEvent.from_dict(e) for e in folder_data["event"]]

        variables = None
        if folder_data.get("variable"):
            variables = [PostmanVariable.from_dict(v) for v in folder_data["variable"]]

        return cls(
            name=folder_data["name"],
            item=items,
            description=folder_data.get("description"),
            auth=PostmanAuth.from_dict(folder_data.get("auth")),
            event=events,
            variable=variables,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"name": self.name, "item": [item.to_dict() for item in self.item]}

        if self.description:
            result["description"] = self.description
        if self.auth:
            result["auth"] = self.auth.to_dict()
        if self.event:
            result["event"] = [e.to_dict() for e in self.event]
        if self.variable:
            result["variable"] = [v.to_dict() for v in self.variable]

        return result

    def get_all_requests(self) -> list[PostmanRequest]:
        """Recursively get all requests from this folder and subfolders."""
        requests = []
        for item in self.item:
            if isinstance(item, PostmanRequest):
                requests.append(item)
            elif isinstance(item, PostmanFolder):
                requests.extend(item.get_all_requests())
        return requests


@dataclass
class PostmanCollectionInfo:
    """Contains metadata about the Postman collection.

    Attributes:
        _postman_id (str): Unique identifier for the collection
        name (str): Name of the collection
        schema (str): The schema version used by the collection
        _exporter_id (str): ID of the exporter that created the collection
        _collection_link (str): Link to the collection in Postman
        description (str): Collection description
    """

    _postman_id: str
    name: str
    schema: str
    _exporter_id: str | None = None
    _collection_link: str | None = None
    description: str | None = None

    @classmethod
    def from_dict(cls, info_data: dict[str, Any]) -> "PostmanCollectionInfo":
        """Create a PostmanCollectionInfo from info data.

        Args:
            info_data (dict[str, Any]): Dictionary containing collection info

        Returns:
            PostmanCollectionInfo: A new info instance
        """
        return cls(
            _postman_id=info_data["_postman_id"],
            name=info_data["name"],
            schema=info_data["schema"],
            _exporter_id=info_data.get("_exporter_id"),
            _collection_link=info_data.get("_collection_link"),
            description=info_data.get("description"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "_postman_id": self._postman_id,
            "name": self.name,
            "schema": self.schema,
        }

        if self._exporter_id:
            result["_exporter_id"] = self._exporter_id
        if self._collection_link:
            result["_collection_link"] = self._collection_link
        if self.description:
            result["description"] = self.description

        return result


@dataclass
class PostmanCollection:
    """Represents a complete Postman collection.

    This is the root class that contains all the information about
    a Postman collection, including its metadata, folders, requests,
    variables, events, and authentication configuration.

    Attributes:
        info (PostmanCollectionInfo): Collection metadata
        item (list[Union[PostmanRequest, PostmanFolder]]): Collection items (requests and folders)
        auth (Optional[PostmanAuth]): Collection-level authentication
        event (Optional[list[PostmanEvent]]): Collection-level events
        variable (Optional[list[PostmanVariable]]): Collection-level variables
        requests (list[PostmanRequest]): Flat list of all requests (computed property)
    """

    info: PostmanCollectionInfo
    item: list[PostmanRequest | PostmanFolder] = field(default_factory=list)
    auth: PostmanAuth | None = None
    event: list[PostmanEvent] | None = None
    variable: list[PostmanVariable] | None = None

    @property
    def requests(self) -> list[PostmanRequest]:
        """Get a flat list of all requests in the collection."""
        requests = []

        def extract_requests(items):
            for item in items:
                if isinstance(item, PostmanRequest):
                    requests.append(item)
                elif isinstance(item, PostmanFolder):
                    extract_requests(item.item)

        extract_requests(self.item)
        return requests

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PostmanCollection":
        """Creates a PostmanCollection object from a JSON dictionary.

        This helper function converts a JSON representation of a Postman
        collection into a structured Python object with proper typing.

        Args:
            data (dict[str, Any]): The JSON data as a Python dictionary

        Returns:
            PostmanCollection: A structured representation of the collection
        """
        info = PostmanCollectionInfo.from_dict(data["info"])

        # Process items (can be requests or folders)
        items = []
        for item_data in data.get("item", []):
            if "request" in item_data:
                # It's a request
                items.append(PostmanRequest.from_dict(item_data))
            else:
                # It's a folder
                items.append(PostmanFolder.from_dict(item_data))

        # Handle collection-level auth
        auth = None
        if data.get("auth"):
            auth = PostmanAuth.from_dict(data["auth"])

        # Handle collection-level events
        events = None
        if data.get("event"):
            events = [PostmanEvent.from_dict(e) for e in data["event"]]

        # Handle collection-level variables
        variables = None
        if data.get("variable"):
            variables = [PostmanVariable.from_dict(v) for v in data["variable"]]

        return cls(info=info, item=items, auth=auth, event=events, variable=variables)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation for validation."""
        result = {
            "info": self.info.to_dict(),
        }

        if self.item:
            result["item"] = [item.to_dict() for item in self.item]
        if self.auth:
            result["auth"] = self.auth.to_dict()
        if self.event:
            result["event"] = [e.to_dict() for e in self.event]
        if self.variable:
            result["variable"] = [v.to_dict() for v in self.variable]

        return result

    @classmethod
    def from_file(cls, file_path: str) -> "PostmanCollection":
        """Load a PostmanCollection from a JSON file.

        Args:
            file_path (str): Path to the Postman collection JSON file

        Returns:
            PostmanCollection: A structured representation of the collection

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file isn't valid JSON
        """

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def list_all_headers(self) -> dict[str, list[str]]:
        """List all unique headers and their values from this collection.

        Returns:
            dict[str, list[str]]: Dictionary where keys are header names and values are lists of unique values
        """
        headers_dict = {}

        for request in self.requests:
            for header in request.header:
                if header.key not in headers_dict:
                    headers_dict[header.key] = set()
                headers_dict[header.key].add(header.value)

        # Convert sets to lists for better serialization
        return {key: list(values) for key, values in headers_dict.items()}

    def list_all_params(self) -> dict[str, list[str]]:
        """List all unique query parameters and their values from this collection.

        Returns:
            dict[str, list[str]]: Dictionary where keys are parameter names and values are lists of unique values
        """
        params_dict = {}

        for request in self.requests:
            if request.url.query:
                for param in request.url.query:
                    if param.key not in params_dict:
                        params_dict[param.key] = set()
                    params_dict[param.key].add(param.value)

        # Convert sets to lists for better serialization
        return {key: list(values) for key, values in params_dict.items()}
