class DuplicateUDSPathError(ValueError):
    """Raised when multiple UDS sockets share the same directory without explicit validation override."""

    def __init__(self, socket_names: list, directory: str) -> None:
        message = (
            f"Duplicate UDS path detected: Sockets {socket_names} share the same directory '{directory}'. "
            f"To permit this, disable the validation rule by adding "
            f"'validation: {{disabled: [noduplicateudspathrule]}}' to your config."
        )
        super().__init__(message)
