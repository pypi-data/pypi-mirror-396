#!/usr/bin/python3
"""
Юнит-тесты для метода create_sphere из business_scenarios.py
"""

import pytest

from polymatica.business_scenarios import BusinessLogic
from polymatica.exceptions import PolymaticaException
from tests.const import TEST_SQL_PARAMS, TEST_SQL_PARAMS_JDBC


class TestCreateSphere:
    """Тесты для метода create_sphere"""

    @pytest.fixture
    def mock_business_logic(
        self, mocker, mock_server_codes, mock_config, mock_execute_manager_command
    ):
        # Мокаем только то, что нужно для работы без сервера
        mock_auth = mocker.patch("polymatica.business_scenarios.Authorization")
        mock_auth_instance = mocker.Mock()
        mock_auth_instance.login.return_value = ("session_id", "uuid", "5.9.13", "v2")
        mock_auth.return_value = mock_auth_instance

        mocker.patch(
            "polymatica.business_scenarios.BusinessLogic._get_interface_config",
            return_value=mock_config,
        )
        mocker.patch("polymatica.business_scenarios.Executor")

        # Создаем реальный экземпляр BusinessLogic
        bl = BusinessLogic(
            url="https://test.polymatica.ru/", login="test", password="test"
        )

        bl.server_codes = mock_server_codes
        bl.config = mock_config
        bl.logger = mocker.Mock()
        bl.cube_id = "test_cube_id"

        # Мокаем только те методы, которые делают реальные запросы к серверу
        bl.execute_manager_command = mocker.Mock(
            side_effect=mock_execute_manager_command
        )
        bl.get_cubes_list = mocker.Mock(return_value=[])

        bl.h.upload_file_to_server = mocker.Mock(return_value="datasource_test_id")

        return bl

    def test_cube_name_validation_min_length(self, mock_business_logic):
        """Тест валидации минимальной длины имени куба (5 символов)"""
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test",  # 4 символа - должно упасть
                source_name="test_source_12345",
                file_type="psql",
                sql_params=TEST_SQL_PARAMS,
            )

    def test_cube_name_validation_forbidden_chars(self, mock_business_logic):
        """Тест валидации запрещенных символов в имени куба"""
        forbidden_chars = "%^&=;±§`~][}{<>"
        for char in forbidden_chars:
            with pytest.raises(ValueError):
                mock_business_logic.create_sphere(
                    cube_name=f"test_cube{char}",
                    source_name="test_source_12345",
                    file_type="psql",
                    sql_params=TEST_SQL_PARAMS,
                )

    def test_source_name_validation_length(self, mock_business_logic):
        """Тест валидации длины имени источника (5-100 символов)"""
        # Слишком короткое имя
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test",  # 4 символа
                file_type="psql",
                sql_params=TEST_SQL_PARAMS,
            )

        # Слишком длинное имя (>100 символов)
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="a" * 101,  # 101 символ
                file_type="psql",
                sql_params=TEST_SQL_PARAMS,
            )

    def test_file_type_validation(self, mock_business_logic):
        """Тест валидации типа источника данных"""
        valid_types = ["excel", "csv", "mssql", "mysql", "psql", "jdbc", "odbc"]
        # Проверяем, что валидные типы проходят
        for file_type in valid_types:
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type=file_type,
                sql_params={} if file_type in ["excel", "csv"]
                else TEST_SQL_PARAMS_JDBC if file_type == "jdbc"
                else TEST_SQL_PARAMS,
                filepath="test.xlsx"
                if file_type == "excel"
                else "test.csv"
                if file_type == "csv"
                else "",
                separator="," if file_type == "csv" else "",
                encoding="UTF-8" if file_type == "csv" else "",
            )

        # Невалидный тип
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="invalid_type",
            )

    def test_csv_source_encoding_validation(self, mock_business_logic):
        """Тест наличия кодировки для CSV источника"""
        # Отсутствует encoding
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="csv",
                filepath="test.csv",
                separator=","
                # encoding отсутствует
            )

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
        kwargs = {
            "cube_name": "test_cube",
            "source_name": "test_source_12345",
            "update_params": update_params,
            "file_type": "psql",
            "sql_params": TEST_SQL_PARAMS,
        }

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

        mock_business_logic.create_sphere(**kwargs)

    def test_update_types_validation_invalid(self, mock_business_logic):
        """Тест валидации типов обновления для невалидного параметра"""
        # Невалидный тип
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={"type": "invalid_type"},
                sql_params=TEST_SQL_PARAMS,
            )

    def test_file_sources_update_restriction(self, mock_business_logic):
        """Тест ограничения типов обновления для файловых источников"""
        file_sources = ["excel", "csv"]

        for file_type in file_sources:
            # Файловые источники не поддерживают обновление
            with pytest.raises(ValueError):
                mock_business_logic.create_sphere(
                    cube_name="test_cube",
                    source_name="test_source_12345",
                    file_type=file_type,
                    update_params={"type": "инкрементальное"},
                    filepath="test.xlsx" if file_type == "excel" else "test.csv",
                    separator="," if file_type == "csv" else "",
                    encoding="UTF-8" if file_type == "csv" else "",
                )

            # без update_params ошибок нет
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type=file_type,
                filepath="test.xlsx" if file_type == "excel" else "test.csv",
                separator="," if file_type == "csv" else "",
                encoding="UTF-8" if file_type == "csv" else "",
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
        # Все валидные интервалы должны работать
        params = {
            "cube_name": "test_cube",
            "source_name": "test_source_12345",
            "file_type": "psql",
            "update_params": {"type": "интервальное"},
            "user_interval": user_interval,
            "interval_dim": "date",
            "sql_params": TEST_SQL_PARAMS,
        }

        if user_interval in ["с указанной даты", "с и по указанную дату"]:
            params["interval_borders"] = (
                ["01.01.2024"]
                if user_interval == "с указанной даты"
                else ["01.01.2024", "31.12.2024"]
            )

        mock_business_logic.create_sphere(**params)

    def test_user_intervals_validation_invalid(self, mock_business_logic):
        """Тест невалидного интервала пользователя"""
        # в случае невалидного интервала тесты должны упасть
        params = {
            "cube_name": "test_cube",
            "source_name": "test_source_12345",
            "file_type": "psql",
            "update_params": {"type": "интервальное"},
            "user_interval": "invalid_interval",
            "interval_dim": "date",
            "sql_params": TEST_SQL_PARAMS,
        }
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(**params)

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
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={"type": "по расписанию", "schedule": schedule},
                sql_params=TEST_SQL_PARAMS,
            )

        # Невалидное время
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={
                    "type": "по расписанию",
                    "schedule": {
                        "type": "Ежедневно",
                        "time": "25:70",
                        "time_zone": "UTC+3:00",
                    },
                },
                sql_params=TEST_SQL_PARAMS,
            )

        # Невалидная временная зона
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={
                    "type": "по расписанию",
                    "schedule": {
                        "type": "Ежедневно",
                        "time": "18:30",
                        "time_zone": "INVALID_ZONE",
                    },
                },
                sql_params=TEST_SQL_PARAMS,
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
                "modified_records_date": "datetime",
            },  # version по умолчанию = 1
        ]

        for params in valid_params:
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={"type": "обновление измененных записей"},
                sql_params=TEST_SQL_PARAMS,
                modified_records_params=params,
            )

        # Проверка на то, что метод покажет warning из-за некорректного значения version
        spy_logger = mocker.spy(mock_business_logic.logger, "warning")
        warning_params = {
            "modified_records_key": "latitude",
            "modified_records_date": "date",
            "version": 2,
        }
        mock_business_logic.create_sphere(
            cube_name="test_cube",
            source_name="test_source_12345",
            file_type="psql",
            update_params={"type": "обновление измененных записей"},
            sql_params=TEST_SQL_PARAMS,
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
                mock_business_logic.create_sphere(
                    cube_name="test_cube",
                    source_name="test_source_12345",
                    file_type="psql",
                    update_params={"type": "обновление измененных записей"},
                    sql_params=TEST_SQL_PARAMS,
                    modified_records_params=params,
                )

    def test_modified_records_duplicate_fields_error(self, mock_business_logic):
        """Тест ошибки при одинаковых значениях key и date в modified_records_params"""
        # При одинаковых значениях key и date выбрасывается ошибка
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={"type": "обновление измененных записей"},
                sql_params=TEST_SQL_PARAMS,
                modified_records_params={
                    "modified_records_key": "id",
                    "modified_records_date": "id",
                },
            )

    def test_relevance_date_validation(self, mock_business_logic):
        """Тест валидации параметров даты актуальности"""
        # Валидные параметры
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
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                sql_params=TEST_SQL_PARAMS,
                relevance_date=params,
            )

        # Невалидный формат
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                sql_params=TEST_SQL_PARAMS,
                relevance_date={
                    "relevance_date_dimension": "date",
                    "format": "invalid",
                    "consider_filter": True,
                },
            )

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
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                sql_params=TEST_SQL_PARAMS,
                indirect_cpu_load_parameter=params,
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
                mock_business_logic.create_sphere(
                    cube_name="test_cube",
                    source_name="test_source_12345",
                    file_type="psql",
                    sql_params=TEST_SQL_PARAMS,
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
                    [{"name": "increment_dim", "type": dim_type, "id": "dim1"}],
                    [{"name": "value", "type": 4}],
                )
            )
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={"type": "инкрементальное"},
                sql_params=TEST_SQL_PARAMS,
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
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={"type": "инкрементальное"},
                sql_params=TEST_SQL_PARAMS,
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

            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={"type": "интервальное"},
                sql_params=TEST_SQL_PARAMS,
                user_interval="с текущего дня",
                interval_dim="interval_field",
            )

    def test_interval_dim_invalid_type_error(self, mocker, mock_business_logic):
        """Тест ошибки при невалидном типе размерности для интервала"""

        # Невалидный тип (string)
        mock_business_logic.h.get_and_process_dims_and_measures = mocker.Mock(
            return_value=(
                [{"name": "interval_field", "type": 5, "id": "dim1"}],
                [{"name": "value", "type": 4}],
            )
        )

        with pytest.raises(PolymaticaException):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={"type": "интервальное"},
                sql_params=TEST_SQL_PARAMS,
                user_interval="с текущего дня",
                interval_dim="interval_field",
            )

    def test_interval_borders_validation(self, mock_business_logic):
        """Тест валидации временных границ интервалов"""

        # Валидные границы для "с указанной даты"
        mock_business_logic.create_sphere(
            cube_name="test_cube",
            source_name="test_source_12345",
            file_type="psql",
            update_params={"type": "интервальное"},
            sql_params=TEST_SQL_PARAMS,
            user_interval="с указанной даты",
            interval_dim="date",
            interval_borders=["01.01.2024"],
        )

        # Валидные границы для "с и по указанную дату"
        mock_business_logic.create_sphere(
            cube_name="test_cube",
            source_name="test_source_12345",
            file_type="psql",
            update_params={"type": "интервальное"},
            sql_params=TEST_SQL_PARAMS,
            user_interval="с и по указанную дату",
            interval_dim="date",
            interval_borders=["01.01.2024", "31.12.2024"],
        )

        # Невалидные границы для "с и по указанную дату"
        with pytest.raises(ValueError):
            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params={"type": "интервальное"},
                sql_params=TEST_SQL_PARAMS,
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

            mock_business_logic.create_sphere(
                cube_name="test_cube",
                source_name="test_source_12345",
                file_type="psql",
                update_params=params,
                sql_params=TEST_SQL_PARAMS,
            )
        # Проверяем, что предупреждение было залогировано
        assert spy_logger.call_count == 2

    def test_sql_params_required_fields(self, mock_business_logic):
        """Тест обязательных полей в sql_params"""
        # Валидные sql_params
        valid_sql_params = TEST_SQL_PARAMS

        # Проверяем что валидные параметры работают
        mock_business_logic.create_sphere(
            cube_name="test_cube",
            source_name="test_source_12345",
            file_type="psql",
            sql_params=valid_sql_params,
        )

        # Создаем список невалидных sql_params, в каждом не хватает одного ключа
        sql_params = TEST_SQL_PARAMS
        invalid_sql_params_list = [
            {k: v for k, v in sql_params.items() if k != key} for key in sql_params
        ]

        # Проверяем, что с невалидными параметрами тесты падают
        with pytest.raises(ValueError):
            for invalid_sql_params in invalid_sql_params_list:
                mock_business_logic.create_sphere(
                    cube_name="test_cube",
                    source_name="test_source_12345",
                    file_type="psql",
                    sql_params=invalid_sql_params,
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

        mock_business_logic.create_sphere(
            cube_name="test_cube",
            source_name="test_source_12345",
            file_type="psql",
            update_params={"type": "по расписанию", "schedule": schedules},
            sql_params=TEST_SQL_PARAMS,
        )
