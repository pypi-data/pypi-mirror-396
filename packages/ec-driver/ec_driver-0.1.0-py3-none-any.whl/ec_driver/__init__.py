"""eChecker driver library for Python."""

class DriverBuilder:
    """Builder for a driver."""

    name: str
    version: str

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version

