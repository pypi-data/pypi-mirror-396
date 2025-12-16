#!/usr/bin/python3
"""
Юнит-тесты для метода update_cube из business_scenarios.py
"""

import pytest

from polymatica.business_scenarios import BusinessLogic
from polymatica.exceptions import PolymaticaException
from tests.const import DEFAULT_RELEVANCE_DATE


class TestUpdateCube:
    """Тесты для метода update_cube"""

    @pytest.fixture
    def mock_business_logic(
        self, mocker, mock_server_codes, mock_config, mock_execute_manager_command
    ):
        """Фикстура с моком BusinessLogic для тестов update_cube"""
        mock_auth = mocker.patch("polymatica.business_scenarios.Authorization")
        mock_auth_instance = mocker.Mock()
        mock_auth_instance.login.return_value = ("session_id", "uuid", "5.9.13", "v2")
        mock_auth.return_value = mock_auth_instance

        mocker.patch(
            "polymatica.business_scenarios.BusinessLogic._get_interface_config",
            return_value=mock_config,
        )
        mocker.patch("polymatica.business_scenarios.Executor")

        bl = BusinessLogic(
            url="https://test.polymatica.ru/", login="test", password="test"
        )

        bl.server_codes = mock_server_codes
        bl.config = mock_config
        bl.logger = mocker.Mock()
        bl.cube_id = "test_cube_id"

        # Мокаем методы, которые делают реальные запросы к серверу
        bl.execute_manager_command = mocker.Mock(
            side_effect=mock_execute_manager_command
        )
        bl.get_cubes_list = mocker.Mock(
            return_value=[{"name": "test_cube", "uuid": "test_cube_id"}]
        )

        # Мокаем helper методы
        bl.h.upload_file_to_server = mocker.Mock(return_value="datasource_test_id")
        bl.h.get_file_type = mocker.Mock(return_value="psql")

        return bl

    @pytest.mark.parametrize(
        "update_type",
        [
            "ручное",
            "по расписанию",
            "полное",
            "интервальное",
            "инкрементальное",
            "обновление измененных записей",
        ],
    )
    def test_update_types_validation(self, mock_business_logic, update_type):
        """Тест валидации типов обновления"""

        update_params = {"type": update_type}
        kwargs = {"cube_name": "test_cube", "update_params": update_params}

        if update_type == "по расписанию":
            update_params["schedule"] = {
                "type": "Ежедневно",
                "time": "18:30",
                "time_zone": "UTC+3:00",
            }
        elif update_type == "интервальное":
            kwargs["interval_dim"] = "date"
        elif update_type == "инкрементальное":
            kwargs["increment_dim"] = "date"
        elif update_type == "обновление измененных записей":
            kwargs["modified_records_params"] = {
                "modified_records_key": "latitude",
                "modified_records_date": "date",
            }

        mock_business_logic.update_cube(**kwargs)

    def test_update_types_validation_invalid(self, mock_business_logic):
        """Тест валидации типов обновления для невалидного параметра"""
        # Невалидный тип
        with pytest.raises(ValueError):
            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={"type": "invalid_type"},
            )

    @pytest.mark.parametrize(
        "user_interval",
        [
            "с текущего дня",
            "с предыдущего дня",
            "с текущей недели",
            "с предыдущей недели",
            "с текущего месяца",
            "с предыдущего месяца",
            "с текущего квартала",
            "с предыдущего квартала",
            "с текущего года",
            "с предыдущего года",
            "с указанной даты",
            "с и по указанную дату",
        ],
    )
    def test_user_intervals_validation(self, mock_business_logic, user_interval):
        """Тест валидации интервалов пользователя"""

        params = {
            "cube_name": "test_cube",
            "update_params": {"type": "интервальное"},
            "user_interval": user_interval,
            "interval_dim": "date",
        }

        if user_interval in ["с указанной даты", "с и по указанную дату"]:
            params["interval_borders"] = (
                ["01.01.2024"]
                if user_interval == "с указанной даты"
                else ["01.01.2024", "31.12.2024"]
            )

        mock_business_logic.update_cube(**params)

    def test_user_intervals_validation_invalid(self, mock_business_logic):
        """Тест невалидного интервала пользователя"""
        # в случае невалидного интервала тесты должны упасть
        params = {
            "cube_name": "test_cube",
            "update_params": {"type": "интервальное"},
            "user_interval": "invalid_interval",
            "interval_dim": "date",
        }
        with pytest.raises(ValueError):
            mock_business_logic.update_cube(**params)

    def test_schedule_validation(self, mock_business_logic):
        """Тест валидации расписания"""
        # Валидное расписание
        valid_schedules = [
            {"type": "Ежедневно", "time": "18:30", "time_zone": "UTC+3:00"},
            {
                "type": "Еженедельно",
                "time": "09:00",
                "time_zone": "UTC+3:00",
                "week_day": "понедельник",
            },
            {"type": "Ежемесячно", "time": "12:00", "time_zone": "UTC+3:00", "day": 15},
        ]
        for schedule in valid_schedules:
            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={"type": "по расписанию", "schedule": schedule},
            )

        # Невалидное время
        with pytest.raises(ValueError):
            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={
                    "type": "по расписанию",
                    "schedule": {
                        "type": "Ежедневно",
                        "time": "25:70",
                        "time_zone": "UTC+3:00",
                    },
                },
            )

        # Невалидная временная зона
        with pytest.raises(ValueError):
            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={
                    "type": "по расписанию",
                    "schedule": {
                        "type": "Ежедневно",
                        "time": "18:30",
                        "time_zone": "INVALID_ZONE",
                    },
                },
            )

    def test_modified_records_params_validation(self, mocker, mock_business_logic):
        """Тест валидации параметров обновления измененных записей"""
        # Валидные параметры
        valid_params = [
            {
                "modified_records_key": "latitude",
                "modified_records_date": "date",
                "version": 0,
            },
            {
                "modified_records_key": "latitude",
                "modified_records_date": "date",
                "version": 1,
            },
            {
                "modified_records_key": "latitude",
                "modified_records_date": "date",
            },  # version по умолчанию = 1
        ]

        for params in valid_params:
            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={"type": "обновление измененных записей"},
                modified_records_params=params,
            )

        # Проверка на то, что метод покажет warning из-за некорректного значения version
        spy_logger = mocker.spy(mock_business_logic.logger, "warning")
        warning_params = {
            "modified_records_key": "latitude",
            "modified_records_date": "date",
            "version": 2,
        }
        mock_business_logic.update_cube(
            cube_name="test_cube",
            update_params={"type": "обновление измененных записей"},
            modified_records_params=warning_params,
        )
        assert spy_logger.call_count == 1

        # Невалидные параметры: отсутствует modified_records_key, отсутствует modified_records_date,
        # modified_records_date не типа date, datetime, размерность отсутствует в мультисфере
        invalid_params = [
            {
                "modified_records": "id",
                "modified_records_date": "date",
                "version": 1,
            },
            {
                "modified_records_key": "date",
                "modified_records": "latitude",
            },
            {
                "modified_records_key": "date",
                "modified_records_date": "latitude",
                "version": 1,
            },
            {
                "modified_records_key": "dim_not_in_cube",
                "modified_records_date": "date",
                "version": 1,
            },
        ]

        for params in invalid_params:
            # noinspection PyTypeChecker
            with pytest.raises((PolymaticaException, ValueError)):
                mock_business_logic.update_cube(
                    cube_name="test_cube",
                    update_params={"type": "обновление измененных записей"},
                    modified_records_params=params,
                )

    def test_modified_records_duplicate_fields_error(self, mock_business_logic):
        """Тест ошибки при одинаковых значениях key и date в modified_records_params"""

        with pytest.raises(ValueError):
            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={"type": "обновление измененных записей"},
                modified_records_params={
                    "modified_records_key": "id",
                    "modified_records_date": "id",
                },
            )

    def test_relevance_date_validation(self, mock_business_logic):
        """Тест валидации параметров даты актуальности"""

        valid_params = [
            {
                "relevance_date_dimension": "date",
                "format": "date",
                "consider_filter": True,
            },
            {
                "relevance_date_dimension": "datetime",
                "format": "datetime",
                "consider_filter": False,
            },
        ]

        for params in valid_params:
            mock_business_logic.update_cube(
                cube_name="test_cube", relevance_date=params
            )

        # Невалидный формат
        with pytest.raises(ValueError):
            mock_business_logic.update_cube(
                cube_name="test_cube",
                relevance_date={
                    "relevance_date_dimension": "date",
                    "format": "invalid",
                    "consider_filter": True,
                },
            )

    def test_empty_relevance_date_reset(self, mock_business_logic):
        """Тест сброса параметров даты актуальности"""

        mock_business_logic.update_cube(
            cube_name="test_cube", relevance_date={}  # Пустой словарь для сброса
        )
        # Получаем последний вызов execute_manager_command
        last_call = mock_business_logic.execute_manager_command.call_args_list[-1]
        assert last_call.kwargs["relevance_date"] == DEFAULT_RELEVANCE_DATE

    def test_indirect_cpu_load_parameter_validation(self, mock_business_logic):
        """Тест валидации параметров ограничения CPU"""
        # Валидные параметры
        valid_params = [
            {"use_default_value": True},
            {"use_default_value": True, "percent": 50},  # процент игнорируется
            {"use_default_value": True, "percent": 500},  # процент игнорируется
            {"use_default_value": False, "percent": 50},
            {"use_default_value": False, "percent": 1},  # минимум
            {"use_default_value": False, "percent": 100},  # максимум
        ]

        for params in valid_params:
            mock_business_logic.update_cube(
                cube_name="test_cube", indirect_cpu_load_parameter=params
            )
            # Получаем последний вызов execute_manager_command
            last_call = mock_business_logic.execute_manager_command.call_args_list[-1]

            # Проверяем, что в последнем вызове процент использования ЦПУ в indirect_cpu_load_parameter
            # равен ожидаемому значению (равен значению из конфига, если заданное значение превышает
            # значение из конфига или если необходимо использовать стандартное значение)
            if params["use_default_value"]:
                assert (
                    last_call.kwargs["indirect_cpu_load_parameter"]["percent"]
                    == mock_business_logic.config["indirect_sort_cpu_load_percent"]
                )
            else:
                if (
                    params.get("percent")
                    <= mock_business_logic.config["indirect_sort_cpu_load_percent"]
                ):
                    assert last_call.kwargs["indirect_cpu_load_parameter"][
                        "percent"
                    ] == params.get("percent")
                else:
                    assert (
                        last_call.kwargs["indirect_cpu_load_parameter"]["percent"]
                        == mock_business_logic.config["indirect_sort_cpu_load_percent"]
                    )

        # Невалидные параметры (проценты)
        invalid_params = (0, 101)
        for percent in invalid_params:
            with pytest.raises(ValueError):
                mock_business_logic.update_cube(
                    cube_name="test_cube",
                    indirect_cpu_load_parameter={
                        "use_default_value": False,
                        "percent": percent,
                    },
                )

    def test_increment_dim_types_validation(self, mocker, mock_business_logic):
        """Тест валидации типов размерности для инкрементального обновления"""

        # Размерности с валидными типами для инкремента
        valid_types = [
            0,
            1,
            2,
            3,
            4,
            6,
            7,
            8,
        ]  # uint8, uint16, uint32, uint64, double, date, time, datetime

        for dim_type in valid_types:
            mock_business_logic.h.get_and_process_dims_and_measures = mocker.Mock(
                return_value=(
                    [
                        {
                            "name": "increment_dim",
                            "type": dim_type,
                            "id": "dim1",
                            "field_id": "field1",
                        }
                    ],
                    [{"name": "value", "type": 4}],
                )
            )

            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={"type": "инкрементальное"},
                increment_dim="increment_dim",
            )

    def test_increment_dim_invalid_type_error(self, mocker, mock_business_logic):
        """Тест ошибки при невалидном типе размерности для инкремента"""

        # Невалидный тип (string)
        mock_business_logic.h.get_and_process_dims_and_measures = mocker.Mock(
            return_value=(
                [{"name": "increment_dim", "type": 5, "id": "dim1"}],
                [{"name": "value", "type": 4}],
            )
        )

        with pytest.raises(PolymaticaException):
            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={"type": "инкрементальное"},
                increment_dim="increment_dim",
            )

    def test_interval_dim_types_validation(self, mocker, mock_business_logic):
        """Тест валидации типов размерности для интервального обновления"""

        # Валидные типы для интервального обновления (date, datetime)
        valid_types = [6, 8]  # date, datetime

        for dim_type in valid_types:
            mock_business_logic.h.get_and_process_dims_and_measures = mocker.Mock(
                return_value=(
                    [{"name": "interval_field", "type": dim_type, "id": "dim1"}],
                    [{"name": "value", "type": 4}],
                )
            )

            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={"type": "интервальное"},
                user_interval="с текущего дня",
                interval_dim="interval_field",
            )

    def test_interval_dim_invalid_type_error(self, mocker, mock_business_logic):
        """Тест ошибки при невалидном типе размерности для интервала"""

        # Невалидный тип (string)
        mock_business_logic.h.get_and_process_dims_and_measures = mocker.Mock(
            return_value=(
                [{"name": "interval_field", "type": 5, "id": "dim1"}],  # string
                [{"name": "value", "type": 4}],
            )
        )

        with pytest.raises(PolymaticaException):
            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={"type": "интервальное"},
                user_interval="с текущего дня",
                interval_dim="interval_field",
            )

    def test_interval_borders_validation(self, mock_business_logic):
        """Тест валидации временных границ интервалов"""

        # Валидные границы для "с указанной даты"
        mock_business_logic.update_cube(
            cube_name="test_cube",
            update_params={"type": "интервальное"},
            user_interval="с указанной даты",
            interval_dim="date",
            interval_borders=["01.01.2024"],
        )

        # Валидные границы для "с и по указанную дату"
        mock_business_logic.update_cube(
            cube_name="test_cube",
            update_params={"type": "интервальное"},
            user_interval="с и по указанную дату",
            interval_dim="date",
            interval_borders=["01.01.2024", "31.12.2024"],
        )

        # Невалидные границы для "с и по указанную дату"
        with pytest.raises(ValueError):
            mock_business_logic.update_cube(
                cube_name="test_cube",
                update_params={"type": "интервальное"},
                user_interval="с и по указанную дату",
                interval_dim="date",
                interval_borders=["01.01.2024"],
            )

    def test_legacy_update_types_warning(self, mock_business_logic, mocker):
        """Тест предупреждения об устаревших типах обновления"""

        spy_logger = mocker.spy(mock_business_logic.logger, "warning")

        # Устаревшие типы должны вызывать предупреждение
        legacy_types = ["ручное", "по расписанию"]

        for update_type in legacy_types:
            params = {"type": update_type}
            if update_type == "по расписанию":
                params["schedule"] = {
                    "type": "Ежедневно",
                    "time": "18:30",
                    "time_zone": "UTC+3:00",
                }

            mock_business_logic.update_cube(cube_name="test_cube", update_params=params)

        # Проверяем, что предупреждение было залогировано
        assert spy_logger.call_count == 2

    def test_file_replacement_validation(self, mocker, mock_business_logic):
        """Тест валидации замены файла"""

        # если тип источника (задан psql) не совпадает с типом файла, то падает ошибка
        with pytest.raises(ValueError):
            mock_business_logic.update_cube(
                cube_name="test_cube",
                filepath="test.csv",
                separator=",",
                encoding="UTF-8",
            )

        # меняем тип источника на csv
        mock_business_logic.h.get_file_type = mocker.Mock(return_value="csv")
        mock_business_logic.update_cube(
            cube_name="test_cube", filepath="test.csv", separator=",", encoding="UTF-8"
        )

    def test_file_type_mismatch_error(self, mocker, mock_business_logic):
        """Тест ошибки при несоответствии типов файлов при замене источника"""

        mock_business_logic.h.get_file_type = mocker.Mock(return_value="csv")

        with pytest.raises(ValueError, match="must be of the same format"):
            mock_business_logic.update_cube(
                cube_name="test_cube",
                filepath="test.xlsx",
                separator=",",
                encoding="UTF-8",
            )

    def test_cube_rename(self, mock_business_logic):
        """Тест переименования куба"""

        mock_business_logic.update_cube(
            cube_name="test_cube", new_cube_name="renamed_cube"
        )

        assert mock_business_logic.cube_name == "renamed_cube"

    @pytest.mark.parametrize(
        "new_cube_name", ["test"] + [f"test_cube{char}" for char in "%^&=;±§`~][}{<>"]
    )
    def test_cube_rename_invalid(self, mock_business_logic, new_cube_name):
        """Тест переименования куба с коротким или некорректным именем"""
        with pytest.raises(ValueError):
            mock_business_logic.update_cube(
                cube_name="test_cube", new_cube_name=new_cube_name
            )

    def test_multiple_schedules(self, mock_business_logic):
        """Тест поддержки нескольких расписаний"""

        schedules = [
            {"type": "Ежедневно", "time": "09:00", "time_zone": "UTC+3:00"},
            {
                "type": "Еженедельно",
                "time": "18:00",
                "time_zone": "UTC+3:00",
                "week_day": "понедельник",
            },
        ]

        mock_business_logic.update_cube(
            cube_name="test_cube",
            update_params={"type": "по расписанию", "schedule": schedules},
        )

    def test_cube_not_found_error(self, mock_business_logic):
        """Тест ошибки при отсутствии куба"""
        with pytest.raises(ValueError):
            mock_business_logic.update_cube(cube_name="non_existent_cube")
