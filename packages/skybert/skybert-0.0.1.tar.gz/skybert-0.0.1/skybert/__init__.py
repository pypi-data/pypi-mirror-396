"""
The official 'skybert' Python package. Currently a placeholder (v0.0.1).
"""

__version__ = "0.0.1"
__all__ = ["__version__"]  # Only explicitly expose the version


def __getattr__(name):
    """
    Raises a helpful error if someone tries to import and use a non-existent
    feature from this placeholder package.
    """

    # You can customize this error message to be specific to your project's features
    if name in ["SkybertClient", "connect"]:
        raise NotImplementedError(
            f"The '{name}' feature is not implemented in this version (__v{__version__}__). "
            "The 'skybert' package is currently a placeholder to reserve the name."
        )

    # Allow standard package access to still function
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
