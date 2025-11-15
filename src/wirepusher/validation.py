"""Input validation utilities for WirePusher library."""

import re
from typing import List, Optional


def normalize_tags(tags: Optional[List[str]]) -> Optional[List[str]]:
    """Normalize tags by converting to lowercase, trimming whitespace, and removing duplicates.

    Args:
        tags: Optional list of tags to normalize

    Returns:
        Normalized list of tags, or None if input is None

    Example:
        >>> normalize_tags(['Production', '  Release  ', 'production', 'Deploy'])
        ['production', 'release', 'deploy']
    """
    if tags is None:
        return None

    if not tags:  # Empty list
        return None

    # Normalize: lowercase, trim whitespace, remove empty strings
    normalized = []
    seen = set()

    for tag in tags:
        if not isinstance(tag, str):
            continue

        # Lowercase and trim
        normalized_tag = tag.lower().strip()

        # Skip empty tags
        if not normalized_tag:
            continue

        # Skip duplicates (case-insensitive)
        if normalized_tag in seen:
            continue

        # Validate characters (alphanumeric, hyphens, underscores only)
        if not re.match(r"^[a-z0-9_-]+$", normalized_tag):
            continue

        normalized.append(normalized_tag)
        seen.add(normalized_tag)

    return normalized if normalized else None
