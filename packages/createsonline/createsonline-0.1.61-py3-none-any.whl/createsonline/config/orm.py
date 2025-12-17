"""Compatibility layer for the AI-enhanced ORM.

The original test-suite and packaging metadata expect to import the
``AIEnhancedORM`` class from ``createsonline.config.orm``.  During the
repository's refactor the implementation was moved to
``createsonline.ai.orm`` without leaving a public shim behind, which now
breaks both the automated tests and downstream users installing the PyPI
package.  Re-introduce the module as a light-weight re-export so that the
documented import path keeps working while the actual implementation
remains in :mod:`createsonline.ai.orm`.

Only the public classes that are required by the tests are re-exported
today.  Should additional helpers be needed in the future they can be
added here without changing the underlying ORM module again.
"""

from __future__ import annotations

from createsonline.ai.orm import AIBaseModel, AIEnhancedORM, Base

__all__ = ["AIEnhancedORM", "AIBaseModel", "Base"]


def __getattr__(name: str):
    """Provide a helpful error for unexpected attribute access.

    The compatibility module purposefully keeps a small surface area.  If
    another symbol is requested we forward the attribute access to the
    original module and raise an informative :class:`AttributeError` when
    the symbol does not exist.  This mirrors the behaviour developers were
    accustomed to before the refactor while still pointing them to the
    new canonical location.
    """

    from createsonline import ai

    try:
        return getattr(ai.orm, name)
    except AttributeError as exc:  # pragma: no cover - defensive branch
        raise AttributeError(
            f"module 'createsonline.config.orm' has no attribute '{name}'. "
            "The ORM implementation now lives in 'createsonline.ai.orm'."
        ) from exc
