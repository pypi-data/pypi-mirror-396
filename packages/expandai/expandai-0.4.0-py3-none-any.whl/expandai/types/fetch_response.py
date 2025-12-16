# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "FetchResponse",
    "Data",
    "DataResponse",
    "DataMeta",
    "DataMetaIcon",
    "DataMetaOpenGraph",
    "DataMetaOpenGraphImage",
    "DataMetaTwitter",
    "DataSnippet",
]


class DataResponse(BaseModel):
    """HTTP response information (URL, status code, optionally headers)"""

    status_code: float = FieldInfo(alias="statusCode")
    """HTTP status code of the response"""

    url: str
    """The URL that was fetched"""

    headers: Optional[Dict[str, str]] = None
    """
    Response headers from the fetch operation (keys are lower-cased HTTP header
    names)
    """


class DataMetaIcon(BaseModel):
    """Favicon or app icon metadata from <link> tags"""

    href: str
    """Icon URL or path"""

    rel: str
    """Link relationship type"""

    sizes: Optional[str] = None
    """Icon dimensions"""

    type: Optional[str] = None
    """MIME type of the icon"""


class DataMetaOpenGraphImage(BaseModel):
    """Open Graph image with optional dimensions and alt text"""

    url: str
    """Image URL"""

    alt: Optional[str] = None
    """Image alt text for accessibility"""

    height: Optional[float] = None
    """Image height in pixels"""

    width: Optional[float] = None
    """Image width in pixels"""


class DataMetaOpenGraph(BaseModel):
    """Open Graph protocol metadata for rich link previews"""

    description: Optional[str] = None
    """Open Graph description (og:description)"""

    images: Optional[List[DataMetaOpenGraphImage]] = None
    """Open Graph images (og:image and related properties)"""

    locale: Optional[str] = None
    """Locale in language_TERRITORY format (og:locale)"""

    site_name: Optional[str] = FieldInfo(alias="siteName", default=None)
    """Site name (og:site_name)"""

    title: Optional[str] = None
    """Open Graph title (og:title)"""

    type: Optional[str] = None
    """Open Graph type (og:type) - website, article, product, etc."""

    url: Optional[str] = None
    """Canonical URL for the content (og:url)"""


class DataMetaTwitter(BaseModel):
    """Twitter Card metadata for social sharing previews"""

    card: Optional[str] = None
    """Twitter card type (twitter:card)"""

    creator: Optional[str] = None
    """Twitter @username of content creator (twitter:creator)"""

    description: Optional[str] = None
    """Description for Twitter card (twitter:description)"""

    image: Optional[str] = None
    """Image URL for Twitter card (twitter:image)"""

    site: Optional[str] = None
    """Twitter @username of the website (twitter:site)"""

    title: Optional[str] = None
    """Title for Twitter card (twitter:title)"""


class DataMeta(BaseModel):
    """Comprehensive metadata extracted from the page HTML head section"""

    canonical_url: Optional[str] = FieldInfo(alias="canonicalUrl", default=None)
    """Canonical URL from <link rel="canonical">"""

    charset: Optional[str] = None
    """Character encoding from <meta charset="...">"""

    description: Optional[str] = None
    """Meta description from <meta name="description">"""

    favicon: Optional[str] = None
    """Primary favicon URL (first icon found)"""

    icons: Optional[List[DataMetaIcon]] = None
    """All icon links (favicons, apple-touch-icons, etc.)"""

    language: Optional[str] = None
    """Page language from <html lang="...">"""

    open_graph: Optional[DataMetaOpenGraph] = FieldInfo(alias="openGraph", default=None)
    """Open Graph protocol metadata for rich link previews"""

    title: Optional[str] = None
    """Page title from <title> tag"""

    twitter: Optional[DataMetaTwitter] = None
    """Twitter Card metadata for social sharing previews"""


class DataSnippet(BaseModel):
    """
    A relevant snippet extracted from the page, compatible with TextPart for AI messages
    """

    index: float
    """Original chunk index"""

    score: float
    """Relevance score from the reranker (0-1)"""

    text: str
    """The text content of the snippet"""

    type: Optional[Literal["text"]] = None
    """Type identifier for TextPart compatibility"""


class Data(BaseModel):
    """
    Contains the extracted content in the formats specified by the select configuration
    """

    response: DataResponse
    """HTTP response information (URL, status code, optionally headers)"""

    html: Optional[str] = None
    """The HTML content of the fetched page"""

    markdown: Optional[str] = None
    """The markdown-formatted content extracted from the page"""

    meta: Optional[DataMeta] = None
    """Comprehensive metadata extracted from the page HTML head section"""

    screenshot: Optional[str] = None
    """Base64-encoded data URI of the screenshot image"""

    snippets: Optional[List[DataSnippet]] = None
    """Relevant snippets extracted from the page based on the search query"""

    summary: Optional[str] = None
    """AI-generated summary of the page content"""


class FetchResponse(BaseModel):
    """Complete response from a fetch operation"""

    data: Data
    """
    Contains the extracted content in the formats specified by the select
    configuration
    """
