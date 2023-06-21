import logging
from dataclasses import dataclass
from typing import Any

from api import API
from data import Course, ExternalTool, ExternalToolTab
from utils import chunk_integer


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AccountManager:
    account_id: int
    api: API

    def get_tools_installed_in_account(self) -> list[ExternalTool]:
        params = {"include_parents": True}
        results = self.api.get_results_from_pages(f'/accounts/{self.account_id}/external_tools', params)
        tools = [ExternalTool(id=tool_dict['id'], name=tool_dict['name']) for tool_dict in results]
        return tools

    def get_courses_in_terms(self, term_ids: list[int], limit: int | None = None) -> list[Course]:
        limit_chunks = None
        if limit is not None:
            limit_chunks = chunk_integer(limit, len(term_ids))

        results: list[dict[str, Any]] = []
        for i, term_id in enumerate(term_ids):
            limit_for_term = limit_chunks[i] if limit_chunks else None
            term_results = self.api.get_results_from_pages(
                f'/accounts/{self.account_id}/courses',
                params={ 'enrollment_term_id': term_id },
                page_size=50,
                limit=limit_for_term
            )
            results += term_results
        courses = [
            Course(
                id=course_dict['id'],
                name=course_dict['name'],
                enrollment_term_id=course_dict['enrollment_term_id']
            )
            for course_dict in results
        ]
        logger.info(f'Number of courses found in account {self.account_id} for terms {term_ids}: {len(courses)}')
        return courses


@dataclass(frozen=True)
class CourseManager:
    id_prefix = 'context_external_tool_'
    course: Course
    api: API

    @staticmethod
    def find_tab_by_tool_id(tool_id: int, tabs: list[ExternalToolTab]) -> ExternalToolTab | None:
        for tab in tabs:
            if tab.tool_id == tool_id:
                return tab
        return None

    @classmethod
    def convert_data_to_tool_tab(cls, data: dict[str, Any]) -> ExternalToolTab:
        tool_id = int(data['id'].replace(cls.id_prefix, ''))
        return ExternalToolTab(
            id=data['id'],
            label=data['label'],
            tool_id=tool_id,
            is_hidden=('hidden' in data.keys() and data['hidden'] is True),
            position=data['position']
        )

    def get_tool_tabs(self) -> list[ExternalToolTab]:
        results = self.api.get_results_from_pages(f'/courses/{self.course.id}/tabs')
        
        tabs: list[ExternalToolTab] = []
        for result in results:
            logger.debug(result)
            if result['type'] == 'external':
                tabs.append(CourseManager.convert_data_to_tool_tab(result))
        return tabs

    def update_tool_tab(self, tab: ExternalToolTab, is_hidden: bool, position: int | None = None):
        params: dict[str, Any] = { "hidden": is_hidden }
        if position is not None:
            params.update({ "position": position })

        result = self.api.put(
            f'/courses/{self.course.id}/tabs/{tab.id}',
            params=params
        )
        logger.debug(result)
        return CourseManager.convert_data_to_tool_tab(result)

    def replace_tool_tab(self, source_tab: ExternalToolTab, target_tab: ExternalToolTab) -> None:
        target_tab_params: dict[str, Any] = {"hidden": False}
        if not source_tab.is_hidden:
            target_tab_params.update({"position": source_tab.position})

        if not source_tab.is_hidden:
            target_position = source_tab.position
        else:
            target_position = None

        new_target_tab = self.update_tool_tab(tab=target_tab, is_hidden=False, position=target_position)
        new_source_tab = self.update_tool_tab(tab=source_tab, is_hidden=True)
        logger.info(f"Successfully replaced tool in course's navigation: {[new_source_tab, new_target_tab]}")
        return
