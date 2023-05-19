import logging
from dataclasses import dataclass
from typing import Any

import httpx

from api import API
from data import Course, ExternalTool, ExternalToolTab


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AccountManager:
    account_id: int
    api: API

    def get_tools_installed_in_account(self) -> list[ExternalTool]:
        params = {"include_parents": True}
        results = self.api.get_results_from_pages(f'/accounts/{self.account_id}/external_tools', params)
        tools = [ExternalTool(id=tool_dict['id'], name=tool_dict['name']) for tool_dict in results]
        logger.info(f'Number of tools found in account {self.account_id}: {len(tools)}')
        return tools

    def get_courses_in_account_for_term(self, term_id: int, bail_after: int | None = None) -> list[Course]:
        results = self.api.get_results_from_pages(
            f'/accounts/{self.account_id}/courses',
            params={ 'enrollment_term_id': term_id },
            page_size=50,
            bail_after=bail_after
        )
        courses = [Course(id=course_dict['id'], name=course_dict['name']) for course_dict in results]
        logger.info(f'Number of courses found in account {self.account_id}: {len(courses)}')
        return courses


@dataclass(frozen=True)
class CourseManager:
    id_prefix = 'context_external_tool_'
    course: Course
    api: API

    def get_tool_tabs(self) -> list[ExternalToolTab]:
        try:
            resp = self.api.client.get(f'/courses/{self.course.id}/tabs')
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"HTTP Exception for {e.request.url} - {e}")
            raise e
        results: list[dict[str, Any]] = resp.json()
        
        tabs: list[ExternalToolTab] = []
        for result in results:
            logger.debug(result)
            if result['type'] == 'external':
                tool_id = int(result['id'].replace(self.id_prefix, ''))
                tabs.append(ExternalToolTab(
                    id=result['id'],
                    label=result['label'],
                    tool_id=tool_id,
                    is_hidden=('hidden' in result.keys() and result['hidden'] is True),
                    position=result['position']
                ))
        return tabs

    @staticmethod
    def find_tab_by_tool_id(tool_id: int, tabs: list[ExternalToolTab]) -> ExternalToolTab | None:
        for tab in tabs:
            if tab.tool_id == tool_id:
                return tab
        return None

    def replace_tool_tab(self, source_tab: ExternalToolTab, target_tab: ExternalToolTab) -> None:
        target_tab_params: dict[str, Any] = {"hidden": False}
        if not source_tab.is_hidden:
            target_tab_params.update({"position": source_tab.position})

        try:
            resp = self.api.client.put(
                f'/courses/{self.course.id}/tabs/{target_tab.id}',
                params=target_tab_params
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"HTTP Exception for {e.request.url} - {e}")
            raise e
        logger.debug(resp.json())

        try:
            resp = self.api.client.put(
                f'/courses/{self.course.id}/tabs/{source_tab.id}',
                params={"hidden": True}
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"HTTP Exception for {e.request.url} - {e}")
            raise e

        return
