import logging
import os
from contextlib import nullcontext
from io import StringIO

import trio
from dotenv import load_dotenv
from tqdm import tqdm

from api import API
from data import Course, ExternalTool, ToolMigration
from db import DB, Dialect
from exceptions import InvalidToolIdsException
from manager import AccountManagerFactory, CourseManager
from utils import convert_csv_to_int_list, find_entity_by_id, time_execution

summaryLogBuffer = StringIO()
summaryLogHandler = logging.StreamHandler(summaryLogBuffer)
summaryLogHandler.setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO,
    style='{',
    format='{asctime} | {levelname} | {module}:{lineno} | {message}',
    handlers=[logging.StreamHandler(), summaryLogHandler]
)

logger = logging.getLogger(__name__)


class TrioProgress(trio.abc.Instrument):

    def __init__(self, total, **kwargs):
        self.tqdm = tqdm(total=total, leave=None, **kwargs)

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
            account_name = await account_manager.get_name()
            logger.info(f'Account ({account_id}) name: {repr(account_name)}')

            term_names = await account_manager.get_term_names(term_ids)
            logger.info(f'Term names…')
            for term_id in term_ids:
                logger.info(f'  Term ({term_id}): {repr(term_names[term_id])}')

            tools = await account_manager.get_tools_installed_in_account()
            logger.info(
                'Number of tools found in account'
                f' ({account_id}): {len(tools)}')

            logger.debug('Tools…\n\t' +
                         '\n\t'.join([str(tool) for tool in tools]))

            tool_pairs = find_tools_for_migrations(tools, migrations)

            # get list of tools available in account
            courses = await account_manager.get_courses_in_terms(term_ids)
            logger.info(
                f'Number of courses found in account ({account_id}) '
                f'for terms {term_ids}: {len(courses)}')

            for source_tool, target_tool in tool_pairs:
                logger.info(f'Source tool: {source_tool}')
                logger.info(f'Target tool: {target_tool}')

                progress = TrioProgress(total=len(courses), unit='course')
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


def run():
    logging.basicConfig(
        level=logging.INFO,
        style='{',
        format='{asctime} | {levelname} | {module}:{lineno} | {message}')

    logger.info('Starting migration…')

    # get configuration (either env. variables, cli flags, or direct input)
    root_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file_name: str = os.path.join(root_dir, 'env')

    if os.path.exists(env_file_name):
        logger.info(f'Setting environment from file "{env_file_name}".')
        load_dotenv(env_file_name, verbose=True)
    else:
        logger.info(f'File "{env_file_name}" not found.  '
                     'Using existing environment.')

    logger.info('Parameters from environment…')

    # Set up logging
    log_level_default = logging.INFO
    log_level = os.getenv('LOG_LEVEL', log_level_default)
    logger.info(f'  LOG_LEVEL: {repr(log_level)} '
                f'({repr(logging.getLevelName(log_level))})')
    if log_level == '':
        log_level = log_level_default
        logger.info(f'  Using default LOG_LEVEL: {repr(log_level)} '
                    f'({repr(logging.getLevelName(log_level))})')

    http_log_level_default = logging.WARNING
    http_log_level = os.getenv('HTTP_LOG_LEVEL', http_log_level_default)
    logger.info(f'  HTTP_LOG_LEVEL: {repr(http_log_level)} '
                f'({repr(logging.getLevelName(http_log_level))})')
    if http_log_level == '':
        http_log_level = http_log_level_default
        logger.info(f'  Using default HTTP_LOG_LEVEL: {repr(http_log_level)} '
                    f'({repr(logging.getLevelName(http_log_level))})')

    logging.basicConfig(level=log_level)

    httpx_logger = logging.getLogger('httpx')
    httpx_logger.setLevel(http_log_level)
    httpcore_logger = logging.getLogger('httpcore')
    httpcore_logger.setLevel(http_log_level)

    api_url: str = os.getenv('API_URL', '')
    logger.info(f'  API_URL: {repr(api_url)}')

    api_key: str = os.getenv('API_KEY', '')
    logger.info(f'  API_KEY: *REDACTED*')

    account_id: int = int(os.getenv('ACCOUNT_ID', 0))
    logger.info(f'  ACCOUNT_ID: ({account_id})')

    enrollment_term_ids: list[int] = convert_csv_to_int_list(
        os.getenv('ENROLLMENT_TERM_IDS_CSV', '0'))
    logger.info(f'  ENROLLMENT_TERM_IDS_CSV: {enrollment_term_ids}')

    source_tool_id: int = int(os.getenv('SOURCE_TOOL_ID', 0))
    logger.info(f'  SOURCE_TOOL_ID: ({source_tool_id})')

    target_tool_id: int = int(os.getenv('TARGET_TOOL_ID', 0))
    logger.info(f'  TARGET_TOOL_ID: ({target_tool_id})')

    wh_host = os.getenv('WH_HOST')
    logger.info(f'  WH_HOST: {repr(wh_host)}')

    wh_port = os.getenv('WH_PORT')
    logger.info(f'  WH_PORT: {repr(wh_port)}')

    wh_name = os.getenv('WH_NAME')
    logger.info(f'  WH_NAME: {repr(wh_name)}')

    wh_user = os.getenv('WH_USER')
    logger.info(f'  WH_USER: {repr(wh_user)}')

    wh_password = os.getenv('WH_PASSWORD')
    logger.info(f'  WH_PASSWORD: *REDACTED*')

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
            'used for some data fetching…')
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
        logger.warning('Warehouse connection is not fully configured, '
                       'so falling back to only using the Canvas API…')

    trio.run(
        main,
        API(api_url, api_key),
        account_id,
        enrollment_term_ids,
        [ToolMigration(source_id=source_tool_id, target_id=target_tool_id)],
        db
    )

    summaryLogHandler.flush()
    summaryLogBuffer.flush()

    logger.info(f'Log summary (WARNING or higher): {"- " * 20}\n' +
                summaryLogBuffer.getvalue())
    logger.info(f'Log summary ends {"- " * 20}\n')

    logger.info('Migration complete.')

if '__main__' == __name__:
    run()
