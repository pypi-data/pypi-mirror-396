from abc import abstractmethod
from dataclasses import dataclass, asdict, field
from typing import List

class ExternalSourceSpec:
    @abstractmethod
    def to_param(self):
        pass

@dataclass
class FilesExternalSourceSpec(ExternalSourceSpec):
    uris: List[str]

    def to_param(self):
        return {"type": "files", **asdict(self)}

@dataclass
class PrefixExternalSourceSpec(ExternalSourceSpec):
    prefix_uri: str
    recursive: bool = True
    include_regexes: List[str] = field(default_factory=list)
    exclude_regexes: List[str] = field(default_factory=list)

    def to_param(self):
        return {"type": "prefix", **asdict(self)}
