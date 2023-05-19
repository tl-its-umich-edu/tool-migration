from typing import TypeVar

from data import CanvasEntity


T = TypeVar('T', bound=CanvasEntity)


def find_entity_by_id(id: int, entities: list[T]) -> T | None:
    for entity in entities:
        if entity.id == id:
            return entity
    return None
