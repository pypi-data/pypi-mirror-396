# zzz-guides

This repository contains:

- ZZZ agent guides in `guides/original`
- Definition of the Standardized ZZZ Guide Format (SZGF) in `schema.json` (or as Pydantic models in `szgf/schema.py`)
- Python package for validating and fetching guides from this repository in `szgf`
- Parsed version of the guides in `guides/parsed`
- Translated guides in `guides/translated`

## Usage

Install the package:

```bash
pip install szgf
```

Import and use the `SZGFClient` to fetch and read guides:

```python
from szgf.client import SZGFClient
client = SZGFClient()
await client.download_guides()
guides = await client.read_guides() # Returns a dict of ParsedGuide objects
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.
