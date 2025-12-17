# pre.dev Architect API - Python Client

A Python client library for the [Pre.dev Architect API](https://docs.pre.dev). Generate comprehensive software specifications using AI-powered analysis.

## Features

- 🚀 **Fast Spec**: Generate comprehensive specifications quickly - perfect for MVPs and prototypes
- 🔍 **Deep Spec**: Generate ultra-detailed specifications for complex systems with enterprise-grade depth
- ⚡ **Async Spec**: Non-blocking async methods for long-running requests
- 📊 **Status Tracking**: Check the status of async specification generation requests
- ✨ **Type Hints**: Full type annotations for better IDE support
- 🛡️ **Error Handling**: Custom exceptions for different error scenarios

## Installation

```bash
pip install predev-api
```

## Quick Start

```python
from predev_api import PredevAPI

# Initialize the predev client with your API key
predev = PredevAPI(api_key="your_api_key_here")

# Generate a fast specification
result = predev.fast_spec(
    input_text="Build a task management app with team collaboration"
)

print(result)
```

## File Upload Support

All `fast_spec`, `deep_spec`, `fast_spec_async`, and `deep_spec_async` methods support optional file uploads. This allows you to provide architecture documents, requirements files, design mockups, or other context files to improve specification generation.

### Using File Path (Simplest)

```python
from predev_api import PredevAPI

predev = PredevAPI(api_key="your_api_key")

# Just pass the file path as a string
result = predev.fast_spec(
    input_text="Generate specs based on these requirements",
    file="path/to/requirements.pdf"
)
```

### Using File-like Objects

```python
# Open and upload a file
with open("architecture.doc", "rb") as f:
    result = predev.deep_spec(
        input_text="Create comprehensive specs",
        file=f
    )

# Or pass a file-like object
from io import BytesIO

file_content = BytesIO(b"Design specifications...")
result = predev.fast_spec(
    input_text="Generate specs",
    file=file_content
)
```

### Supported File Types

- PDF documents (`*.pdf`)
- Word documents (`*.doc`, `*.docx`)
- Text files (`*.txt`)
- Images (`*.jpg`, `*.png`, `*.jpeg`)

### Response with File Upload

When you upload a file, the response includes:

```python
result = predev.fast_spec(
    input_text="Based on the design document",
    file="design.pdf"
)

print(result.uploadedFileName)       # "design.pdf"
print(result.uploadedFileShortUrl)   # "https://api.pre.dev/f/xyz123"
print(result.codingAgentSpecUrl)     # Spec for AI systems
print(result.humanSpecUrl)           # Spec for humans
```

## Authentication

The Pre.dev API uses API key authentication. Get your API key from the [pre.dev dashboard](https://pre.dev) under Settings → API Keys:

```python
predev = PredevAPI(api_key="your_api_key")
```

## API Methods

### Synchronous Methods

#### `fast_spec(input_text: str, current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> SpecResponse`

Generate a fast specification (30-40 seconds, 10 credits).

**Parameters:**
- `input_text` **(required)**: `str` - Description of what you want to build
- `current_context` **(optional)**: `str` - Existing project context
- `doc_urls` **(optional)**: `List[str]` - Documentation URLs to reference (e.g., Stripe docs, framework docs)

**Returns:** `SpecResponse` object with complete specification data

**Example:**
```python
result = predev.fast_spec(
    input_text="Build a SaaS project management tool with real-time collaboration"
)
```

**Example with Documentation URLs:**
```python
result = predev.fast_spec(
    input_text="Build a payment processing integration with Stripe",
    doc_urls=["https://stripe.com/docs/api"]
)

# When doc_urls are provided, the response includes zippedDocsUrls:
# result.zippedDocsUrls = [
#     ZippedDocsUrl(
#         platform="stripe.com",
#         masterZipShortUrl="https://api.pre.dev/s/xyz789"
#     )
# ]
# These zipped documentation folders can be downloaded and help coding agents
# stay on track by providing complete, up-to-date documentation context.
```

#### `deep_spec(input_text: str, current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> SpecResponse`

Generate a deep specification (2-3 minutes, 50 credits).

**Parameters:** Same as `fast_spec`

**Returns:** `SpecResponse` object with comprehensive specification data

**Example:**
```python
result = predev.deep_spec(
    input_text="Build a healthcare platform with HIPAA compliance"
)
```

### Asynchronous Methods

#### `fast_spec_async(input_text: str, current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> AsyncResponse`

Generate a fast specification asynchronously (returns immediately).

**Parameters:** Same as `fast_spec`

**Returns:** `AsyncResponse` object with `specId` for polling

**Example:**
```python
result = predev.fast_spec_async(
    input_text="Build a comprehensive e-commerce platform"
)
# Returns: AsyncResponse(specId="spec_123", status="pending")
```

#### `deep_spec_async(input_text: str, current_context: Optional[str] = None, doc_urls: Optional[List[str]] = None) -> AsyncResponse`

Generate a deep specification asynchronously (returns immediately).

**Parameters:** Same as `fast_spec`

**Returns:** `AsyncResponse` object with `specId` for polling

**Example:**
```python
result = predev.deep_spec_async(
    input_text="Build a fintech platform with regulatory compliance"
)
# Returns: AsyncResponse(specId="spec_456", status="pending")
```

### Status Checking

#### `get_spec_status(spec_id: str) -> SpecResponse`

Check the status of an async specification generation request.

**Parameters:**
- `spec_id` **(required)**: `str` - The specification ID from async methods

**Returns:** `SpecResponse` object with current status and data (when completed)

**Example:**
```python
status = predev.get_spec_status("spec_123")
# Returns SpecResponse with status: "pending" | "processing" | "completed" | "failed"
```

### Listing and Searching Specs

#### `list_specs(limit: Optional[int] = None, skip: Optional[int] = None, endpoint: Optional[Literal["fast_spec", "deep_spec"]] = None, status: Optional[Literal["pending", "processing", "completed", "failed"]] = None) -> ListSpecsResponse`

List all specs with optional filtering and pagination.

**Parameters:**
- `limit` **(optional)**: `int` - Results per page (1-100, default: 20)
- `skip` **(optional)**: `int` - Offset for pagination (default: 0)
- `endpoint` **(optional)**: `"fast_spec" | "deep_spec"` - Filter by endpoint type
- `status` **(optional)**: `"pending" | "processing" | "completed" | "failed"` - Filter by status

**Returns:** `ListSpecsResponse` object with specs array and pagination metadata

**Examples:**
```python
# Get first 20 specs
result = predev.list_specs()

# Get completed specs only
completed = predev.list_specs(status='completed')

# Paginate: get specs 20-40
page2 = predev.list_specs(skip=20, limit=20)

# Filter by endpoint type
fast_specs = predev.list_specs(endpoint='fast_spec')
```

#### `find_specs(query: str, limit: Optional[int] = None, skip: Optional[int] = None, endpoint: Optional[Literal["fast_spec", "deep_spec"]] = None, status: Optional[Literal["pending", "processing", "completed", "failed"]] = None) -> ListSpecsResponse`

Search for specs using regex patterns.

**Parameters:**
- `query` **(required)**: `str` - Regex pattern (case-insensitive)
- `limit` **(optional)**: `int` - Results per page (1-100, default: 20)
- `skip` **(optional)**: `int` - Offset for pagination (default: 0)
- `endpoint` **(optional)**: `"fast_spec" | "deep_spec"` - Filter by endpoint type
- `status` **(optional)**: `"pending" | "processing" | "completed" | "failed"` - Filter by status

**Returns:** `ListSpecsResponse` object with matching specs and pagination metadata

**Examples:**
```python
# Search for "payment" specs
payment_specs = predev.find_specs(query='payment')

# Search for specs starting with "Build"
build_specs = predev.find_specs(query='^Build')

# Search: only completed specs mentioning "auth"
auth_specs = predev.find_specs(
    query='auth',
    status='completed'
)

# Complex regex: find SaaS or SASS projects
saas_specs = predev.find_specs(query='saas|sass')
```

**Regex Pattern Examples:**

| Pattern | Matches |
|---------|---------|
| `payment` | "payment", "Payment", "make payment" |
| `^Build` | Specs starting with "Build" |
| `platform$` | Specs ending with "platform" |
| `(API\|REST)` | Either "API" or "REST" |
| `auth.*system` | "auth" then anything then "system" |
| `\\d{3,}` | 3+ digits (budgets, quantities) |
| `saas\|sass` | SaaS or SASS |

## Response Types

### `AsyncResponse`
```python
@dataclass
class AsyncResponse:
    specId: str                                    # Unique ID for polling (e.g., "spec_abc123")
    status: Literal['pending', 'processing', 'completed', 'failed']
```

### `SpecResponse`
```python
@dataclass
class SpecResponse:
    # Basic info
    _id: Optional[str] = None                      # Internal ID
    created: Optional[str] = None                  # ISO timestamp
    endpoint: Optional[Literal['fast_spec', 'deep_spec']] = None
    input: Optional[str] = None                    # Original input text
    status: Optional[Literal['pending', 'processing', 'completed', 'failed']] = None
    success: Optional[bool] = None

    # Output data (when completed)
    uploadedFileShortUrl: Optional[str] = None    # URL to input file
    uploadedFileName: Optional[str] = None        # Name of input file
    codingAgentSpecUrl: Optional[str] = None      # Spec optimized for AI/LLM systems
    humanSpecUrl: Optional[str] = None            # Spec optimized for human readers
    totalHumanHours: Optional[int] = None         # Estimated hours for human developers
    # Direct returns (new)
    codingAgentSpecJson: Optional[CodingAgentSpecJson] = None   # Simplified JSON for coding tools
    codingAgentSpecMarkdown: Optional[str] = None               # Simplified markdown for coding tools
    humanSpecJson: Optional[HumanSpecJson] = None               # Full JSON with hours/personas/roles
    humanSpecMarkdown: Optional[str] = None                     # Full markdown with all details
    executionTime: Optional[int] = None           # Processing time in milliseconds

    # Integration URLs (when completed)
    predevUrl: Optional[str] = None               # Link to pre.dev project
    lovableUrl: Optional[str] = None              # Link to generate with Lovable
    cursorUrl: Optional[str] = None               # Link to generate with Cursor
    v0Url: Optional[str] = None                   # Link to generate with v0
    boltUrl: Optional[str] = None                 # Link to generate with Bolt

    # Documentation (when doc_urls provided)
    zippedDocsUrls: Optional[List[ZippedDocsUrl]] = None
                                                  # Complete documentation as zipped folders
                                                  # Helps coding agents stay on track with full context
                                                  # Each entry contains platform name and download URL

    # Error handling
    errorMessage: Optional[str] = None            # Error details if failed
    progress: Optional[str] = None                # Progress information
```

### Direct Spec JSON structures
```python
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
```

### `ListSpecsResponse`
```python
@dataclass
class ListSpecsResponse:
    specs: List[SpecResponse]  # Array of spec objects
    total: int                 # Total count of matching specs
    hasMore: bool              # Whether more results are available
```

## Examples Directory

Check out the [examples directory](https://github.com/predotdev/predev-api/tree/main/predev-api-python/examples) for detailed usage examples.

## Documentation

For more information about the Pre.dev Architect API, visit:
- [API Documentation](https://docs.pre.dev)
- [pre.dev Website](https://pre.dev)

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/predotdev/predev-api).
