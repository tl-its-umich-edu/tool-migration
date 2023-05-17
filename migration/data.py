from dataclasses import dataclass
from abc import ABC


@dataclass(frozen=True)
class CanvasEntity(ABC):
    id: int
    name: str


class ExternalTool(CanvasEntity):
    pass


class Course(CanvasEntity):
    pass


@dataclass(frozen=True)
class ExternalToolTab:
    id: str
    label: str
    tool_id: int
    is_hidden: bool
    position: int
