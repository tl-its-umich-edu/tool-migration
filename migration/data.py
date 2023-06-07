from dataclasses import dataclass
from abc import ABC


@dataclass(frozen=True)
class CanvasEntity(ABC):
    id: int
    name: str


@dataclass(frozen=True)
class ExternalTool(CanvasEntity):
    pass


@dataclass(frozen=True)
class Course(CanvasEntity):
    enrollment_term_id: int


@dataclass(frozen=True)
class ExternalToolTab:
    id: str
    label: str
    tool_id: int
    is_hidden: bool
    position: int


@dataclass(frozen=True)
class ToolMigration:
    source_id: int
    target_id: int
