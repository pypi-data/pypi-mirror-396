# TeaserPaste Python SDK

Official Python SDK for TeaserPaste API. Simple, typed, and ready for the Teaserverse.

## Installation

```bash
# Using uv (Recommended)
uv add tp-sdk

# Using pip
pip install tp-sdk
```

## Quick Start

```python
import tp

# Initialize with your API Key
api = tp.TeaserPaste("YOUR_API_KEY")

# Create a new paste
note = api.paste(tp.SnippetInput(
    title="Teaserverse Logs", 
    content="System status: All green."
))
print(f"Created: {note.id}")

# Get a paste
data = api.get(note.id)
print(data.content)
```

## API Reference

"One-word" API's.

* `api.paste(input)` — Create a new snippet.
* `api.get(id, pwd=None)` — Get a snippet.
* `api.edit(id, **kwargs)` — Update a snippet.
* `api.kill(id)` — Soft delete a snippet.
* `api.live(id)` — Restore a deleted snippet.
* `api.fork(id)` — Copy a snippet to your account.
* `api.star(id, on=True)` — Star (or unstar) a snippet.
* `api.ls(limit=20)` — List your snippets.
* `api.user(uid)` — List another user's public snippets.
* `api.find(q)` — Search snippets.
* `api.me()` — Get your account info.

## Development
```bash
# Install dependencies
uv sync

# Build
uv build
```

## License

[MIT](LICENSE)
