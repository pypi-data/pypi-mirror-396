class TPError(Exception):
    """Base exception for the TeaserPaste SDK."""
    pass

class AuthError(TPError):
    """Invalid API Key or Permission Denied (401/403)."""
    pass

class NotFoundError(TPError):
    """Snippet or resource not found (404)."""
    pass

class ServerError(TPError):
    """Server internal error (500) - Likely an issue on the API side."""
    pass
