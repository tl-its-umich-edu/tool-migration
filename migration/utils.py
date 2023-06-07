import logging
from typing import TypeVar

from data import CanvasEntity
from exceptions import ConfigException


logger = logging.getLogger(__name__)

T = TypeVar('T', bound=CanvasEntity)


def find_entity_by_id(id: int, entities: list[T]) -> T | None:
    for entity in entities:
        if entity.id == id:
            return entity
    return None


def convert_csv_to_int_list(csv_string: str) -> list[int]:
    string_list = csv_string.split(',')
    logger.debug(string_list)
    try:
        int_list = [int(elem) for elem in string_list]
    except ValueError:
        exception = ConfigException()
        exception.add_note(
            'One or more of the items in a CSV configuration could not be converted to a string'
        )
        raise exception
    return int_list
