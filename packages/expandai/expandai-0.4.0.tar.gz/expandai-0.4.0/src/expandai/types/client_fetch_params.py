# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "ClientFetchParams",
    "BrowserConfig",
    "Select",
    "SelectResponse",
    "SelectScreenshot",
    "SelectScreenshotSelectScreenshotConfig",
    "SelectSnippets",
    "SelectSummary",
    "SelectSummaryPrompt",
]


class ClientFetchParams(TypedDict, total=False):
    url: Required[str]
    """a string to be decoded into a URL"""

    browser_config: Annotated[BrowserConfig, PropertyInfo(alias="browserConfig")]
    """Configuration options for browser behavior during the fetch"""

    select: Select
    """Specifies which content formats to include in the response"""


class BrowserConfig(TypedDict, total=False):
    """Configuration options for browser behavior during the fetch"""

    scroll_full_page: Annotated[bool, PropertyInfo(alias="scrollFullPage")]
    """Whether to scroll the entire page to capture lazy-loaded content"""


class SelectResponse(TypedDict, total=False):
    """Configure response info options (headers inclusion)"""

    include_headers: Annotated[bool, PropertyInfo(alias="includeHeaders")]
    """Whether to include HTTP response headers"""


class SelectScreenshotSelectScreenshotConfig(TypedDict, total=False):
    """Options for customizing screenshot capture behavior"""

    full_page: Annotated[bool, PropertyInfo(alias="fullPage")]
    """Whether to capture the full page including content below the fold"""


SelectScreenshot: TypeAlias = Union[bool, SelectScreenshotSelectScreenshotConfig]


class SelectSnippets(TypedDict, total=False):
    """
    Options for extracting relevant snippets from page content using semantic search
    """

    query: Required[str]
    """Query to find relevant content snippets from the page (required, non-empty)"""

    max_snippets: Annotated[int, PropertyInfo(alias="maxSnippets")]
    """Maximum number of snippets to return (1-50)"""

    min_score: Annotated[float, PropertyInfo(alias="minScore")]
    """Minimum relevance score threshold (0-1).

    Snippets below this score are filtered out.
    """

    target_snippet_size: Annotated[int, PropertyInfo(alias="targetSnippetSize")]
    """Target snippet size in characters (100-2000)"""


class SelectSummaryPrompt(TypedDict, total=False):
    """Options for AI-powered page summarization"""

    prompt: str
    """Custom prompt for AI summarization (max 5000 characters)"""


SelectSummary: TypeAlias = Union[bool, SelectSummaryPrompt]


class Select(TypedDict, total=False):
    """Specifies which content formats to include in the response"""

    html: Union[bool, Iterable[object], object]
    """Set to true to include HTML"""

    markdown: Union[bool, Iterable[object], object]
    """Include markdown-formatted content in the response"""

    meta: bool
    """Include page metadata in the response"""

    response: SelectResponse
    """Configure response info options (headers inclusion)"""

    screenshot: SelectScreenshot
    """Set to true to include a screenshot"""

    snippets: SelectSnippets
    """
    Options for extracting relevant snippets from page content using semantic search
    """

    summary: SelectSummary
    """Set to true to generate an AI summary"""
