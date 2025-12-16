"""
TeaserPaste Python SDK (tp-sdk)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Short. Fast. Fun.

Usage:
    >>> import tp
    >>> api = tp.TeaserPaste("KEY")
    >>> api.paste(tp.SnippetInput(title="Hi", content="Yo"))
"""

from .client import TeaserPaste
from .errors import AuthError, NotFoundError, TPError
from .models import SearchResult, Snippet, SnippetInput, UserInfo, Visibility

__all__ = [
    "TeaserPaste",
    "Snippet",
    "SnippetInput",
    "Visibility",
    "SearchResult",
    "UserInfo",
    "TPError",
    "AuthError",
    "NotFoundError",
]
