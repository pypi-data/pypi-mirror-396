"""
Client for the Pre.dev Architect API
"""

from typing import Optional, Dict, Any, Literal, List, Union, BinaryIO
from dataclasses import dataclass
import requests
from .exceptions import PredevAPIError, AuthenticationError, RateLimitError


@dataclass
class AsyncResponse:
    """Async mode response class"""
    specId: str
    status: Literal['pending', 'processing', 'completed', 'failed']


@dataclass
class ZippedDocsUrl:
    """Zipped documentation URL class"""
    platform: str
    masterZipShortUrl: str


@dataclass
class SpecCoreFunctionality:
    name: str
    description: str
    priority: Optional[str] = None


@dataclass
class SpecTechStackItem:
    name: str
    category: str


@dataclass
class SpecPersona:
    title: str
    description: str
    primaryGoals: Optional[List[str]] = None
    painPoints: Optional[List[str]] = None
    keyTasks: Optional[List[str]] = None


@dataclass
class SpecRole:
    name: str
    shortHand: str


@dataclass
class CodingAgentSubTask:
    id: Optional[str] = None
    description: str = ""
    complexity: str = ""


@dataclass
class CodingAgentStory:
    id: Optional[str] = None
    title: str = ""
    description: Optional[str] = None
    acceptanceCriteria: Optional[List[str]] = None
    complexity: Optional[str] = None
    subTasks: Optional[List[CodingAgentSubTask]] = None


@dataclass
class CodingAgentMilestone:
    milestoneNumber: int = 0
    description: str = ""
    stories: Optional[List[CodingAgentStory]] = None


@dataclass
class CodingAgentSpecJson:
    title: Optional[str] = None
    executiveSummary: str = ""
    coreFunctionalities: Optional[List[SpecCoreFunctionality]] = None
    techStack: Optional[List[SpecTechStackItem]] = None
    techStackGrouped: Optional[Dict[str, List[str]]] = None
    milestones: Optional[List[CodingAgentMilestone]] = None


@dataclass
class HumanSpecSubTask:
    id: Optional[str] = None
    description: str = ""
    hours: float = 0
    complexity: str = ""
    roles: Optional[List[SpecRole]] = None


@dataclass
class HumanSpecStory:
    id: Optional[str] = None
    title: str = ""
    description: Optional[str] = None
    acceptanceCriteria: Optional[List[str]] = None
    hours: float = 0
    complexity: Optional[str] = None
    subTasks: Optional[List[HumanSpecSubTask]] = None


@dataclass
class HumanSpecMilestone:
    milestoneNumber: int = 0
    description: str = ""
    hours: float = 0
    stories: Optional[List[HumanSpecStory]] = None


@dataclass
class HumanSpecJson:
    title: Optional[str] = None
    executiveSummary: str = ""
    coreFunctionalities: Optional[List[SpecCoreFunctionality]] = None
    personas: Optional[List[SpecPersona]] = None
    techStack: Optional[List[SpecTechStackItem]] = None
    techStackGrouped: Optional[Dict[str, List[str]]] = None
    milestones: Optional[List[HumanSpecMilestone]] = None
    totalHours: Optional[float] = None
    roles: Optional[List[SpecRole]] = None


@dataclass
class SpecResponse:
    """Status check response class"""
    _id: Optional[str] = None
    created: Optional[str] = None

    endpoint: Optional[Literal['fast_spec', 'deep_spec']] = None
    input: Optional[str] = None
    status: Optional[Literal['pending',
                             'processing', 'completed', 'failed']] = None
    success: Optional[bool] = None

    uploadedFileShortUrl: Optional[str] = None
    uploadedFileName: Optional[str] = None
    codingAgentSpecUrl: Optional[str] = None
    humanSpecUrl: Optional[str] = None
    totalHumanHours: Optional[int] = None
    codingAgentSpecJson: Optional['CodingAgentSpecJson'] = None
    codingAgentSpecMarkdown: Optional[str] = None
    humanSpecJson: Optional['HumanSpecJson'] = None
    humanSpecMarkdown: Optional[str] = None
    executionTime: Optional[int] = None

    architectureInfographicUrl: Optional[str] = None

    predevUrl: Optional[str] = None
    lovableUrl: Optional[str] = None
    cursorUrl: Optional[str] = None
    v0Url: Optional[str] = None
    boltUrl: Optional[str] = None

    zippedDocsUrls: Optional[List['ZippedDocsUrl']] = None

    errorMessage: Optional[str] = None
    progress: Optional[int] = None  # Overall progress percentage (0-100)
    progressMessage: Optional[str] = None  # Detailed progress message (e.g., "Generating User Stories...")


@dataclass
class ErrorResponse:
    """Error response class"""
    error: str
    message: str


@dataclass
class ListSpecsResponse:
    """List/Find specs response class"""
    specs: List['SpecResponse']
    total: int
    hasMore: bool


@dataclass
class CreditsBalanceResponse:
    """Credits balance response class"""
    success: bool
    creditsRemaining: int


class PredevAPI:
    """
    Client for interacting with the Pre.dev Architect API.

    The API offers two main endpoints:
    - Fast Spec: Generate comprehensive specs quickly (ideal for MVPs and prototypes)
    - Deep Spec: Generate ultra-detailed specs for complex systems (enterprise-grade depth)

    Args:
        api_key: Your API key from pre.dev settings
        base_url: Base URL for the API (default: https://api.pre.dev)

    Example:
        >>> from predev_api import PredevAPI
        >>> client = PredevAPI(api_key="your_api_key")
        >>> result = client.fast_spec("Build a task management app")
        >>> print(result)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.pre.dev"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

        # Set up headers with Authorization Bearer token
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def fast_spec(
        self,
        input_text: str,
        current_context: Optional[str] = None,
        doc_urls: Optional[List[str]] = None,
        file: Optional[Union[str, BinaryIO]] = None
    ) -> SpecResponse:
        """
        Generate a fast specification for your project.

        Perfect for MVPs and prototypes with balanced depth and speed.

        Args:
            input_text: Description of the project or feature to generate specs for
            current_context: Existing project/codebase context. When omitted, generates
                           full new project spec. When provided, generates feature addition spec.
            doc_urls: Array of documentation URLs to reference (e.g., API docs, design systems)
            file: Optional file to upload (file path as string or file-like object)

        Returns:
            API response as SpecResponse object

        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            PredevAPIError: For other API errors

        Example:
            >>> client = PredevAPI(api_key="your_key")
            >>> result = client.fast_spec(
            ...     input_text="Build a task management app with team collaboration",
            ...     file="path/to/architecture.pdf"
            ... )
        """
        return self._make_request(
            endpoint="/fast-spec",
            input_text=input_text,
            current_context=current_context,
            doc_urls=doc_urls,
            file=file
        )

    def deep_spec(
        self,
        input_text: str,
        current_context: Optional[str] = None,
        doc_urls: Optional[List[str]] = None,
        file: Optional[Union[str, BinaryIO]] = None
    ) -> SpecResponse:
        """
        Generate a deep specification for your project.

        Ultra-detailed specifications for complex systems with enterprise-grade depth
        and comprehensive analysis.

        Args:
            input_text: Description of the project or feature to generate specs for
            current_context: Existing project/codebase context. When omitted, generates
                           full new project spec. When provided, generates feature addition spec.
            doc_urls: Array of documentation URLs to reference (e.g., API docs, design systems)
            file: Optional file to upload (file path as string or file-like object)

        Returns:
            API response as SpecResponse object

        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            PredevAPIError: For other API errors

        Example:
            >>> client = PredevAPI(api_key="your_key")
            >>> result = client.deep_spec(
            ...     input_text="Build an enterprise resource planning system",
            ...     file="path/to/requirements.doc"
            ... )
        """
        return self._make_request(
            endpoint="/deep-spec",
            input_text=input_text,
            current_context=current_context,
            doc_urls=doc_urls,
            file=file
        )

    def fast_spec_async(
        self,
        input_text: str,
        current_context: Optional[str] = None,
        doc_urls: Optional[List[str]] = None,
        file: Optional[Union[str, BinaryIO]] = None
    ) -> AsyncResponse:
        """
        Generate a fast specification asynchronously for your project.

        Perfect for MVPs and prototypes with balanced depth and speed.
        Returns immediately with a request ID for polling the status.

        Args:
            input_text: Description of the project or feature to generate specs for
            current_context: Existing project/codebase context. When omitted, generates
                           full new project spec. When provided, generates feature addition spec.
            doc_urls: Array of documentation URLs to reference (e.g., API docs, design systems)
            file: Optional file to upload (file path as string or file-like object)

        Returns:
            API response as AsyncResponse object with specId for polling

        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            PredevAPIError: For other API errors

        Example:
            >>> client = PredevAPI(api_key="your_key")
            >>> result = client.fast_spec_async(
            ...     input_text="Build a task management app with team collaboration",
            ...     file="path/to/architecture.pdf"
            ... )
            >>> # Poll for status using result.specId
            >>> status = client.get_spec_status(result.specId)
        """
        return self._make_request_async(
            endpoint="/fast-spec",
            input_text=input_text,
            current_context=current_context,
            doc_urls=doc_urls,
            file=file
        )

    def deep_spec_async(
        self,
        input_text: str,
        current_context: Optional[str] = None,
        doc_urls: Optional[List[str]] = None,
        file: Optional[Union[str, BinaryIO]] = None
    ) -> AsyncResponse:
        """
        Generate a deep specification asynchronously for your project.

        Ultra-detailed specifications for complex systems with enterprise-grade depth
        and comprehensive analysis. Returns immediately with a request ID for polling the status.

        Args:
            input_text: Description of the project or feature to generate specs for
            current_context: Existing project/codebase context. When omitted, generates
                           full new project spec. When provided, generates feature addition spec.
            doc_urls: Array of documentation URLs to reference (e.g., API docs, design systems)
            file: Optional file to upload (file path as string or file-like object)

        Returns:
            API response as AsyncResponse object with specId for polling

        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            PredevAPIError: For other API errors

        Example:
            >>> client = PredevAPI(api_key="your_key")
            >>> result = client.deep_spec_async(
            ...     input_text="Build an enterprise resource planning system",
            ...     file="path/to/requirements.doc"
            ... )
            >>> # Poll for status using result.specId
            >>> status = client.get_spec_status(result.specId)
        """
        return self._make_request_async(
            endpoint="/deep-spec",
            input_text=input_text,
            current_context=current_context,
            doc_urls=doc_urls,
            file=file
        )

    def get_spec_status(self, spec_id: str) -> SpecResponse:
        """
        Get the status of an async specification generation request.

        Args:
            spec_id: The ID of the specification request

        Returns:
            API response with status information

        Raises:
            AuthenticationError: If authentication fails
            PredevAPIError: For other API errors

        Example:
            >>> client = PredevAPI(api_key="your_key")
            >>> status = client.get_spec_status("spec_123")
        """
        url = f"{self.base_url}/spec-status/{spec_id}"

        try:
            response = requests.get(url, headers=self.headers, timeout=60)
            self._handle_response(response)
            return response.json()
        except requests.RequestException as e:
            raise PredevAPIError(f"Request failed: {str(e)}") from e

    def list_specs(
        self,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        endpoint: Optional[Literal['fast_spec', 'deep_spec']] = None,
        status: Optional[Literal['pending',
                                 'processing', 'completed', 'failed']] = None
    ) -> ListSpecsResponse:
        """
        List all specs with optional filtering and pagination.

        Args:
            limit: Results per page (1-100, default: 20)
            skip: Offset for pagination (default: 0)
            endpoint: Filter by endpoint type
            status: Filter by status

        Returns:
            ListSpecsResponse with specs array and pagination metadata

        Raises:
            AuthenticationError: If authentication fails
            PredevAPIError: For other API errors

        Example:
            >>> client = PredevAPI(api_key="your_key")
            >>> # Get first 20 specs
            >>> result = client.list_specs()
            >>> # Get completed specs only
            >>> completed = client.list_specs(status='completed')
            >>> # Paginate: get specs 20-40
            >>> page2 = client.list_specs(skip=20, limit=20)
        """
        url = f"{self.base_url}/list-specs"
        params = {}

        if limit is not None:
            params['limit'] = limit
        if skip is not None:
            params['skip'] = skip
        if endpoint is not None:
            params['endpoint'] = endpoint
        if status is not None:
            params['status'] = status

        try:
            response = requests.get(
                url, headers=self.headers, params=params, timeout=60)
            self._handle_response(response)
            return response.json()
        except requests.RequestException as e:
            raise PredevAPIError(f"Request failed: {str(e)}") from e

    def find_specs(
        self,
        query: str,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        endpoint: Optional[Literal['fast_spec', 'deep_spec']] = None,
        status: Optional[Literal['pending',
                                 'processing', 'completed', 'failed']] = None
    ) -> ListSpecsResponse:
        """
        Search for specs using regex patterns.

        Args:
            query: REQUIRED - Regex pattern (case-insensitive)
            limit: Results per page (1-100, default: 20)
            skip: Offset for pagination (default: 0)
            endpoint: Filter by endpoint type
            status: Filter by status

        Returns:
            ListSpecsResponse with matching specs and pagination metadata

        Raises:
            AuthenticationError: If authentication fails
            PredevAPIError: For other API errors

        Example:
            >>> client = PredevAPI(api_key="your_key")
            >>> # Search for "payment" specs
            >>> result = client.find_specs(query='payment')
            >>> # Search for specs starting with "Build"
            >>> builds = client.find_specs(query='^Build')
            >>> # Search: only completed specs mentioning "auth"
            >>> auth = client.find_specs(query='auth', status='completed')
        """
        url = f"{self.base_url}/find-specs"
        params = {'query': query}

        if limit is not None:
            params['limit'] = limit
        if skip is not None:
            params['skip'] = skip
        if endpoint is not None:
            params['endpoint'] = endpoint
        if status is not None:
            params['status'] = status

        try:
            response = requests.get(
                url, headers=self.headers, params=params, timeout=60)
            self._handle_response(response)
            return response.json()
        except requests.RequestException as e:
            raise PredevAPIError(f"Request failed: {str(e)}") from e

    def get_credits_balance(self) -> CreditsBalanceResponse:
        """
        Get the current credits balance for the API key.

        Returns:
            CreditsBalanceResponse with credits remaining

        Raises:
            AuthenticationError: If authentication fails
            PredevAPIError: For other API errors

        Example:
            >>> client = PredevAPI(api_key="your_key")
            >>> balance = client.get_credits_balance()
            >>> print(balance.creditsRemaining)
        """
        url = f"{self.base_url}/credits-balance"

        try:
            response = requests.get(url, headers=self.headers, timeout=60)
            self._handle_response(response)
            data = response.json()
            return CreditsBalanceResponse(success=data['success'], creditsRemaining=data['creditsRemaining'])
        except requests.RequestException as e:
            raise PredevAPIError(f"Request failed: {str(e)}") from e

    def _make_request(
        self,
        endpoint: str,
        input_text: str,
        current_context: Optional[str] = None,
        doc_urls: Optional[List[str]] = None,
        file: Optional[Union[str, BinaryIO]] = None
    ) -> SpecResponse:
        """Make a POST request to the API."""
        url = f"{self.base_url}{endpoint}"

        if file:
            return self._make_request_with_file(url, input_text, current_context, doc_urls, file)

        payload = {
            "input": input_text
        }

        if current_context is not None:
            payload["currentContext"] = current_context

        if doc_urls is not None:
            payload["docURLs"] = doc_urls

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=300
            )
            self._handle_response(response)
            return response.json()
        except requests.RequestException as e:
            raise PredevAPIError(f"Request failed: {str(e)}") from e

    def _make_request_async(
        self,
        endpoint: str,
        input_text: str,
        current_context: Optional[str] = None,
        doc_urls: Optional[List[str]] = None,
        file: Optional[Union[str, BinaryIO]] = None
    ) -> AsyncResponse:
        """Make an async POST request to the API."""
        url = f"{self.base_url}{endpoint}"

        if file:
            return self._make_request_with_file_async(url, input_text, current_context, doc_urls, file)

        payload = {
            "input": input_text,
            "async": True
        }

        if current_context is not None:
            payload["currentContext"] = current_context

        if doc_urls is not None:
            payload["docURLs"] = doc_urls

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=300
            )
            self._handle_response(response)
            return response.json()
        except requests.RequestException as e:
            raise PredevAPIError(f"Request failed: {str(e)}") from e

    def _make_request_with_file(
        self,
        url: str,
        input_text: str,
        current_context: Optional[str],
        doc_urls: Optional[List[str]],
        file: Union[str, BinaryIO]
    ) -> SpecResponse:
        """Make a POST request with file upload."""
        headers = {key: value for key, value in self.headers.items()
                   if key.lower() != "content-type"}

        data = {
            "input": input_text
        }

        if current_context is not None:
            data["currentContext"] = current_context

        if doc_urls is not None:
            data["docURLs"] = doc_urls

        files = self._prepare_file(file)

        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                files=files,
                timeout=300
            )
            self._handle_response(response)
            return response.json()
        except requests.RequestException as e:
            raise PredevAPIError(f"Request failed: {str(e)}") from e

    def _make_request_with_file_async(
        self,
        url: str,
        input_text: str,
        current_context: Optional[str],
        doc_urls: Optional[List[str]],
        file: Union[str, BinaryIO]
    ) -> AsyncResponse:
        """Make an async POST request with file upload."""
        headers = {key: value for key, value in self.headers.items()
                   if key.lower() != "content-type"}

        data = {
            "input": input_text,
            "async": "true"
        }

        if current_context is not None:
            data["currentContext"] = current_context

        if doc_urls is not None:
            data["docURLs"] = doc_urls

        files = self._prepare_file(file)

        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                files=files,
                timeout=300
            )
            self._handle_response(response)
            return response.json()
        except requests.RequestException as e:
            raise PredevAPIError(f"Request failed: {str(e)}") from e

    def _prepare_file(self, file: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Prepare file for multipart upload."""
        if isinstance(file, str):
            file_handle = open(file, "rb")
            filename = file.split("/")[-1]
            return {"file": (filename, file_handle)}
        else:
            filename = getattr(file, "name", "upload.txt")
            return {"file": (filename, file)}

    def _handle_response(self, response: requests.Response) -> None:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 200:
            return

        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")

        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")

        try:
            error_data = response.json()
            error_message = error_data.get("error") or error_data.get(
                "message") or str(error_data)
        except Exception:
            error_message = response.text or "Unknown error"

        raise PredevAPIError(
            f"API request failed with status {response.status_code}: {error_message}"
        )
