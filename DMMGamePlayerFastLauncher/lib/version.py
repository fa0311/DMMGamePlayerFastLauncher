import re


class Version:
    def __init__(self, version):
        if not re.match(r"v\d{1,}\.\d{1,}\.\d{1,}", version):
            raise ValueError(f"Invalid version format: {version}")
        self.major, self.minor, self.patch = map(int, version[1:].split("."))

    def __str__(self):
        return f"v{self.major}.{self.minor}.{self.patch}"

    def __eq__(self, other: "Version"):
        return self.major == other.major and self.minor == other.minor and self.patch == other.patch

    def __ne__(self, other: "Version"):
        return not self.__eq__(other)

    def __lt__(self, other: "Version"):
        return self.major < other.major or self.minor < other.minor or self.patch < other.patch

    def __le__(self, other: "Version"):
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other: "Version"):
        return self.major > other.major or self.minor > other.minor or self.patch > other.patch

    def __ge__(self, other: "Version"):
        return self.__eq__(other) or self.__gt__(other)

    def __hash__(self):
        return hash((self.major, self.minor, self.patch))

    def to_dict(self):
        return {"major": self.major, "minor": self.minor, "patch": self.patch}
