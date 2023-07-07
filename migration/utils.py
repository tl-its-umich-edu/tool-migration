import functools
import logging
import time
from typing import Callable, TypeVar

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


def chunk_integer(value: int, num_chunks: int) -> list[int]:
    if value < 0:
        raise Exception('value parameter for chunk_integer must be zero or a positive integer.')
    if num_chunks < 1:
        raise Exception('num_chunks parameter for chunk_integer must be a positive integer.')

    chunks: list[int] = []
    div_floor = (value // num_chunks)
    remainder = value % div_floor if div_floor > 0 else value
    for i in range(num_chunks):
        if i < remainder:
            chunks.append(div_floor + 1)
        else:
            chunks.append(div_floor)
    return chunks


def time_execution(callable: Callable) -> Callable:
    @functools.wraps(callable)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = callable(*args, **kwargs)
        end = time.time()
        delta = end - start
        logger.info(f'{callable.__qualname__} took {delta} seconds to complete.')
        return result
    return wrapper
