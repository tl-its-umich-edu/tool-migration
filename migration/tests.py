import logging
import os
import unittest

from dotenv import load_dotenv

from data import Course, ExternalTool, ExternalToolTab
from manager import API, AccountManager, CourseManager


logger = logging.getLogger(__name__)


class AccountManagerTestCase(unittest.TestCase):
    """
    Integration tests for AccountManager class
    """

    def setUp(self) -> None:
        api_url: str = os.getenv('API_URL', '')
        api_key: str = os.getenv('API_KEY', '')
        self.enrollment_term_id: int = int(os.getenv('ENROLLMENT_TERM_ID', '0'))
        self.api = API(api_url, api_key)

    def test_manager_gets_tools(self):
        with self.api.client:
            manager = AccountManager(1, self.api)
            tools = manager.get_tools_installed_in_account()
        self.assertTrue(len(tools) > 0)
        for tool in tools:
            logger.info(tool)
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
        self.test_source_tool_id: int = int(os.getenv('TEST_SOURCE_LTI_ID', '0'))
        self.test_target_tool_id: int = int(os.getenv('TEST_TARGET_LTI_ID', '0'))

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
            manager = CourseManager(
                Course(self.test_course_id, name='Test Course'),
                self.api
            )
            tabs = manager.get_tool_tabs()
            source_tab = CourseManager.find_tab_by_tool_id(self.test_source_tool_id, tabs)
            target_tab = CourseManager.find_tab_by_tool_id(self.test_target_tool_id, tabs)
            if source_tab is None or target_tab is None:
                raise Exception(
                    'One or both of the following tool IDs are invalid: ' + 
                    str([self.test_source_tool_id, self.test_target_tool_id])
                )
            source_original_position = source_tab.position

            manager.replace_tool_tab(source_tab, target_tab)
            tabs = manager.get_tool_tabs()
            source_tab = CourseManager.find_tab_by_tool_id(self.test_source_tool_id, tabs)
            target_tab = CourseManager.find_tab_by_tool_id(self.test_target_tool_id, tabs)
            if source_tab is not None and target_tab is not None:
                self.assertTrue(source_tab.is_hidden)
                self.assertFalse(target_tab.is_hidden)
                self.assertTrue(target_tab.position == source_original_position)


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    load_dotenv(os.path.join('..', '.env'), verbose=True)
    unittest.main()
