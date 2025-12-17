import os
import pandas as pd
from notion2pandas import Notion2PandasClient


def test_simplest_read_from_a_notion_database():
    """This test just download from notion a database with any kind of column
    and verify """
    n2p = Notion2PandasClient(auth=os.environ["NOTION_TOKEN"])
    df_from_notion = n2p.from_notion_DB_to_dataframe(os.environ["NOTION_SIMPLEST_READ_TABLE"])
    new_row = { 'Checkbox': True, 'Text': 'Fake data', 'Tags': 'asd', 'Email': 'notion2pandas@test.com',
                '👾 Digital Memories': "['5e7d82bd-8e6d-4fe0-8583-5786a9952440',"
                                      " '29039171-7edc-420c-a47a-400e74f4a3a3',"
                                      " '7e1ed224-144d-4c92-9954-59ea2d55dd94']",
                'Test table': "['b091497a-bdb8-4845-bedb-c527a632921f',"
                              " 'e2326d18-8a44-4bf2-8e45-39b5dea54a24']",
                'Number': 18.0, 'Person': "[]", 'Multi-select': "['aa', 'dddd']",
                'URL': 'https://gitlab.com/Jaeger87/notion2pandas', 'Status': 'Done',
                'Date With End': {'start': '2025-01-01T00:00:00.000+01:00',
                                  'end': '2025-01-21T00:35:00.000+01:00', 'time_zone': None},
                'Date':  {'start': '2024-03-18', 'end': None, 'time_zone': None},
                'Files & media': [], 'Name': 'Dessert', 'Phone': '5555',
                'Row_Hash': 0, 'PageID': ''}

    df_from_notion_with_row_added = pd.concat([df_from_notion, pd.DataFrame([new_row])], ignore_index=True)
    df_from_notion_with_row_added.loc[df_from_notion_with_row_added['Name'] == 'primo', 'Number'] = 126 #love gang <3
    n2p.update_notion_DB_from_dataframe(os.environ["NOTION_SIMPLEST_READ_TABLE"], df_from_notion_with_row_added)

    df_from_notion_updated = n2p.from_notion_DB_to_dataframe(os.environ["NOTION_SIMPLEST_READ_TABLE"])

    valueToTest = df_from_notion_updated.loc[df_from_notion_updated['Name'] == 'primo', 'Number'].values[0]

    assert df_from_notion_with_row_added.shape == df_from_notion_updated.shape
    assert valueToTest == 126

    indexToDelete = df_from_notion_updated.index[df_from_notion_updated['Name'] == 'Dessert'][0]
    n2p.delete_rows_and_pages(df_from_notion_updated, [indexToDelete])
    df_from_notion_updated.loc[df_from_notion_updated['Name'] == 'primo', 'Number'] = 6
    n2p.update_notion_DB_from_dataframe(os.environ["NOTION_SIMPLEST_READ_TABLE"], df_from_notion_updated)

    df_from_notion_cleaned = n2p.from_notion_DB_to_dataframe(os.environ["NOTION_SIMPLEST_READ_TABLE"])

    valueToTest2 = df_from_notion_cleaned.loc[df_from_notion_cleaned['Name'] == 'primo', 'Number'].values[0]

    assert df_from_notion_cleaned.shape == df_from_notion.shape
    assert valueToTest2 == 6



def test_create_dataframe_from_empty_database():
    expected_columns = {'Checkbox', 'Text', 'Last edited time', 'Tags',
                        'Files & media', '👾 Digital Memories', 'Created time', 'Test table',
                        'Rollup Date Range', 'Rollup', 'ID', 'Number', 'Person', 'Last edited by',
                        'Multi-select', 'Formula', 'Rollup Counter', 'Created by', 'URL', 'Status',
                        'Date With End', 'Date', 'Name', 'PageID', 'Row_Hash'}
    n2p = Notion2PandasClient(auth=os.environ["NOTION_TOKEN"])
    df_empty_db = n2p.from_notion_DB_to_dataframe(os.environ['NOTION_EMPTY_DB_ID'])
    columns_empty_db = set(df_empty_db.columns)
    print(columns_empty_db)
    print(df_empty_db.head())
    assert columns_empty_db == expected_columns
    assert df_empty_db.empty