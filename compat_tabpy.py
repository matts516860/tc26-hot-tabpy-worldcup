"""Compatibility helpers for legacy TabPy client imports on modern Python."""

import collections
import collections.abc


def patch_legacy_collections_aliases():
    """Restore aliases that older dependencies still import from collections."""
    aliases = (
        "Mapping",
        "MutableMapping",
        "Sequence",
        "MutableSequence",
        "Set",
        "MutableSet",
        "Iterable",
    )

    for name in aliases:
        if not hasattr(collections, name) and hasattr(collections.abc, name):
            setattr(collections, name, getattr(collections.abc, name))


patch_legacy_collections_aliases()
