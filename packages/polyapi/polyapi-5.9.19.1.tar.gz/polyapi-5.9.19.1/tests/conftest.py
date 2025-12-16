#!/usr/bin/python3
"""
Общие фикстуры для тестов
"""

import pytest

from tests.const import (
    RESPONSE_USER_CUBE_CREATE_CUBE_REQUEST,
    RESPONSE_USER_CUBE_EXT_INFO_REQUEST,
    RESPONSE_USER_CUBE_STRUCTURE_PREVIEW_REQUEST,
    RESPONSE_USER_CUBE_TEST_SOURCE_CONNECTION_REQUEST,
    SERVER_CODES,
)


@pytest.fixture
def mock_server_codes():
    """Фикстура с моком server_codes"""
    return SERVER_CODES


@pytest.fixture
def mock_config():
    """Фикстура с моком конфигурации"""
    return {"indirect_sort_cpu_load_percent": 80}


@pytest.fixture
def mock_execute_manager_command():
    """Фикстура с моком execute_manager_command"""

    def mock_func(command_name, state, *args, **kwargs):
        # Проверяем аргументы и возвращаем соответствующий ответ
        if command_name == "user_cube" and state == "create_cube_request":
            return RESPONSE_USER_CUBE_CREATE_CUBE_REQUEST
        elif command_name == "user_cube" and state == "test_source_connection_request":
            return RESPONSE_USER_CUBE_TEST_SOURCE_CONNECTION_REQUEST
        elif command_name == "user_cube" and state == "structure_preview_request":
            return RESPONSE_USER_CUBE_STRUCTURE_PREVIEW_REQUEST
        elif (
            command_name == "user_cube" and state == "ext_info_several_sources_request"
        ):
            return RESPONSE_USER_CUBE_EXT_INFO_REQUEST
        elif (
            command_name == "user_cube"
            and state == "save_ext_info_several_sources_request"
        ):
            return {
                "state": 1,
                "queries": [
                    {
                        "uuid": "uuid123",
                        "command": {
                            "plm_type_code": 208,
                            "state": 29,
                            "cube_id": "cube_id",
                        },
                    }
                ],
            }
        else:
            return {"result": "default_success"}

    return mock_func
