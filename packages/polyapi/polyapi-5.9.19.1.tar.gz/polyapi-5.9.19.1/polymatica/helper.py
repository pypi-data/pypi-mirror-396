#!/usr/bin/python3
""" Содержит вспомогательные (служебные) методы, использующиеся в основном модуле работы с Полиматикой """

import time
from datetime import datetime
from itertools import count
from typing import Any, List, Tuple, Optional

from polymatica.common import FUNCS, MEASURE_STR_INT_TYPES_MAP, POLYMATICA_INT_TYPES_MAP, raise_exception, \
    DATETIME_DETAILS_MAPPING
from polymatica.exceptions import ParseError, PolymaticaException, ScenarioError


class Helper:
    def __init__(self, sc):
        """
        Инициализация вспомогательного класса.
        :param sc: экземпляр класса BusinessLogic
        """
        self.sc = sc
        # хранит функцию-генератор исключений
        self._raise_exception = raise_exception(self.sc)

    def get_cube_id(self, cubes_list: List, cube_name: str) -> str:
        """
        Получить id мультисферы (куба).
        :param cubes_list: список мультисфер
        :param cube_name: название мультисферы
        :return: id мультисферы
        """
        for cube in cubes_list:
            if cube["name"] == cube_name:
                return cube["uuid"]
        return self._raise_exception(
            ValueError,
            f'No such cube "{cube_name}" in cubes list!',
            with_traceback=False,
        )

    def get_measure_or_dim_id(
        self, multisphere_data: dict, measure_dim: str, name
    ) -> str:
        """
        Получить id факта/размерности по имени.
        :param multisphere_data: рабочая область мультисферы
        :param measure_dim: "facts" / "dimensions"
        :param name: название размерности / факта
        :return: id размерности / факта
        """
        for item in multisphere_data[measure_dim]:
            if item["name"].rstrip() == name.rstrip():
                return item["id"]
        error_msg = f'No such {measure_dim[:-1]}: "{name}"'
        return self._raise_exception(
            ValueError,
            error_msg,
            with_traceback=False,
        )

    def get_dim_id(self, multisphere_data: dict, name: str, cube_name: str) -> str:
        """
        Получить идентификатор размерности по её названию.
        :param multisphere_data: рабочая область мультисферы.
        :param name: название размерности.
        :param cube_name: название текущей мультисферы.
        :return: Идентификатор размерности.
        """
        for item in multisphere_data["dimensions"]:
            if item.get("name", "").rstrip() == name.rstrip():
                return item.get("id")
        error_msg = (
            f'Dimension name "{name}" is not valid for Multisphere "{cube_name}"!'
        )
        return self._raise_exception(ValueError, error_msg, with_traceback=False)

    def get_measure_id(self, multisphere_data: dict, name: str, cube_name: str) -> str:
        """
        Получить идентификатор факта по его названию.
        :param multisphere_data: информация по рабочей области мультисферы.
        :param name: название факта.
        :param cube_name: название текущей мультисферы.
        :return: идентификатор факта.
        """
        # поиск идентификатора факта по его названию
        name = name.strip()
        for item in multisphere_data.get("facts"):
            if item.get("name").strip() == name:
                return item.get("id")
        # если не найдено ничего - бросаем ошибку
        error_msg = f'Measure name "{name}" is not valid for Multisphere "{cube_name}"'
        return self._raise_exception(
            PolymaticaException, error_msg, with_traceback=False
        )

    def get_measure_or_dim_name_by_id(self, id_: str, type_: str) -> str:
        """
        Получить название факта/размерности по идентификатору.
        :param id_: (str) идентификатор факта/размерности.
        :param type_: (str) принимает одно из значений: "facts" или "dimensions".
        :return: (str) название факта/размерности.
        """
        # проверка
        if self.sc.multisphere_module_id == "":
            return self._raise_exception(
                ValueError,
                "First create cube and get data from it!",
                with_traceback=False,
            )

        # получить словать с размерностями, фактами и данными
        self.sc.get_multisphere_data()

        # поиск нужного имени
        data = self.sc.multisphere_data.get(type_)
        for item in data:
            if item.get("id") == id_:
                return item.get("name")
        error_msg = 'No {} with id "{}" in the multisphere!'.format(
            "measure" if type_ == "facts" else "dimension", id_
        )
        return self._raise_exception(
            PolymaticaException, error_msg, with_traceback=False
        )

    def get_measure_type(self, name: str) -> int:
        """
        Возвращает целочисленный вид факта по его строковому названию. При передаче неверного строкового вида факта
        будет сгенерирована ошибка.
        :param name: (str) вид факта (в строковом представлении)
        :return: (int) целочисленный вид факта.
        """
        if name not in MEASURE_STR_INT_TYPES_MAP:
            return self._raise_exception(
                ValueError,
                f"No such measure type: {name}",
                with_traceback=False,
            )
        return MEASURE_STR_INT_TYPES_MAP[name]

    def parse_formula(self, formula: str) -> List:
        """
        Парсинг формулы для создания вычислимого факта.
        Разбивает исходную формулу на составляющие, при этом склеивая названия фактов, содержащие пробелы.
        Примеры:
            1. "5 + [Сумма&Март] * 2 + corr([Сумма];[ID])" ->
                ["5", "+", "[Сумма&Март]", "*", "2", "+", "corr([Сумма];[ID])"]
            2. "top([Сумма по всем отделам]; 10) >= 94" -> ["top([Сумма по всем отделам]; 10)", ">=", "94"]
        :param formula: (str) исходная формула.
        :return: (List) составляющие исходной формулы.
        """
        splitted_formula = formula.split()
        result = []
        in_func, in_measure, func_parts, measure_parts = False, False, list(), list()

        for formula_part in splitted_formula:
            # является ли текущая часть формулы функцией
            if not in_func:
                for logic_func in FUNCS:
                    if f"{logic_func}(" in formula_part:
                        in_func = True
            if in_func:
                func_parts.append(formula_part)
                if ")" in formula_part:
                    result.append(" ".join(func_parts))
                    in_func, func_parts = False, list()
                continue

            # является ли текущая часть формулы фактом
            if not in_measure:
                if "[" in formula_part:
                    in_measure = True
            if in_measure:
                measure_parts.append(formula_part)
                if "]" in formula_part:
                    result.append(" ".join(measure_parts))
                    in_measure, measure_parts = False, list()
                continue

            # всё остальное (операнды, числа) добавляем безо всяких преобразований
            result.append(formula_part)
        return result

    def get_scenario_id_by_name(
        self, script_descs: dict, scenario_name: str, scenario_path: str = None
    ) -> str:
        """
        Получение идентификатор сценария по его имени.
        :param script_descs: (dict) данные по всем сценариям.
        :param scenario_name: (str) название сценария.
        :param scenario_path: (str) путь сценария (необязательный параметр).
        :return: идентификатор сценария
        """
        expected_path = scenario_path.split("/") if scenario_path else []
        for script in script_descs:
            if script.get("name") == scenario_name and script.get("path", []) == expected_path:
                return script.get("id")
        return self._raise_exception(
            ScenarioError,
            'Scenario named "{}" not found!'.format(scenario_name),
            with_traceback=False,
        )

    def get_scenario_name_by_id(self, script_descs: dict, scenario_id: str) -> str:
        """
        Получение идентификатор сценария по его имени.
        :param script_descs: (dict) данные по всем сценариям.
        :param scenario_id: (str) идентификатор сценария.
        :return: название сценария
        """
        for script in script_descs:
            if script.get("id") == scenario_id:
                return script.get("name")
        return self._raise_exception(
            ScenarioError,
            'Scenario with id "{}" not found!'.format(scenario_id),
            with_traceback=False,
        )

    def wait_scenario_layer_loaded(self, sc_layer: str) -> Tuple:
        """
        Ожидание загрузки слоя с заданным сценарием.
        :param sc_layer: (str) идентификатор слоя с запускаемым сценарием.
        :return: (Tuple) количество обращений к серверу для получения текущего статуса, число законченных шагов.
        """
        need_check_progress, count_of_requests = True, 0
        while need_check_progress:
            # периодичностью раз в полсекунды запрашиваем результат с сервера и проверяем статус загрузки слоя
            # если не удаётся получить статус - скорее всего нет ответа от сервера - сгенерируем ошибку
            # в таком случае считаем, что сервер не ответил и генерируем ошибку
            time.sleep(0.5)
            count_of_requests += 1
            try:
                progress = self.sc.execute_manager_command(
                    command_name="script", state="run_progress", layer_id=sc_layer
                )
                status = self.parse_result(result=progress, key="status") or {}
                status_code, status_message = status.get("code", -1), status.get(
                    "message", "Unknown error!"
                )
            except Exception:
                # если упала ошибка - не удалось получить ответ от сервера: возможно, он недоступен
                return self._raise_exception(
                    ScenarioError,
                    "Failed to load script! Possible server is unavailable.",
                )

            # проверяем код статуса
            if status_code == 206:
                # сценарий в процессе воспроизведения
                need_check_progress = True
            elif status_code == 207:
                # сценарий полностью выполнен
                need_check_progress = False
            elif status_code == 208:
                # ошибка: сценарий остановлен пользователем (довольно редкий случай)
                return self._raise_exception(
                    ScenarioError,
                    "Script loading was stopped by user!",
                    with_traceback=False,
                )
            elif status_code == -1:
                # ошибка: не удалось получить код текущего статуса
                return self._raise_exception(
                    ScenarioError, "Unable to get status code!", with_traceback=False
                )
            else:
                # прочие ошибки
                return self._raise_exception(
                    ScenarioError, status_message, with_traceback=False
                )
        return count_of_requests, self.parse_result(
            result=progress, key="finished_steps_count"
        )

    def parse_result(
        self, result: dict, key: str, nested_key: str = None, default_value: Any = None
    ) -> Any:
        """
        Парсит и проверяет на ошибки ответ в виде ['queries'][0]['command']['значение']['необязательное значение'].
        :param result: (dict) нераспарсенный ответ от API.
        :param key: (str) ключ, значение которого нужно распарсить.
        :param nested_key: (str) вложенный ключ, значение которого нужно распарсить.
        :param default_value: (Any) значение по-умолчанию для ключа в случае, если этот ключ отсутствует;
            если при отсутствующем ключе данный параметр не будет задан, то будет сгенерирована ошибка.
        :return: (Any) Значение заданного поля.
        """
        base_error_msg = "Error while parsing response: ['queries'][0]['command']"
        request_queries = next(iter(result.get("queries")))
        request_command = request_queries.get("command")

        if key not in request_command:
            if default_value is None:
                error_msg = f"{base_error_msg}['{key}']"
                return self._raise_exception(
                    ParseError, error_msg, with_traceback=False
                )
            value = default_value
        else:
            value = request_command.get(key)

        if nested_key is not None:
            if not isinstance(value, dict):
                error_msg = f"{base_error_msg}['{key}'] is not dict!"
                return self._raise_exception(
                    ParseError, error_msg, with_traceback=False
                )
            if nested_key not in value:
                error_msg = f"{base_error_msg}['{key}']['{nested_key}']"
                return self._raise_exception(
                    ParseError, error_msg, with_traceback=False
                )
            return value.get(nested_key)

        return value

    def get_rows_cols(self, num_row: int = None, num_col: int = None) -> dict:
        """
        Загрузить строки и колонки мультисферы
        :param num_row: (int) количество строк мультисферы
        :param num_col: (int) количество колонок мультисферы
        :return: (dict) command_name="view", state="get_2"
        """
        if (num_row is not None) and (num_col is not None):
            return self.sc.execute_olap_command(
                command_name="view",
                state="get_2",
                from_row=0,
                from_col=0,
                num_row=num_row,
                num_col=num_col,
            )

        # 1000, 2000, 3000, ...
        gen = count(1000, 1000)

        prev_data = []

        result = self.sc.execute_olap_command(
            command_name="view",
            state="get_2",
            from_row=0,
            from_col=0,
            num_row=next(gen),
            num_col=next(gen),
        )
        data = self.parse_result(result=result, key="data")

        while len(prev_data) < len(data):
            prev_data = data
            result = self.sc.execute_olap_command(
                command_name="view",
                state="get_2",
                from_row=0,
                from_col=0,
                num_row=next(gen),
                num_col=next(gen),
            )
            data = self.parse_result(result=result, key="data")
        return result

    def get_pretty_size(
        self, num_bytes: int, presicion: int = 1, units_lang: str = "ru"
    ) -> str:
        """
        Перевод значения в байтах в более крупные единицы измерения.
        :param num_bytes: (int) исходный размер в байтах.
        :param presicion: (int) точность; количество знаков после запятой; по-умолчанию 1.
        :param units_lang: (str) язык отображения размерностей; доступны варианты "ru", "en".
        :return: (str) человеко-читабельная запись исходного размера в байтах; например: "3.5 MB", "7 bytes".
        """
        if units_lang == "ru":
            units = ["байт", "Кбайт", "Мбайт", "Гбайт", "Тбайт"]
        elif units_lang == "en":
            units = ["bytes", "kB", "MB", "GB", "TB"]
        else:
            raise ValueError('Wrong "units_lang" param: "{}"! Available: "ru", "en".')

        len_units = len(units)
        # предел; число, после которого единицы измерения переходят на уровень выше
        threshold = 1024
        for i in range(0, len_units):
            if num_bytes < threshold:
                return f"{num_bytes:g} {units[i]}"
            if i == len_units - 1:
                break
            num_bytes = round(num_bytes / threshold, presicion)
        return f"{num_bytes:g} {units[-1]}"

    def get_datetime_from_timestamp(
        self, timestamp: int, mask: str = r"%d.%m.%Y %H:%M"
    ) -> str:
        """
        Получение даты-времени в человеко-читаемом виде из исходного числа секунд (таймстампа).
        :param timestamp: (int) количество секунд.
        :param mask: (str) маска перевода в формат даты-времени.
        :return: (str) значение даты-времени в человеко-читаемом виде.
        """
        return datetime.fromtimestamp(int(timestamp / 10**6)).strftime(mask)

    def get_filter_rows(self, dim_id: str) -> dict:
        """
        Загрузить строки и колонки мультисферы
        :param dim_id: (str) id размерности
        :return: (dict) command_name="view", state="get_2"
        """

        # 1000, 2000, 3000, ...
        gen = count(1000, 1000)

        prev_data = []

        result = self.sc.execute_olap_command(
            command_name="filter",
            state="pattern_change",
            dimension=dim_id,
            pattern="",
            # кол-во значений отображается на экране, после скролла их становится больше:
            # num=30
            num=next(gen),
        )

        data = self.parse_result(result=result, key="data")

        while len(prev_data) < len(data):
            prev_data = data
            result = self.sc.execute_olap_command(
                command_name="filter",
                state="pattern_change",
                dimension=dim_id,
                pattern="",
                # кол-во значений отображается на экране, после скролла их становится больше:
                # num=30
                num=next(gen),
            )
            data = self.parse_result(result=result, key="data")
        return result

    def get_source_type(self, file_type: str) -> int:
        """
        Метод для получения параметра source_type по file_type. Используется
        в методе create_sphere.
        """
        return self.sc.server_codes["manager"]["data_source_type"][file_type]

    def get_file_type(self, source_type: int) -> str:
        """
        Метод для получения параметра file_type по source_type. Используется
        в методе update_cube.
        """
        data_source_type = self.sc.server_codes["manager"]["data_source_type"]
        return next((k for k, v in data_source_type.items() if v == source_type), None)

    def upload_file_to_server(self, filepath: str):
        """
        Метод для загрузки файла типа excel или csv на сервер. Используется
        в методах create_sphere, update_cube.
        """
        try:
            response = self.sc.exec_request.execute_request(
                params=filepath, method="PUT"
            )
        except Exception as e:
            return self.sc._raise_exception(PolymaticaException, str(e))
        if response.status_code == 200:
            encoded_file_name = response.headers["File-Name"]
            return encoded_file_name
        else:
            return self.sc._raise_exception(
                PolymaticaException,
                f"Unable to get file id from server! URL: {response.url}, STATUS_CODE: {response.status_code}",
                with_traceback=False,
            )

    def get_and_process_dims_and_measures(self,
                                          response: dict,
                                          file_type: str = None,
                                          measures: Optional[dict] = None,
                                          dims: Optional[dict] = None,
                                          links: Optional[list] = None,
                                          all_fields: Optional[list] = None,
                                          sources: Optional[list] = None):
        """
        Метод для получения и обработки словарей с размерностями и фактами в методах
        create_sphere, update_cube.
        """
        dims_rp = self.parse_result(result=response, key="dims")
        measures_rp = self.parse_result(result=response, key="facts")
        # Определяем, используется ли режим нескольких источников
        is_multisource = sources is not None and len(sources) > 1
        processed_dims = self.process_dims(dims, dims_rp, all_fields or [], is_multisource) if dims else dims_rp
        processed_measures = self.process_measures(measures, measures_rp, all_fields or [], is_multisource) if measures else measures_rp

        self.validate_unique_dims_measures_names(processed_dims, processed_measures, all_fields)

        # Обработка link_role для связей
        if links:
            processed_dims, processed_measures = self._apply_link_role(
                links, processed_dims, processed_measures
            )

        for i in processed_dims:
            i.update({"field_type": "field"})
            if file_type == "csv":
                self.sc.checks("check_bom_in_dims_and_measures", i)
        for i in processed_measures:
            i.update({"field_type": "field"})
            if file_type == "csv":
                self.sc.checks("check_bom_in_dims_and_measures", i)
        return processed_dims, processed_measures

    @staticmethod
    def _apply_link_role(links: list, dims: list, measures: list) -> tuple:
        """
        Применяет link_role к связям: удаляет связь из dims или measures в зависимости от роли.
        :param links: список связей в пользовательском формате
        :param dims: список размерностей
        :param measures: список фактов
        :return: кортеж (dims, measures) после обработки link_role
        """
        numeric_types = {k for k, v in POLYMATICA_INT_TYPES_MAP.items()
                         if v in ("uint8", "uint16", "uint32", "uint64", "double")}

        for link in links:
            link_name = link.get("link_name")
            link_role = link.get("link_role", 1)
            
            link_item = next((d for d in dims if d.get("name") == link_name), None) or \
                        next((m for m in measures if m.get("name") == link_name), None)
            
            # применяем link_role только для числовых связей
            if link_item and link_item.get("type") in numeric_types:
                if link_role == 2:
                    # связь только как размерность - удаляем из measures
                    measures = [m for m in measures if m.get("name") != link_name]
                elif link_role == 3:
                    # связь только как факт - удаляем из dims
                    dims = [d for d in dims if d.get("name") != link_name]
                # если link_role == 1, оставляем как есть (и в dims, и в measures)
        
        return dims, measures

    def process_measures(self, measures: dict, measures_rp: List[dict], all_fields: List[dict], is_multisource: bool = False) -> List[dict]:
        """
        Обрабатывает список фактов, полученный от сервера, по правилам
        whitelist/blacklist и применяет пользовательские настройки фактов.

        :param measures: (dict) настройки обработки фактов. Поддерживает поля:
            - "measures_list_mode" (str): режим списка — "blacklist" или "whitelist" (по умолчанию "whitelist").
            - "measures_list" (List[str] или List[dict]): для "blacklist" — имена, которые необходимо исключить;
                для "whitelist" — имена, которые необходимо оставить.
                В режиме нескольких источников это список словарей с полями source_name и measures.
            - "measures_custom_list" (List[dict]): перечень настроек фактов.
        :param measures_rp: (List[dict]) список фактов из ответа сервера.
        :param all_fields: (List[dict]) список всех полей из всех источников
        :param is_multisource: (bool) флаг, указывающий на режим нескольких источников.
        :return: (List[dict]) итоговый список фактов после фильтрации и внедрения настроек
        """
        measures_list_mode = measures.get("measures_list_mode", "whitelist")
        measures_list = measures.get("measures_list", [])
        measures_custom_list = measures.get("measures_custom_list", [])

        # удаление или добавление фактов в соответствии с whitelist/blacklist
        if not measures_list:
            result = measures_rp
        else:
            if is_multisource:
                # Режим нескольких источников: measures_list - это список словарей
                # Создаем маппинг source_id -> source_name из all_fields
                source_id_to_name = {}
                for field in all_fields:
                    source_id = field.get("source_id")
                    source_name = field.get("source_name")
                    if source_id and source_name:
                        source_id_to_name[str(source_id).lower()] = str(source_name).lower()
                
                # Преобразуем measures_list в список словарей с source_name и measure_name (db_field)
                measures_list_items = []
                for item in measures_list:
                    source_name = str(item.get("source_name", "")).lower()
                    item_measures = item.get("measures", [])
                    for measure_name in item_measures:
                        measures_list_items.append({
                            "source_name": source_name,
                            "db_field": str(measure_name).lower()
                        })
                
                # проверка, что в measures_list отсутствуют значения, которых нет среди полей источников
                db_fields_set = {
                    (str(field.get("source_name", "")).lower(), str(field.get("name", "")).lower())
                    for field in all_fields
                }
                wrong_measures = []
                for measure_item in measures_list_items:
                    source_name = measure_item["source_name"]
                    db_field = measure_item["db_field"]
                    if (source_name, db_field) not in db_fields_set:
                        wrong_measures.append(f'"{db_field}" from source "{source_name}"')
                
                if wrong_measures:
                    wrong_measures_str = ", ".join(wrong_measures)
                    return self._raise_exception(
                        ValueError,
                        f"Measure(s) {wrong_measures_str} not found among fields in the data sources!",
                        with_traceback=False,
                    )
                
                # Фильтрация по whitelist/blacklist с учетом источника
                # В measures_rp есть datasource (id источника) и db_field (имя поля)
                # Нужно сопоставить source_name из measures_list_items с datasource через маппинг
                if measures_list_mode == "blacklist":
                    result = [
                        m for m in measures_rp 
                        if not any(
                            measure_item["source_name"] == source_id_to_name.get(str(m.get("datasource", "")).lower(), "") and
                            measure_item["db_field"] == str(m.get("db_field", "")).lower()
                            for measure_item in measures_list_items
                        )
                    ]
                else:
                    result = [
                        m for m in measures_rp 
                        if any(
                            measure_item["source_name"] == source_id_to_name.get(str(m.get("datasource", "")).lower(), "") and
                            measure_item["db_field"] == str(m.get("db_field", "")).lower()
                            for measure_item in measures_list_items
                        )
                    ]
            else:
                # Режим одного источника: measures_list - это список строк
                names_set = {x.lower() for x in measures_list}
                
                # проверка, что в measures_list отсутствуют значения, которых нет среди названий полей источника
                db_fields_set = {str(m.get("db_field", "")).lower() for m in measures_rp}
                wrong_measures = [
                    measure for measure in measures_list
                    if measure.lower() not in db_fields_set
                ]
                if wrong_measures:
                    wrong_measures_str = ", ".join(f'"{measure}"' for measure in wrong_measures)
                    return self._raise_exception(
                        ValueError,
                        f"Measure(s) {wrong_measures_str} not found among fields in the data source!",
                        with_traceback=False,
                    )
                if measures_list_mode == "blacklist":
                    result = [m for m in measures_rp if m.get("name", "").lower() not in names_set]
                else:
                    result = [m for m in measures_rp if m.get("name", "").lower() in names_set]

        # применение пользовательских настроек фактов
        if measures_custom_list:
            for measure_settings in measures_custom_list:
                source_column = measure_settings.get("source_column", "")
                measure_name = measure_settings.get("measure_name") or source_column
                nullable = measure_settings.get("nullable", False)
                
                if is_multisource:
                    # В режиме нескольких источников нужно учитывать source_name
                    source_name = measure_settings.get("source_name", "")
                    
                    # Создаем маппинг source_id -> source_name из all_fields
                    source_id_to_name = {}
                    for field in all_fields:
                        source_id = field.get("source_id")
                        source_name_field = field.get("source_name")
                        if source_id and source_name_field:
                            source_id_to_name[str(source_id).lower()] = str(source_name_field).lower()
                    
                    # проверка: если source_column не пустой, проверяем его наличие среди полей в all_fields
                    if source_column:
                        source_column_exists = any(
                            str(field.get("source_name", "")).lower() == str(source_name).lower() and
                            str(field.get("name", "")).lower() == str(source_column).lower() 
                            for field in all_fields
                        )
                        if not source_column_exists:
                            return self._raise_exception(
                                ValueError,
                                f'Source column "{source_column}" from source "{source_name}" is not found among available fields!',
                                with_traceback=False,
                            )
                    
                    # Находим source_id по source_name
                    source_id = None
                    for sid, sname in source_id_to_name.items():
                        if sname == str(source_name).lower():
                            source_id = sid
                            break
                    
                    measure = None
                    if source_id:
                        measure = next((
                            m for m in result 
                            if str(m.get("datasource", "")).lower() == source_id and
                               str(m.get("db_field", "")).lower() == str(source_column).lower()
                        ), None)
                    
                    if measure is None:
                        return self._raise_exception(
                            ValueError,
                            f'Source column "{source_column}" from source "{source_name}" was filtered out by measures_list and cannot be configured!',
                            with_traceback=False,
                        )
                else:
                    # Режим одного источника
                    # проверка: если source_column не пустой, проверяем его наличие среди db_field в measures_rp
                    if source_column:
                        source_column_exists = any(
                            str(m.get("db_field", "")).lower() == str(source_column).lower() 
                            for m in measures_rp
                        )
                        if not source_column_exists:
                            return self._raise_exception(
                                ValueError,
                                f'Source column "{source_column}" is not found among available fields in the data source!',
                                with_traceback=False,
                            )

                    measure = next((
                        m for m in result 
                        if str(m.get("db_field", "")).lower() == str(source_column).lower()
                    ), None)
                    
                    if measure is None:
                        return self._raise_exception(
                            ValueError,
                            f'Source column "{source_column}" was filtered out by measures_list and cannot be configured!',
                            with_traceback=False,
                        )
                
                # применяем настройки
                measure["name"] = measure_name
                measure["nulls_allowed"] = nullable

            # проверка уникальности итоговых имен фактов
            final_names = [m.get("name", "").lower() for m in result]
            duplicates = [name for name in final_names if final_names.count(name) > 1]
            if duplicates:
                unique_duplicates = sorted(set(duplicates))
                duplicates_str = ", ".join(f'"{d}"' for d in unique_duplicates)
                return self._raise_exception(
                    ValueError,
                    f"Duplicate measure names found after applying custom settings: {duplicates_str}",
                    with_traceback=False,
                )

        return result

    def process_dims(self, dims: dict, dims_rp: List[dict], all_fields: List[dict], is_multisource: bool = False) -> List[dict]:
        """
        Обрабатывает список размерностей, полученный от сервера, по правилам
        whitelist/blacklist и применяет пользовательские настройки размерностей.

        :param dims: (dict) настройки обработки размерностей. Поддерживает поля:
            - "dims_list_mode" (str): режим списка — "blacklist" или "whitelist" (по умолчанию "whitelist").
            - "dims_list" (List[str] или List[dict]): для "blacklist" — имена, которые необходимо исключить;
                для "whitelist" — имена, которые необходимо оставить.
                В режиме нескольких источников это список словарей с полями source_name и dims.
            - "dims_custom_list" (List[dict]): перечень настроек размерностей.
        :param dims_rp: (List[dict]) список размерностей из ответа сервера.
        :param all_fields: (List[dict]) cписок всех полей из всех источников
        :param is_multisource: (bool) флаг, указывающий на режим нескольких источников.
        :return: (List[dict]) итоговый список размерностей после фильтрации и внедрения настроек
        """
        dims_list_mode = dims.get("dims_list_mode", "whitelist")
        dims_list = dims.get("dims_list", [])
        dims_custom_list = dims.get("dims_custom_list", [])

        # удаление или добавление размерностей в соответствии с whitelist/blacklist
        if not dims_list:
            result = dims_rp
        else:
            if is_multisource:
                # Режим нескольких источников: dims_list - это список словарей
                # Создаем маппинг source_id -> source_name из all_fields
                source_id_to_name = {}
                for field in all_fields:
                    source_id = field.get("source_id")
                    source_name = field.get("source_name")
                    if source_id and source_name:
                        source_id_to_name[str(source_id).lower()] = str(source_name).lower()
                
                # Преобразуем dims_list в список словарей с source_name и dim_name (db_field)
                dims_list_items = []
                for item in dims_list:
                    source_name = str(item.get("source_name", "")).lower()
                    item_dims = item.get("dims", [])
                    for dim_name in item_dims:
                        dims_list_items.append({
                            "source_name": source_name,
                            "db_field": str(dim_name).lower()
                        })
                
                # проверка, что в dims_list отсутствуют значения, которых нет среди полей источников
                db_fields_set = {
                    (str(field.get("source_name", "")).lower(), str(field.get("name", "")).lower())
                    for field in all_fields
                }
                wrong_dims = []
                for dim_item in dims_list_items:
                    source_name = dim_item["source_name"]
                    db_field = dim_item["db_field"]
                    if (source_name, db_field) not in db_fields_set:
                        wrong_dims.append(f'"{db_field}" from source "{source_name}"')
                
                if wrong_dims:
                    wrong_dims_str = ", ".join(wrong_dims)
                    return self._raise_exception(
                        ValueError,
                        f"Dims(s) {wrong_dims_str} not found among fields in the data sources!",
                        with_traceback=False,
                    )
                
                # Фильтрация по whitelist/blacklist с учетом источника
                if dims_list_mode == "blacklist":
                    result = [
                        d for d in dims_rp 
                        if not any(
                            dim_item["source_name"] == source_id_to_name.get(str(d.get("datasource", "")).lower(), "") and
                            dim_item["db_field"] == str(d.get("db_field", "")).lower()
                            for dim_item in dims_list_items
                        )
                    ]
                else:
                    result = [
                        d for d in dims_rp 
                        if any(
                            dim_item["source_name"] == source_id_to_name.get(str(d.get("datasource", "")).lower(), "") and
                            dim_item["db_field"] == str(d.get("db_field", "")).lower()
                            for dim_item in dims_list_items
                        )
                    ]
            else:
                # Режим одного источника: dims_list - это список строк
                names_set = {x.lower() for x in dims_list}
                
                # проверка, что в dims_list отсутствуют значения, которых нет среди названий полей источника
                db_fields_set = {str(d.get("db_field", "")).lower() for d in dims_rp}
                wrong_dims = [
                    dim for dim in dims_list
                    if dim.lower() not in db_fields_set
                ]
                if wrong_dims:
                    wrong_dims_str = ", ".join(f'"{dim}"' for dim in wrong_dims)
                    return self._raise_exception(
                        ValueError,
                        f"Dims(s) {wrong_dims_str} not found among fields in the data source!",
                        with_traceback=False,
                    )
                if dims_list and dims_list_mode == "blacklist":
                    result = [d for d in dims_rp if d.get("name", "").lower() not in names_set]
                else:
                    result = [d for d in dims_rp if d.get("name", "").lower() in names_set]

        # добавление настроек и новых имён размерностей
        if dims_custom_list:
            forbidden_names = []
            
            # Добавляем элементы белого списка dims_list
            if dims_list_mode == "whitelist" and isinstance(dims_list, list):
                if is_multisource:
                    # В режиме нескольких источников dims_list - это список словарей
                    for item in dims_list:
                        item_dims = item.get("dims", [])
                        for name in item_dims:
                            forbidden_names.append(str(name).lower())
                else:
                    # В режиме одного источника dims_list - это список строк
                    for name in dims_list:
                        forbidden_names.append(str(name).lower())
            
            # Добавляем имена из dims_rp
            for dim in dims_rp:
                dim_name = dim.get("name")
                if dim_name:
                    forbidden_names.append(str(dim_name).lower())
            
            # Добавляем все dim_name, date_gen_name, date_orig_name из dims_custom_list
            for dim_item in dims_custom_list:
                dim_item_name = dim_item.get("dim_name")
                date_gen_item = dim_item.get("date_gen_name")
                date_orig_item = dim_item.get("date_orig_name")
                if dim_item_name:
                    forbidden_names.append(str(dim_item_name).lower())
                if date_gen_item:
                    forbidden_names.append(str(date_gen_item).lower())
                if date_orig_item:
                    forbidden_names.append(str(date_orig_item).lower())

            for idx, dim_settings in enumerate(dims_custom_list):
                source_column = dim_settings.get("source_column", "")
                dim_name = dim_settings.get("dim_name") or source_column
                date_details = dim_settings.get("date_details")
                date_orig_name = dim_settings.get("date_orig_name")
                date_gen_name = dim_settings.get("date_gen_name")
                
                conflicts = []
                
                if date_orig_name:
                    date_orig_lower = str(date_orig_name).lower()
                    current_forbidden = forbidden_names.copy()
                    if date_orig_lower in current_forbidden:
                        current_forbidden.remove(date_orig_lower)
                    if dim_name:
                        dim_name_lower = str(dim_name).lower()
                        if dim_name_lower in current_forbidden:
                            current_forbidden.remove(dim_name_lower)
                    if date_orig_lower in current_forbidden:
                        conflicts.append(f'"date_orig_name" = "{date_orig_name}"')

                if date_gen_name:
                    date_gen_lower = str(date_gen_name).lower()
                    current_forbidden = forbidden_names.copy()
                    if date_gen_lower in current_forbidden:
                        current_forbidden.remove(date_gen_lower)
                    if dim_name:
                        dim_name_lower = str(dim_name).lower()
                        if dim_name_lower in current_forbidden:
                            current_forbidden.remove(dim_name_lower)
                    if date_gen_lower in current_forbidden:
                        conflicts.append(f'"date_gen_name" = "{date_gen_name}"')
                
                if conflicts:
                    conflicts_str = "; ".join(conflicts)
                    self._raise_exception(
                        ValueError,
                        f'Params in dims_custom_list[{idx}] have conflicts: {conflicts_str}. '
                        f'Date names must not duplicate values from whitelist dims_list, '
                        f'dim_name in other dims_custom_list items or db_field name in source, '
                        f'or date_orig_name/date_gen_name in any dims_custom_list items.',
                        with_traceback=False,
                    )

                if is_multisource:
                    # В режиме нескольких источников нужно учитывать source_name
                    source_name = dim_settings.get("source_name", "")
                    
                    # Создаем маппинг source_id -> source_name из all_fields
                    source_id_to_name = {}
                    for field in all_fields:
                        source_id = field.get("source_id")
                        source_name_field = field.get("source_name")
                        if source_id and source_name_field:
                            source_id_to_name[str(source_id).lower()] = str(source_name_field).lower()
                    
                    # Проверка наличия поля в all_fields
                    source_column_exists = any(
                        str(field.get("source_name", "")).lower() == str(source_name).lower() and
                        str(field.get("name", "")).lower() == str(source_column).lower() 
                        for field in all_fields
                    )
                    if not source_column_exists:
                        return self._raise_exception(
                            ValueError,
                            f'Source column "{source_column}" from source "{source_name}" is not found among available fields!',
                            with_traceback=False,
                        )
                    
                    # Находим source_id по source_name
                    source_id = None
                    for sid, sname in source_id_to_name.items():
                        if sname == str(source_name).lower():
                            source_id = sid
                            break
                    
                    dim = None
                    if source_id:
                        dim = next((
                            d for d in result 
                            if str(d.get("datasource", "")).lower() == source_id and
                               str(d.get("db_field", "")).lower() == str(source_column).lower()
                        ), None)
                    
                    if dim is None:
                        return self._raise_exception(
                            ValueError,
                            f'Source column "{source_column}" from source "{source_name}" was filtered out by dims_list and cannot be configured!',
                            with_traceback=False,
                        )
                else:
                    # В режиме одного источника ищем только по db_field
                    dim = next((d for d in result if str(d.get("db_field", "")).lower() == str(source_column).lower()), None)
                    if dim is None:
                        return self._raise_exception(
                            ValueError,
                            f'Source column "{source_column}" was filtered out by dims_list and cannot be configured!',
                            with_traceback=False,
                        )

                # определяем поведение для date_details в зависимости от типа поля источника
                type_code = dim.get("type")
                type_name_map = {6: "date", 7: "time", 8: "datetime"}
                field_type = type_name_map.get(type_code)

                # вычисляем итоговый список date_details
                final_date_details = None
                if field_type in ("date", "time", "datetime"):
                    if date_details is None:
                        # параметр не указывался — выставляем дефолтные значения по типу
                        if field_type == "datetime":
                            final_date_details = [
                                "year", "quarter", "month", "week", "dow", "date", "time",
                                "hour", "minute", "second", "day"
                            ]
                        elif field_type == "date":
                            final_date_details = ["year", "quarter", "month", "week", "dow", "day"]
                        else:  # time
                            final_date_details = ["hour", "minute", "second"]
                    elif isinstance(date_details, list) and len(date_details) > 0:
                        # проверка допустимости date_details
                        for date_detail in date_details:
                            if date_detail not in DATETIME_DETAILS_MAPPING.get(field_type):
                                return self._raise_exception(
                                    ValueError,
                                    f"Source column {source_column} has field type '{field_type}', "
                                    f"for which date_detail '{date_detail}' is unacceptable",
                                    with_traceback=False,
                                )
                        final_date_details = date_details
                else:
                    final_date_details = None

                descendant_map = {
                    "date": 6,
                    "time": 7,
                    "datetime": 8,
                    "year": 9,
                    "quarter": 10,
                    "month": 11,
                    "day": 12,
                    "week": 13,
                    "dow": 14,
                    "hour": 15,
                    "minute": 16,
                    "second": 17,
                }
                date_descendant = None
                if isinstance(final_date_details, list) and final_date_details:
                    date_descendant = [descendant_map[x] for x in final_date_details if x in descendant_map]

                # применяем настройки
                dim["name"] = dim_name
                if date_descendant:
                    dim["date_descendant"] = date_descendant
                if date_orig_name:
                    dim["new_dimension_name"] = date_orig_name
                if date_gen_name:
                    dim["date_descendant_name"] = date_gen_name

        return result

    def validate_links_names(self, links, fields, measures, dims):
        """
        Проверка пересечений имен связей с полями источников и настройками measures/dims.
        :param links: список связей
        :param fields: список полей из всех источников
        :param measures: настройки фактов
        :param dims: настройки размерностей
        """
        forbidden_names = set()
        
        # добавляем имена всех полей из fields
        for field in fields:
            field_name = field.get("name")
            if field_name:
                forbidden_names.add(field_name)
        
        # добавляем dim_name из dims_custom_list
        if dims and dims.get("dims_custom_list"):
            for dim_item in dims["dims_custom_list"]:
                dim_name = dim_item.get("dim_name")
                if dim_name:
                    forbidden_names.add(dim_name)
                # добавляем date_orig_name и date_gen_name
                date_orig_name = dim_item.get("date_orig_name")
                if date_orig_name:
                    forbidden_names.add(date_orig_name)
                date_gen_name = dim_item.get("date_gen_name")
                if date_gen_name:
                    forbidden_names.add(date_gen_name)
        
        # добавляем measure_name из measures_custom_list
        if measures and measures.get("measures_custom_list"):
            for measure_item in measures["measures_custom_list"]:
                measure_name = measure_item.get("measure_name")
                if measure_name:
                    forbidden_names.add(measure_name)
        
        # проверяем пересечения link_name с forbidden_names
        for link in links:
            link_name = link.get("link_name")
            if link_name in forbidden_names:
                return self._raise_exception(
                    ValueError,
                    f'Link name "{link_name}" conflicts with existing field name. '
                    f'Link names must not match any field names from sources, dimension names, '
                    f'measure names, date_orig_name or date_gen_name values.',
                    with_traceback=False
                )

    def process_links(self, links, fields_by_source, sources):
        """
        Обрабатывает links.
        :param links: список связей в пользовательском формате
        :param fields_by_source: словарь с полями по источникам вида {source_name: [fields]}
        :param sources: список источников (для получения соответствия имен)
        :return: список связей в формате сервера
        """
        
        processed_links = []
        
        for link in links:
            link_name = link.get("link_name")
            field_ids = []
            
            # Собираем все column_N из link
            column_idx = 1
            while f"column_{column_idx}" in link:
                column_name = link.get(f"column_{column_idx}")
                source_name_key = f"source_name_{column_idx}"
                source_name = link.get(source_name_key)
                
                if column_name and source_name:
                    # Ищем поле в конкретном источнике
                    source_fields = fields_by_source.get(source_name, [])
                    field_id = None
                    
                    for field in source_fields:
                        if field.get("name") == column_name:
                            field_id = field.get("id")
                            break
                    
                    if field_id is None:
                        return self._raise_exception(
                            ValueError,
                            f'Column "{column_name}" not found in source "{source_name}" for link "{link_name}"',
                            with_traceback=False
                        )
                    
                    field_ids.append(field_id)
                
                column_idx += 1
            
            processed_link = {
                "id": "",
                "name": link_name,
                "field_ids": field_ids
            }
            
            processed_links.append(processed_link)
        
        return processed_links

    def validate_unique_dims_measures_names(self, dims: List[dict], measures: List[dict], all_fields: List[dict]):
        """
        Метод для проверки уникальности имен размерностей и фактов.
        Имена размерности и факта могут совпадать, проверяются дубликаты отдельно в именах размерностей и отдельно в
        именах фактов.
        :param dims: (List[dict]) список всех размерностей после обработки
        :param measures: (List[dict]) список всех фактов после обработки
        :param all_fields: (List[dict]) список всех полей источника (источников) для получения имени источника
            дублирующейся размерности или факт
        """

        for list_name, validated_list in [("dims", dims), ("measures", measures)]:
            entity_type = "dimension" if list_name == "dims" else "measure"
            final_names = [entity.get("name", "").lower() for entity in validated_list]
            duplicates = [name for name in final_names if final_names.count(name) > 1]
            if duplicates:
                unique_duplicates = sorted(set(duplicates))
                
                # Найти источники для каждого дублирующегося имени
                duplicate_details = []
                for dup_name in unique_duplicates:
                    sources = [
                        field.get("source_name", "unknown")
                        for field in all_fields
                        if field.get("name", "").lower() == dup_name
                    ]
                    sources_str = ", ".join(sorted(set(sources)))
                    duplicate_details.append(f'"{dup_name}" from sources: {sources_str}')
                
                details_str = "; ".join(duplicate_details)
                return self._raise_exception(
                    ValueError,
                    f"Duplicate {entity_type} names found: {details_str}. "
                    f"You must use parameter '{list_name}' to rename or exclude the {entity_type}.",
                    with_traceback=False,
                )
