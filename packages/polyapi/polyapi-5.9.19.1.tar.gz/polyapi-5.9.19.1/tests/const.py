RESPONSE_USER_CUBE_STRUCTURE_PREVIEW_REQUEST = {
    "state": 1,
    "queries": [
        {
            "uuid": "uuid123",
            "command": {
                "plm_type_code": 208,
                "state": 31,
                "links": [],
                "dims": [
                    {
                        "id": "40737f15",
                        "name": "date",
                        "type": 6,
                        "mark": 1,
                        "field_id": "463c0f3b",
                        "db_field": "date",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                    {
                        "id": "528ba8ed",
                        "name": "datetime",
                        "type": 8,
                        "mark": 1,
                        "field_id": "6fbd153f",
                        "db_field": "datetime",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                    {
                        "id": "04df8885",
                        "name": "latitude",
                        "type": 4,
                        "mark": 1,
                        "field_id": "8a0edc5d",
                        "db_field": "latitude",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                    {
                        "id": "9e65f5a4",
                        "name": "longitude",
                        "type": 4,
                        "mark": 1,
                        "field_id": "f61ce78e",
                        "db_field": "longitude",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                ],
                "facts": [
                    {
                        "id": "8abfcb0e",
                        "name": "latitude",
                        "mark": 1,
                        "nulls_allowed": False,
                        "field_id": "8a0edc5d",
                        "db_field": "latitude",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                    {
                        "id": "99a9a656",
                        "name": "longitude",
                        "mark": 1,
                        "nulls_allowed": False,
                        "field_id": "f61ce78e",
                        "db_field": "longitude",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                ],
            },
        }
    ],
}
RESPONSE_USER_CUBE_CREATE_CUBE_REQUEST = {
    "state": 1,
    "queries": [
        {
            "uuid": "uuid123",
            "command": {
                "plm_type_code": 208,
                "state": 43,
                "cube_id": "5ff6667b",
                "cube_name": "Театры",
            },
        }
    ],
}
RESPONSE_USER_CUBE_TEST_SOURCE_CONNECTION_REQUEST = {
    "state": 1,
    "queries": [
        {
            "uuid": "uuid123",
            "command": {
                "plm_type_code": 208,
                "state": 13,
                "status": {"code": 0},
                "logs": "",
            },
        }
    ],
}
RESPONSE_USER_CUBE_EXT_INFO_REQUEST = {
    "state": 1,
    "queries": [
        {
            "uuid": "uuid123",
            "command": {
                "plm_type_code": 208,
                "state": 27,
                "cube_name": "test_cube",
                "datasources": [
                    {
                        "server": "192.168.11.61:5432",
                        "server_type": 8,
                        "login": "testing",
                        "passwd": "",
                        "database": "testing",
                        "sql_query": "SELECT * FROM public.autotest_ui_table;",
                        "skip": -1,
                        "fields": [
                            {"id": "dim1", "name": "id", "type": 2, "mark": 0},
                            {"id": "dim2", "name": "date", "type": 6, "mark": 0},
                            {
                                "id": "e9edbfc1",
                                "name": "novaya_colonka",
                                "type": 5,
                                "mark": 0,
                            },
                        ],
                        "encoding": "",
                        "name": "test_source",
                        "id": "test_source_id",
                        "status": {"code": 0},
                    }
                ],
                "schedule": {"delayed": False, "items": []},
                "interval": {
                    "type": 11,
                    "left_border": "",
                    "right_border": "",
                    "dimension_id": "00000000",
                    "for_the_last_period": "",
                    "number_of_periods": 0,
                },
                "increment_field": "00000000",
                "dims": [
                    {
                        "id": "40737f15",
                        "name": "date",
                        "type": 6,
                        "mark": 1,
                        "field_id": "463c0f3b",
                        "db_field": "date",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                    {
                        "id": "528ba8ed",
                        "name": "datetime",
                        "type": 8,
                        "mark": 1,
                        "field_id": "6fbd153f",
                        "db_field": "datetime",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                    {
                        "id": "04df8885",
                        "name": "latitude",
                        "type": 4,
                        "mark": 1,
                        "field_id": "8a0edc5d",
                        "db_field": "latitude",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                    {
                        "id": "9e65f5a4",
                        "name": "longitude",
                        "type": 4,
                        "mark": 1,
                        "field_id": "f61ce78e",
                        "db_field": "longitude",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                ],
                "facts": [
                    {
                        "id": "8abfcb0e",
                        "name": "latitude",
                        "mark": 1,
                        "nulls_allowed": False,
                        "field_id": "8a0edc5d",
                        "db_field": "latitude",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                    {
                        "id": "99a9a656",
                        "name": "longitude",
                        "mark": 1,
                        "nulls_allowed": False,
                        "field_id": "f61ce78e",
                        "db_field": "longitude",
                        "update_ts": 0,
                        "datasource": "test_source",
                    },
                ],
                "delta": {
                    "primary_key_dim": "45d32583",
                    "timestamp_dim": "80c462ad",
                    "version": 1,
                },
                "relevance_date": {
                    "dimension_id": "00000000",
                    "data_type": 19,
                    "consider_filter": False,
                },
                "cleanup": {"querying_datasources": [], "start_update_after": False},
                "indirect_cpu_load_parameter": {
                    "use_default_value": True,
                    "percent": 80,
                },
                "links": [],
            },
        }
    ],
}
TEST_SQL_PARAMS = {
    "server": "192.168.1.1",
    "login": "u",
    "passwd": "p",
    "database": "d",
    "sql_query": "SELECT 1",
}
TEST_SQL_PARAMS_JDBC = {
    "server": "192.168.1.1",
    "login": "u",
    "passwd": "p",
    "sql_query": "SELECT 1",
}
SERVER_CODES = {
    "manager": {
        "timezone": {
            "UTC-1:00": 0,
            "UTC-2:00": 1,
            "UTC-3:00": 3,
            "UTC-3:30": 4,
            "UTC-4:00": 5,
            "UTC-5:00": 6,
            "UTC-6:00": 7,
            "UTC-7:00": 8,
            "UTC-8:00": 9,
            "UTC-9:00": 10,
            "UTC-9:30": 11,
            "UTC-10:00": 12,
            "UTC-11:00": 13,
            "UTC-12:00": 14,
            "UTC±0:00": 15,
            "UTC+1:00": 16,
            "UTC+2:00": 17,
            "UTC+3:00": 18,
            "UTC+3:30": 19,
            "UTC+4:00": 20,
            "UTC+4:30": 21,
            "UTC+5:00": 22,
            "UTC+5:30": 23,
            "UTC+5:45": 24,
            "UTC+6:00": 25,
            "UTC+6:30": 26,
            "UTC+7:00": 27,
            "UTC+8:00": 28,
            "UTC+8:45": 29,
            "UTC+9:00": 30,
            "UTC+9:30": 31,
            "UTC+10:00": 32,
            "UTC+10:30": 33,
            "UTC+11:00": 34,
            "UTC+12:00": 35,
            "UTC+12:45": 36,
            "UTC+13:00": 37,
            "UTC+13:45": 38,
            "UTC+14:00": 39,
        },
        "data_source_type": {
            "none": 0,
            "file": 1,
            "excel": 2,
            "csv": 3,
            "odbc": 4,
            "mssql": 5,
            "mysql": 6,
            "dsn": 7,
            "psql": 8,
            "h2": 9,
            "oracle": 10,
            "jdbc": 11,
            "jdbc_bridge": 18,
        },
    }
}

DEFAULT_RELEVANCE_DATE = {
    "dimension_id": "00000000",
    "data_type": 19,
    "consider_filter": False,
}
