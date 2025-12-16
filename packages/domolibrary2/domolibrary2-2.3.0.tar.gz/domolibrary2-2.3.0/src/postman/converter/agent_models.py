# agent_models.py - Pydantic models for agent outputs


from pydantic import BaseModel, Field


class ConversionPlan(BaseModel):
    """Output model for Orchestrator Agent."""

    collection_name: str
    total_requests: int
    processing_strategy: str = Field(description="sequential or parallel")
    estimated_complexity: str = Field(description="low, medium, high")
    next_step: str


class ParsedCollection(BaseModel):
    """Output model for Parser Agent."""

    collection: dict = Field(description="Parsed PostmanCollection as dict")
    total_requests: int
    folder_structure: list[str] = Field(description="List of folder paths")
    parsing_issues: list[str] = Field(default_factory=list)
    collection_variables: dict[str, str]
    collection_auth: dict | None = None


class ValidationReport(BaseModel):
    """Output model for Validation Agent."""

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    passed_checks: list[str] = Field(default_factory=list)


class StructureAnalysis(BaseModel):
    """Output model for Structure Analyzer Agent."""

    folder_hierarchy: dict[str, list[str]]
    request_groupings: dict[str, list[str]]
    naming_patterns: list[str] = Field(description="Identified naming conventions")
    suggested_module_structure: dict[str, list[str]]
    complexity_score: int = Field(ge=1, le=10)


class AuthAnalysis(BaseModel):
    """Output model for Authentication Analyzer Agent."""

    auth_types: list[str] = Field(
        description="Types of auth used: bearer, basic, apikey, etc."
    )
    auth_locations: list[str] = Field(description="collection, folder, request")
    requires_token_refresh: bool
    auth_variables: list[str] = Field(description="Variables used in auth")
    suggested_auth_class: str = Field(description="Recommended auth class name")
    auth_implementation_notes: str


class ParameterAnalysis(BaseModel):
    """Output model for Parameter Analyzer Agent."""

    common_params: dict[str, list[str]] = Field(
        description="Parameters used across multiple requests"
    )
    required_params: dict[str, list[str]] = Field(
        description="Request name to required params"
    )
    optional_params: dict[str, list[str]] = Field(
        description="Request name to optional params"
    )
    param_types: dict[str, str] = Field(description="Inferred parameter types")
    default_values: dict[str, str] = Field(description="Default values for params")
    path_variables: dict[str, list[str]] = Field(
        description="Path variables per request"
    )


class HeaderAnalysis(BaseModel):
    """Output model for Header Analyzer Agent."""

    common_headers: dict[str, list[str]] = Field(
        description="Headers used across requests"
    )
    required_headers: list[str] = Field(description="Headers needed for all requests")
    optional_headers: dict[str, list[str]] = Field(
        description="Request-specific headers"
    )
    header_variables: list[str] = Field(description="Variables in header values")
    content_types: list[str] = Field(description="Content-Type values found")
    auth_headers: list[str] = Field(description="Headers used for authentication")


class AggregatedAnalysis(BaseModel):
    """Output model for Analysis Aggregator Agent."""

    structure: dict = Field(description="From Structure Analyzer")
    authentication: dict = Field(description="From Auth Analyzer")
    parameters: dict = Field(description="From Parameter Analyzer")
    headers: dict = Field(description="From Header Analyzer")

    code_generation_strategy: str = Field(description="Recommended approach")
    module_organization: dict[str, list[str]]
    shared_components: list[str] = Field(description="Components to generate once")
    per_request_customization: dict[str, dict]
    complexity_assessment: str


class GeneratedCode(BaseModel):
    """Output model for Code Generator Agent."""

    function_name: str
    function_code: str = Field(description="Complete Python function code")
    imports_needed: list[str] = Field(description="Import statements required")
    dependencies: list[str] = Field(description="Other functions this depends on")
    docstring: str
    type_hints: dict[str, str] = Field(description="Parameter name to type hint")
    complexity: str = Field(description="low, medium, high")


class GeneratedTests(BaseModel):
    """Output model for Test Generator Agent."""

    test_function_name: str
    test_code: str = Field(description="Complete test function code")
    test_fixtures: list[str] = Field(description="Fixtures needed")
    mock_data: dict = Field(description="Mock data for testing")
    assertions: list[str] = Field(description="Key assertions made")
    test_coverage_areas: list[str] = Field(description="What aspects are tested")


class CodeValidationResult(BaseModel):
    """Output model for Code Validator Agent."""

    is_valid: bool
    syntax_errors: list[str] = Field(default_factory=list)
    type_errors: list[str] = Field(default_factory=list)
    style_issues: list[str] = Field(default_factory=list)
    security_concerns: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    passed_checks: list[str] = Field(default_factory=list)


class FormattedCode(BaseModel):
    """Output model for Code Formatter Agent."""

    formatted_function: str
    formatted_tests: str
    imports_block: str
    file_header: str = Field(description="Module docstring and metadata")
    changes_made: list[str] = Field(description="Formatting changes applied")


class MatchValidationResult(BaseModel):
    """Output model for Route Matcher Agent."""

    is_valid_match: bool
    confidence_adjusted: float = Field(
        description="Adjusted confidence score after agent review", ge=0.0, le=1.0
    )
    match_type: str = Field(description="EXACT_MATCH, URL_MATCH, NAME_MATCH, NO_MATCH")
    reasoning: str = Field(description="Agent's reasoning for the validation")
    suggestions: list[str] = Field(
        default_factory=list, description="Suggestions for improving the match"
    )
    should_create_wrapper: bool = Field(
        description="Whether a wrapper should be created for this match"
    )


class GeneratedWrapper(BaseModel):
    """Output model for Wrapper Generator Agent."""

    wrapper_function_name: str
    wrapper_code: str = Field(description="Complete Python wrapper function code")
    imports_needed: list[str] = Field(description="Import statements required")
    docstring: str = Field(description="Wrapper function docstring")
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata about the wrapper",
    )


class DocstringUpdate(BaseModel):
    """Output model for Docstring Updater Agent."""

    updated_docstring: str = Field(
        description="Updated docstring with Postman metadata"
    )
    changes_made: list[str] = Field(description="List of changes made to the docstring")
    postman_reference: str = Field(
        description="Reference to the Postman request that matches this route"
    )
