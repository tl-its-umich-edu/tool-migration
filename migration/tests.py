import logging
import os
import unittest

from dotenv import load_dotenv

from data import Course, ExternalTool, ExternalToolTab, ToolMigration
from exceptions import InvalidToolIdsException
from main import main, find_tools_for_migrations
from manager import API, AccountManager, CourseManager
from utils import find_entity_by_id


logger = logging.getLogger(__name__)


class AccountManagerTestCase(unittest.TestCase):
    """
    Integration/unit tests for AccountManager class
    """

    def setUp(self) -> None:
        api_url: str = os.getenv('API_URL', '')
        api_key: str = os.getenv('API_KEY', '')
        self.enrollment_term_id: int = int(os.getenv('ENROLLMENT_TERM_ID', '0'))
        self.api = API(api_url, api_key)

        self.test_external_tool_tab = ExternalToolTab(
            id='context_external_tool_99999',
            label='Test External Tool',
            tool_id=99999,
            is_hidden=True,
            position=30
        )

    def test_find_tab_by_tool_id_returns_tab(self):
        tab = CourseManager.find_tab_by_tool_id(99999, [self.test_external_tool_tab])
        self.assertTrue(isinstance(tab, ExternalToolTab))

    def test_find_tab_by_tool_id_returns_none(self):
        tab = CourseManager.find_tab_by_tool_id(100000, [self.test_external_tool_tab])
        self.assertTrue(tab is None)

    def test_manager_gets_tools(self):
        with self.api.client:
            manager = AccountManager(1, self.api)
            tools = manager.get_tools_installed_in_account()
        self.assertTrue(len(tools) > 0)
        for tool in tools:
            self.assertTrue(isinstance(tool, ExternalTool))

    def test_manager_get_courses(self):
        with self.api.client:
            manager = AccountManager(1, self.api)
            courses = manager.get_courses_in_account_for_term(self.enrollment_term_id, 100)
        self.assertTrue(len(courses) > 0)
        for course in courses:
            self.assertTrue(isinstance(course, Course))


class CourseManagerTestCase(unittest.TestCase):
    """
    Integration tests for CourseManager class
    """

    def setUp(self) -> None:
        api_url: str = os.getenv('API_URL', '')
        api_key: str = os.getenv('API_KEY', '')
        self.api = API(api_url, api_key)
        self.test_course_id: int = int(os.getenv('TEST_COURSE_ID', '0'))
        self.course_manager = CourseManager(
            Course(self.test_course_id, name='Test Course'),
            self.api
        )
        self.source_tool_id: int = int(os.getenv('SOURCE_TOOL_ID', '0'))
        self.target_tool_id: int = int(os.getenv('TARGET_TOOL_ID', '0'))

    def test_manager_gets_tool_tabs_in_course(self):
        with self.api.client:
            manager = CourseManager(
                Course(self.test_course_id, name='Test Course'),
                self.api
            )
            tabs = manager.get_tool_tabs()
        self.assertTrue(len(tabs) > 0)
        for tab in tabs:
            self.assertTrue(isinstance(tab, ExternalToolTab))

    def test_manager_replaces_tool_tab_in_course(self):
        with self.api.client:
            tabs_before = self.course_manager.get_tool_tabs()
            source_tab = CourseManager.find_tab_by_tool_id(self.source_tool_id, tabs_before)
            target_tab = CourseManager.find_tab_by_tool_id(self.target_tool_id, tabs_before)
            if source_tab is None or target_tab is None:
                raise Exception(
                    'One or both of the following tool IDs are not available in this course: ' +
                    str([self.source_tool_id, self.target_tool_id])
                )
            source_original_position = source_tab.position

            self.course_manager.replace_tool_tab(source_tab, target_tab)
            tabs_after = self.course_manager.get_tool_tabs()

        source_tab = CourseManager.find_tab_by_tool_id(self.source_tool_id, tabs_after)
        target_tab = CourseManager.find_tab_by_tool_id(self.target_tool_id, tabs_after)
        if source_tab is not None and target_tab is not None:
            self.assertTrue(source_tab.is_hidden)
            self.assertFalse(target_tab.is_hidden)
            self.assertTrue(target_tab.position == source_original_position)


class UtilsTestCase(unittest.TestCase):
    """
    Unit tests for utils
    """

    def setUp(self):
        self.test_external_tool = ExternalTool(id=77777, name='Test External Tool')

    def test_find_tool_by_id_returns_tool(self):
        tool = find_entity_by_id(77777, [self.test_external_tool])
        self.assertTrue(isinstance(tool, ExternalTool))

    def test_find_tool_by_id_returns_none(self):
        tool = find_entity_by_id(77778, [self.test_external_tool])
        self.assertTrue(tool is None)


class MainTestCase(unittest.TestCase):

    def setUp(self) -> None:
        api_url: str = os.getenv('API_URL', '')
        api_key: str = os.getenv('API_KEY', '')
        self.api = API(api_url, api_key)
        self.account_id: int = int(os.getenv('ACCOUNT_ID', '0'))
        self.enrollment_term_id:  int = int(os.getenv('ENROLLMENT_TERM_ID', '0'))

        self.source_tool_id: int = int(os.getenv('SOURCE_TOOL_ID', '0'))
        self.target_tool_id: int = int(os.getenv('TARGET_TOOL_ID', '0'))

    def test_find_tool_ids_for_migrations_raises_exception_when_tool_ids_are_invalid(self):
        with self.api.client:
            account_manager = AccountManager(self.account_id, self.api)
            tools = account_manager.get_tools_installed_in_account()
        with self.assertRaises(InvalidToolIdsException):
            find_tools_for_migrations(tools, [ToolMigration(100000000, 100000001)])

    def test_main_migrates_tool_successfully(self):
        main(
            self.api,
            self.account_id,
            self.enrollment_term_id,
            [ToolMigration(source_id=self.source_tool_id, target_id=self.target_tool_id)]
        )
        # what needs to be checked?


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    root_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(root_dir, '.env'), verbose=True)
    unittest.main()
