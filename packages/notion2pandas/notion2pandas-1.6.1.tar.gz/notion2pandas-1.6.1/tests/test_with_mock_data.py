import os
import json
import logging
import pandas as pd
import pandas.testing as pdt
from unittest.mock import patch
from notion2pandas import Notion2PandasClient


def load_mock_data_simplest_read_table():
    with open("tests/mock_data/NOTION_SIMPLEST_READ_TABLE.json", "r", encoding="utf-8") as file:
        return json.load(file)


def load_mock_data_empty_db_columns():
    with open("tests/mock_data/NOTION_EMPTY_DB_COLUMNS.json", "r", encoding="utf-8") as file:
        return json.load(file)


def load_mock_data_empty_read_table():
    return []


def fake_create_page():
    return 'fake_page_id'


def fake_update_page(page_id):
    return page_id


def fake_fetch_all_property_data_if_needed(page_id: str, prop: dict):
    return prop


@patch.object(Notion2PandasClient, "_fetch_all_property_data_if_needed")
@patch.object(Notion2PandasClient, "collect_paginated_db")
def test_from_notion_db_to_dataframe_simplest_table(mock_executor, mock_fake_fetch):
    n2p = Notion2PandasClient(auth="fake_token", log_level=logging.DEBUG)

    mock_executor.return_value = load_mock_data_simplest_read_table()
    mock_fake_fetch.side_effect = fake_fetch_all_property_data_if_needed

    df_mock = n2p.from_notion_DB_to_dataframe(
        database_id=os.environ["NOTION_SIMPLEST_READ_TABLE"]
    )

    df_pkl = pd.read_pickle("tests/mock_data/NOTION_SIMPLEST_READ_TABLE.pkl")

    pdt.assert_frame_equal(df_mock, df_pkl)


@patch.object(Notion2PandasClient, "_fetch_all_property_data_if_needed")
@patch.object(Notion2PandasClient, "_Notion2PandasClient__get_database_columns_and_types")
@patch.object(Notion2PandasClient, "_update_page")
@patch.object(Notion2PandasClient, "create_page")
@patch.object(Notion2PandasClient, "collect_paginated_db")
def test_add_row_and_update(mock_collect_paginated_db, mock_fake_create_page, mock_fake_update_page,
                            mock_columns_and_types, mock_fake_fetch):
    n2p = Notion2PandasClient(auth="fake_token", log_level=logging.DEBUG)

    mock_collect_paginated_db.return_value = load_mock_data_simplest_read_table()
    mock_fake_create_page.return_value = fake_create_page()
    mock_fake_update_page.return_value = fake_update_page('e6f2dae9-fa49-47ab-9b58-b876c2a1954c')
    mock_columns_and_types.return_value = load_mock_data_empty_db_columns()
    mock_fake_fetch.side_effect = fake_fetch_all_property_data_if_needed

    df_mock = n2p.from_notion_DB_to_dataframe(
        database_id=os.environ["NOTION_SIMPLEST_READ_TABLE"]
    )
    df_mock.at[0, 'Number'] = 126  # love gang <3
    print(df_mock)
    new_row = {'Checkbox': True,
               'Text': 'Fake data', 'Tags': 'asd',
               '👾 Digital Memories': "['5e7d82bd-8e6d-4fe0-8583-5786a9952440',"
                                     " '29039171-7edc-420c-a47a-400e74f4a3a3',"
                                     " '7e1ed224-144d-4c92-9954-59ea2d55dd94']",
               'Test table': "['b091497a-bdb8-4845-bedb-c527a632921f',"
                             " 'e2326d18-8a44-4bf2-8e45-39b5dea54a24']",
               'Number': 18.0, 'Person': "[]", 'Multi-select': "['aa', 'dddd']",
               'URL': 'https://gitlab.com/Jaeger87/notion2pandas', 'Status': 'Done',
               'Date With End': {'start': '2025-01-01T00:00:00.000+01:00',
                                 'end': '2025-01-21T00:35:00.000+01:00', 'time_zone': None},
               'Date': {'start': '2024-03-18', 'end': None, 'time_zone': None},
               'Files & media': [], 'Name': 'Dessert', 'Row_Hash': 0, 'PageID': ''}
    df_mock = pd.concat([df_mock, pd.DataFrame([new_row])], ignore_index=True)
    n2p.update_notion_DB_from_dataframe(os.environ["NOTION_SIMPLEST_READ_TABLE"], df_mock)


@patch.object(Notion2PandasClient, "_fetch_all_property_data_if_needed")
@patch.object(Notion2PandasClient, "_Notion2PandasClient__get_database_columns_and_types")
@patch.object(Notion2PandasClient, "collect_paginated_db")
def test_from_notion_db_to_dataframe_empty_table(mock_executor, mock_columns_and_types,
                                                 mock_fake_fetch):
    expected_columns = {'Checkbox', 'Text', 'Last edited time', 'Tags',
                        'Files & media', '👾 Digital Memories', 'Created time', 'Test table',
                        'Rollup Date Range', 'Rollup', 'ID', 'Number', 'Person', 'Last edited by',
                        'Multi-select', 'Formula', 'Rollup Counter', 'Created by', 'URL', 'Status',
                        'Date With End', 'Date', 'Name', 'PageID', 'Row_Hash'}
    n2p = Notion2PandasClient(auth="fake_token", log_level=logging.DEBUG)

    mock_executor.return_value = load_mock_data_empty_read_table()
    mock_columns_and_types.return_value = load_mock_data_empty_db_columns()
    mock_fake_fetch.side_effect = fake_fetch_all_property_data_if_needed

    df_empty_mock_db = n2p.from_notion_DB_to_dataframe(os.environ['NOTION_EMPTY_DB_ID'])
    columns_empty_db = set(df_empty_mock_db.columns)
    assert columns_empty_db == expected_columns
    assert df_empty_mock_db.empty
