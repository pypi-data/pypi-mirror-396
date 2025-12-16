class InvalidPathMissingEntityError(Exception):
    """Raised when a path is missing an entity component."""

    def __init__(self, path: str):
        super().__init__(f"Invalid path '{path}': missing entity component.")
        self.path = path


class InvalidPathEntityError(Exception):
    """Raised when a path is invalid."""

    def __init__(self, path: str):
        super().__init__(f"Invalid path '{path}'.")
        self.path = path
