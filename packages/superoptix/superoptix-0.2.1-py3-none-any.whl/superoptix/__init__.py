"""SuperOptiX: A CLI tool for managing agentic DSL configurations."""

# ---------------------------------------------------------------------------
# Global warning filters
# ---------------------------------------------------------------------------
# Pydantic v2 raises a verbose UserWarning when serialising dynamic objects
# (e.g. DSPy Message / Choices) with a different field shape. These are
# harmless for SuperOptiX users and clutter the console, so we silence them
# once at package import time.  Down-stream modules (CLI runners, notebooks)
# inherit the filter automatically.

import warnings

# Match any variant of the Pydantic serializer warning header
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r"Pydantic serializer warnings.*",
)

# Suppress PydanticDeprecatedSince20 warnings from dependencies (e.g., storage3/Supabase)
# These are from third-party libraries using deprecated Pydantic v2 syntax
# Will be fixed when dependencies update to Pydantic v3-compatible syntax
# Note: PydanticDeprecatedSince20 is a UserWarning subclass, not DeprecationWarning
warnings.filterwarnings(
    "ignore",
    message=r".*PydanticDeprecatedSince20.*",
)
warnings.filterwarnings(
    "ignore",
    message=r".*pydantic.config.Extra.*",
)
# Suppress warnings from storage3 module (Supabase dependency)
warnings.filterwarnings(
    "ignore",
    module="storage3.*",
    category=UserWarning,
)

__version__ = "0.2.1"
