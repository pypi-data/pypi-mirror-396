from __future__ import annotations

from typing import Any

from szgf.schemas.original import OriginalGuide


def validate_original_guide(data: Any) -> OriginalGuide:
    return OriginalGuide.model_validate(data)
