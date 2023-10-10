import logging
import os
from contextlib import nullcontext

import trio
from dotenv import load_dotenv
from tqdm import tqdm

from api import API
from data import Course, ExternalTool, ToolMigration
from db import DB, Dialect
from exceptions import InvalidToolIdsException
from manager import AccountManagerFactory, CourseManager
from utils import convert_csv_to_int_list, find_entity_by_id, time_execution

logger = logging.getLogger(__name__)


class TrioProgress(trio.abc.Instrument):

    def __init__(self, total, **kwargs):
        self.tqdm = tqdm(total=total, **kwargs)

    def task_exited(self, task):
        self.tqdm.update(1)


def find_tools_for_migrations(
        tools: list[ExternalTool], migrations: list[ToolMigration]
) -> list[tuple[ExternalTool, ExternalTool]]:
    tool_pairs: list[tuple[ExternalTool, ExternalTool]] = []
    for migration in migrations:
        source_tool = find_entity_by_id(migration.source_id, tools)
        target_tool = find_entity_by_id(migration.target_id, tools)
        if source_tool is None or target_tool is None:
            invalid_tool_ids = []
            if source_tool is None:
                invalid_tool_ids.append(migration.source_id)
            if target_tool is None:
                invalid_tool_ids.append(migration.target_id)
            raise InvalidToolIdsException(
                'The following tool IDs from one of your migrations '
                'were not found in the account: ' +
                str(invalid_tool_ids)
            )
        tool_pairs.append((source_tool, target_tool))
    return tool_pairs


async def migrate_tool_for_course(api: API, course: Course,
                                  source_tool: ExternalTool,
                                  target_tool: ExternalTool):
    course_manager = CourseManager(course, api)
    tabs = await course_manager.get_tool_tabs()
    source_tool_tab = CourseManager.find_tab_by_tool_id(source_tool.id, tabs)
    target_tool_tab = CourseManager.find_tab_by_tool_id(target_tool.id, tabs)
    if source_tool_tab is None or target_tool_tab is None:
        raise InvalidToolIdsException(
            'One or both of the following tool IDs are not available in '
            'this course: ' +
            str([source_tool.id, target_tool.id])
        )
    await course_manager.replace_tool_tab(source_tool_tab, target_tool_tab)


@time_execution
async def main(api: API, account_id: int, term_ids: list[int],
               migrations: list[ToolMigration], db: DB | None = None):
    factory = AccountManagerFactory()
    account_manager = factory.get_manager(account_id, api, db)

    async with api.client:
        with db if db is not None else nullcontext():  # type: ignore
            tools = await account_manager.get_tools_installed_in_account()
            logger.info(
                f'Number of tools found in account {account_id}: {len(tools)}')

            logger.debug('Tools…\n\t' +
                         '\n\t'.join([str(tool) for tool in tools]))

            tool_pairs = find_tools_for_migrations(tools, migrations)

            # get list of tools available in account
            courses = await account_manager.get_courses_in_terms(term_ids)
            logger.info(
                f'Number of courses found in account {account_id} '
                f'for terms {term_ids}: {len(courses)}')

            for source_tool, target_tool in tool_pairs:
                logger.info(f'Source tool: {source_tool}')
                logger.info(f'Target tool: {target_tool}')

                progress = TrioProgress(total=len(courses))
                trio.lowlevel.add_instrument(progress)
                async with trio.open_nursery() as nursery:
                    for course in courses:
                        nursery.start_soon(
                            migrate_tool_for_course,
                            api,
                            course,
                            source_tool,
                            target_tool
                        )
                trio.lowlevel.remove_instrument(progress)


if '__main__' == __name__:
    logging.basicConfig(level=logging.INFO)

    # get configuration (either env. variables, cli flags, or direct input)
    root_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file_name: str = os.path.join(root_dir, 'env')

    if not os.path.exists(env_file_name):
        logger.error(f'File "{env_file_name}" not found.  '
                     'Please create one and try again.')
        exit(1)

    load_dotenv(env_file_name, verbose=True)

    # Set up logging
    log_level = os.getenv('LOG_LEVEL', logging.INFO)
    http_log_level = os.getenv('HTTP_LOG_LEVEL', logging.WARNING)
    logging.basicConfig(level=log_level)

    httpx_logger = logging.getLogger('httpx')
    httpx_logger.setLevel(http_log_level)
    httpcore_level = logging.getLogger('httpcore')
    httpcore_level.setLevel(http_log_level)

    api_url: str = os.getenv('API_URL', '')
    api_key: str = os.getenv('API_KEY', '')
    account_id: int = int(os.getenv('ACCOUNT_ID', 0))
    enrollment_term_ids: list[int] = convert_csv_to_int_list(
        os.getenv('ENROLLMENT_TERM_IDS_CSV', '0'))

    wh_host = os.getenv('WH_HOST')
    wh_port = os.getenv('WH_PORT')
    wh_name = os.getenv('WH_NAME')
    wh_user = os.getenv('WH_USER')
    wh_password = os.getenv('WH_PASSWORD')

    db: DB | None = None
    if (
            wh_host is not None and
            wh_port is not None and
            wh_name is not None and
            wh_user is not None and
            wh_password is not None
    ):
        logger.info(
            'Warehouse connection is configured, so it will be '
            'used for some data fetching...')
        db = DB(
            Dialect.POSTGRES,
            {
                'host': wh_host,
                'port': wh_port,
                'name': wh_name,
                'user': wh_user,
                'password': wh_password
            }
        )
    else:
        logger.info(
            'Warehouse connection is not configured, so falling back '
            'to only using the Canvas API...')

    source_tool_id: int = int(os.getenv('SOURCE_TOOL_ID', 0))
    target_tool_id: int = int(os.getenv('TARGET_TOOL_ID', 0))

    trio.run(
        main,
        API(api_url, api_key),
        account_id,
        enrollment_term_ids,
        [ToolMigration(source_id=source_tool_id, target_id=target_tool_id)],
        db
    )
