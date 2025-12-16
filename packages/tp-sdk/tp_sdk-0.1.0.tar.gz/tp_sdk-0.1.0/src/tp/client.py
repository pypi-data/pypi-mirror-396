import logging
from typing import Any, Dict, List, Optional

import httpx

from .errors import AuthError, NotFoundError, ServerError, TPError
from .models import SearchResult, Snippet, SnippetInput, UserInfo, Visibility

logger = logging.getLogger("tp-sdk")

class TeaserPaste:
    """
    TeaserPaste Client - The "One Word" Edition.
    Less typing, more pasting.
    """

    BASE_URL = "https://paste-api.teaserverse.online"

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TeaserPaste-SDK/0.1.0 (Python)"
        }

    def _req(self, method: str, path: str, json: Optional[Dict] = None) -> Any:
        url = f"{self.BASE_URL}{path}"
        logger.debug(f"{method} {url}")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.request(method, url, headers=self.headers, json=json)

                if resp.status_code in (401, 403):
                    raise AuthError(f"Nope ({resp.status_code}): {resp.text}")
                if resp.status_code == 404:
                    raise NotFoundError(f"Gone ({resp.status_code}): {resp.text}")
                if resp.status_code >= 500:
                    raise ServerError(f"Ouch ({resp.status_code}): {resp.text}")

                resp.raise_for_status()
                return resp.json()
        except httpx.RequestError as e:
            raise TPError(f"Network bad: {e}")

    # --- The "One Word" Public API ---

    def get(self, id: str, pwd: Optional[str] = None) -> Snippet:
        """Get a snippet."""
        payload = {"snippetId": id}
        if pwd: payload["password"] = pwd
        return Snippet(**self._req("POST", "/getSnippet", json=payload))

    def paste(self, data: SnippetInput) -> Snippet:
        """Create (Paste) a new snippet."""
        return Snippet(**self._req("POST", "/createSnippet", json=data.model_dump(by_alias=True)))

    def edit(self, id: str, **kwargs) -> Snippet:
        """Update a snippet. Pass fields as kwargs."""
        # Clean kwargs to valid update fields
        return Snippet(**self._req("PATCH", "/updateSnippet", json={"snippetId": id, "updates": kwargs}))

    def kill(self, id: str) -> bool:
        """Soft delete a snippet."""
        self._req("DELETE", "/deleteSnippet", json={"snippetId": id})
        return True

    def live(self, id: str) -> bool:
        """Restore (Resurrect) a deleted snippet."""
        self._req("POST", "/restoreSnippet", json={"snippetId": id})
        return True

    def star(self, id: str, on: bool = True) -> Dict[str, Any]:
        """Star (on=True) or Unstar (on=False)."""
        return self._req("POST", "/starSnippet", json={"snippetId": id, "star": on})

    def fork(self, id: str) -> Dict[str, str]:
        """Copy (Fork) a snippet to your account."""
        return self._req("POST", "/copySnippet", json={"snippetId": id})

    def ls(self, limit: int = 20, mode: Optional[Visibility] = None) -> List[Snippet]:
        """List MY snippets (ls)."""
        payload = {"limit": limit}
        if mode: payload["visibility"] = mode
        return [Snippet(**i) for i in self._req("POST", "/listSnippets", json=payload)]

    def user(self, uid: str) -> List[Snippet]:
        """Get PUBLIC snippets of another USER."""
        return [Snippet(**i) for i in self._req("POST", "/getUserPublicSnippets", json={"userId": uid})]

    def find(self, q: str, size: int = 20, skip: int = 0) -> SearchResult:
        """Search (Find) snippets."""
        data = self._req("POST", "/searchSnippets", json={"term": q, "size": size, "from": skip})
        return SearchResult(hits=[Snippet(**h) for h in data.get("hits", [])], total=data.get("total", 0))

    def me(self) -> UserInfo:
        """Get MY info."""
        return UserInfo(**self._req("GET", "/getUserInfo"))
