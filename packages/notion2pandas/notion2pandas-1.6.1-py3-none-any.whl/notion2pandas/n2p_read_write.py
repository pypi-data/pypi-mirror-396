"""
This module provides functions for reading and writing various property types
to and from Notion. It includes utility functions to handle specific data
types such as title, rich text, checkboxes, dates, and more.

Functions:
- read_value_from_notion: Retrieves values from Notion properties
 based on their type.
- write_value_to_notion: Prepares values for writing to Notion properties
 based on their type.
- Additional read/write functions for specific Notion property types.
"""

from datetime import datetime
import ast
from typing import Any

import pandas as pd


def read_value_from_notion(notion_property: dict, column_name: str,
                           n2p, notion_type: str = '') -> Any:
    """Retrieves the appropriate value from a Notion property
     based on its type.

    This function checks if a specific Notion type is provided. If it is,
    it retrieves the value using that type; otherwise, it infers the type
    from the Notion property itself. The value is then fetched using a
    helper function.

    Args:
        notion_property (dict): A dictionary representing a Notion property.
        column_name (str): The name of the column associated with the property.
        n2p (Notion2PandasClient): The current instance of Notion2PandasClient.
        notion_type (str, optional): A specific type of Notion property
         to use for retrieval.

    Returns:
        The value associated with the specified Notion property and type,
        as determined by the corresponding function in the switcher inside n2p.
    """
    if notion_type:
        return __get_value_from_lambda(notion_property, column_name,
                                       notion_type, n2p, 0)[0]

    notion_property_type = notion_property.get("type")

    return __get_value_from_lambda(notion_property, column_name,
                                   notion_property_type, n2p, 0)[0]


def write_value_to_notion(row_value: Any, column_name: str, notion_type: str,
                          n2p) -> tuple[dict, bool]:
    """Creates a dictionary representing the value
     to be sent to Notion for writing.

    This function takes a row value and retrieves
     the corresponding writing function
    from a switcher inside n2p based on the Notion property type.
     It then calls this function
    to prepare the value for writing.

    Args:
        row_value (any): The value to be prepared for writing
         to the Notion property.
        column_name (str): The name of the column associated with the property.
        notion_type (str): The type of Notion property to use for writing.
        n2p (Notion2PandasClient): The current instance of Notion2PandasClient.

    Returns:
        dict: A dictionary representing the value to be sent to the Notion property.
    """
    return __get_value_from_lambda(row_value, column_name,
                                   notion_type, n2p, 1)


def __invalid_type_function(input_value, column_name):
    return "Invalid: " + str(input_value) + " for column: " + str(column_name)


def __get_value_from_lambda(input_value, column_name, notion_type, n2p,
                            lambda_index) -> tuple[Any, bool]:
    # Define default lambda functions when the notion_type is not found
    default_lambda = __invalid_type_function

    lambdas = n2p.switcher.get(notion_type, (default_lambda, default_lambda))
    current_lambda = lambdas[lambda_index]

    value = __get_inner_value_from_lambda(input_value, column_name, current_lambda, n2p)
    if lambda_index == 0:
        return value, True
    return value


def __get_inner_value_from_lambda(input_value, column_name, current_lambda, n2p) -> Any:
    if current_lambda.num_params == 0:
        return current_lambda.function()
    if current_lambda.num_params == 1:
        return current_lambda.function(input_value)
    if current_lambda.num_params == 2:
        if current_lambda.need_column_name:
            return current_lambda.function(input_value, column_name)
        if current_lambda.need_n2p:
            return current_lambda.function(input_value, n2p)
    if (current_lambda.num_params == 3 and
            current_lambda.need_column_name and
            current_lambda.need_n2p):
        return current_lambda.function(input_value, column_name, n2p)
    return ''


def title_read(notion_property: dict) -> str:
    """Default implementation to read the title property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The plain text of the first title entry if available,
        otherwise an empty string.
    """
    title = notion_property.get('title')
    if title is None or len(title) == 0:
        return ''
    return title[0].get("plain_text")


def title_write(row_value: str) -> tuple[dict, bool]:
    """Default implementation to write the title property
    as a Notion property dictionary.

    Args:
        row_value (str): The title text to be written.

    Returns:
        dict: A dictionary representing the title property
        for Notion, with the title set to an empty list if
        the row value is empty.
    """
    if row_value != '':
        return {"title": [{"type": "text", "text": {"content": row_value}}]}, True
    return {"title": []}, True


def rich_text_read(notion_property: dict) -> str:
    """Default implementation to read the rich text property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The plain text of the first rich text entry if available,
        otherwise an empty string.
    """
    rich_text = notion_property.get('rich_text')
    if rich_text is None or len(rich_text) == 0:
        return ''
    return rich_text[0].get("plain_text")


def rich_text_write(row_value: str) -> tuple[dict, bool]:
    """Default implementation to write the rich text property
    as a Notion property dictionary.

    Args:
        row_value (str): The text content to be written.

    Returns:
        dict: A dictionary representing the rich text property for Notion,
        with an empty list if the row value is empty.
    """
    if row_value != '':
        return {"rich_text": [{"type": "text", "text": {"content": row_value}}]}, True
    return {"rich_text": []}, True


def checkbox_read(notion_property: dict) -> bool:
    """Default implementation to read the checkbox property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        bool: The value of the checkbox property.
    """
    checkbox = notion_property.get('checkbox')
    return checkbox if checkbox is not None else False


def checkbox_write(row_value: bool) -> tuple[dict, bool]:
    """Default implementation to write the checkbox property
    as a Notion property dictionary.

    Args:
        row_value (bool): The checkbox value to be written.

    Returns:
        dict: A dictionary representing the checkbox property for Notion.
    """
    return {'checkbox': row_value}, True


def created_time_read(notion_property: dict) -> str:
    """Default implementation to read the created time property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The created time property as a string.
    """
    created_time = notion_property.get('created_time')
    return created_time if created_time is not None else ''


def created_time_write() -> tuple[str, bool]:
    """Not supported implementation for writing the created time property
    in a Notion property dictionary, as it cannot be modified through the API.

    Returns:
        str: A message indicating that the created time write operation
        is unsupported.
    """
    return 'Not supported from API', False


def number_read(notion_property: dict) -> float:
    """Default implementation to read the number property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        float: The value of the number property, or None if not available.
    """
    number = notion_property.get('number')
    return number if number is not None else float('nan')


def number_write(row_value: float) -> tuple[dict, bool]:
    """Default implementation to write the number property
    as a Notion property dictionary.

    Args:
        row_value (float): The number value to be written.

    Returns:
        dict: A dictionary representing the number property for Notion,
        with None if the value is NaN.
    """
    return ({'number': row_value}, True) if pd.notna(row_value) else ({'number': None}, True)


def email_read(notion_property: dict) -> str:
    """Default implementation to read the email property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The email property value if available, otherwise an empty string.
    """
    email = notion_property.get('email')
    return email if email is not None else ''


def email_write(row_value: str) -> tuple[dict, bool]:
    """Default implementation to write the email property
    as a Notion property dictionary.

    Args:
        row_value (str): The email value to be written.

    Returns:
        dict: A dictionary representing the email property for Notion,
        with None if the row value is an empty string.
    """
    return ({'email': row_value}, True) if row_value != '' else ({'email': None}, True)


def url_read(notion_property: dict) -> str:
    """Default implementation to read the URL property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The URL property value if available, otherwise an empty string.
    """
    url = notion_property.get('url')
    return url if url is not None else ''


def url_write(row_value: str) -> tuple[dict, bool]:
    """Default implementation to write the URL property
    as a Notion property dictionary.

    Args:
        row_value (str): The URL value to be written.

    Returns:
        dict: A dictionary representing the URL property for Notion,
        with None if the row value is an empty string.
    """
    return ({'url': row_value}, True) if row_value != '' else ({'url': None}, True)


def multi_select_read(notion_property: dict) -> str:
    """Default implementation to read the multi-select property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: A string representation of the list of selected names
        for the multi-select property.
    """
    multi_selects = notion_property.get('multi_select', [])
    names = [notion_select.get('name') for notion_select in multi_selects]

    return str(names)


def multi_select_write(row_value: str) -> tuple[dict, bool]:
    """Default implementation to write the multi-select property
    as a Notion property dictionary.

    Args:
        row_value (str): The string representation
         of a list of multi-select options.

    Returns:
        dict: A dictionary representing the multi-select property for Notion.
    """
    if row_value == '':
        return {"multi_select": []}, True

    notion_selects = ast.literal_eval(row_value)
    multi_selects = [{"name": notion_select} for notion_select in notion_selects]

    return {"multi_select": multi_selects}, True


def select_read(notion_property: dict) -> str:
    """Default implementation to read the select property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The name of the selected option if available, otherwise an empty string.
    """
    select = notion_property.get('select')
    return select.get('name') if select is not None else ''


def select_write(row_value: str) -> tuple[dict, bool]:
    """Default implementation to write the select property
    as a Notion property dictionary.

    Args:
        row_value (str): The selected option name to be written.

    Returns:
        dict: A dictionary representing the select property for Notion,
        with None if the row value is an empty string.
    """
    return ({'select': {'name': row_value}}, True) if row_value != '' else ({'select': None}, True)


def date_read(notion_property: dict) -> str:
    """Default implementation to read the date property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The date value if available, otherwise an empty string.
    """
    date = notion_property.get('date')
    return date if date is not None else ''


def date_write(row_value: str) -> tuple[dict, bool]:
    """Default implementation to write the date property
    as a Notion property dictionary.

    Args:
        row_value (str): The date value to be written.

    Returns:
        dict: A dictionary representing the date property for Notion,
        with None if the row value is an empty string.
    """
    return {"date": row_value if row_value != '' else None}, True


def files_read(notion_property: dict) -> list[dict]:
    """Reads a Notion 'files' property and returns it unchanged as a list of file objects.

    Args:
        notion_property (dict): The Notion property dictionary.

    Returns:
        list[dict]: A list of file objects in Notion's native format.
    """
    return notion_property.get("files", [])


def files_write(row_value: list[dict], n2p) -> tuple[dict, bool]:
    """Converts a list of Notion-format file objects back into a Notion 'files' property payload.

    Args:
        row_value (list[dict]): A list of file objects in Notion's native structure.
        n2p: (Unused) Notion2Pandas client, used here for logging.

    Returns:
        tuple[dict, bool]: The Notion property payload and a success flag.
    """
    if not row_value:
        return {"files": []}, True

    valid_files = []

    for f in row_value:
        file_type = f.get("type")

        if file_type == "file":
            data = f.get("file", {})
            if not data.get("url"):
                n2p.logger.warning(f"Skipped file without URL: {f}")
                continue
            valid_files.append(f)
            continue

        if file_type == "file_upload":
            data = f.get("file_upload", {})
            if not data.get("id"):
                n2p.logger.warning(f"Skipped file_upload without ID: {f}")
                continue
            valid_files.append(f)
            continue

        if file_type == "external":
            data = f.get("external", {})
            if not data.get("url"):
                n2p.logger.warning(f"Skipped external file without URL: {f}")
                continue
            valid_files.append(f)
            continue

        n2p.logger.warning(f"Unknown file type: {f}")
        continue

    return {"files": valid_files}, True


def formula_read(notion_property: dict, column_name: str, n2p) -> str:
    """Reads the formula property from a Notion property dictionary
    and returns the computed value.

    Args:
        notion_property (dict): A dictionary representing a Notion property.
        column_name (str): The column name for referencing the formula.
        n2p (Notion2PandasClient): The current instance of Notion2PandasClient.

    Returns:
        str: The computed formula value.
    """
    formula = notion_property.get('formula')
    return read_value_from_notion(formula, column_name, n2p) if formula is not None else ''


def formula_write() -> tuple[str, bool]:
    """Default implementation for writing formula properties,
    indicating that this action is not supported by the API.

    Returns:
        str: Message indicating lack of API support.
    """
    return 'Not supported by the API.', False


def phone_number_read(notion_property: dict) -> str:
    """Default implementation to read the phone number property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The phone number if available, otherwise an empty string.
    """
    phone_number = notion_property.get('phone_number')
    return phone_number if phone_number is not None else ''


def phone_number_write(row_value: str) -> tuple[dict, bool]:
    """Default implementation to write the phone number property
    as a Notion property dictionary.

    Args:
        row_value (str): The phone number to be written.

    Returns:
        dict: A dictionary representing the phone number property for Notion,
        with None if the row value is an empty string.
    """
    return ({'phone_number': row_value}, True) if row_value != '' else \
        ({'phone_number': None}, True)


def status_read(notion_property: dict) -> str:
    """Reads the status property from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The name of the status if available, otherwise None.
    """
    status = notion_property.get('status')
    return status.get('name') if status is not None else ''


def status_write(row_value: str) -> tuple[dict, bool]:
    """Writes the status property as a Notion property dictionary.

    Args:
        row_value (str): The status name to be written.

    Returns:
        dict: A dictionary representing the status property for Notion.
    """
    return {'status': {"name": row_value}}, True


def unique_id_read(notion_property: dict) -> str:
    """Reads the unique ID from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The unique ID, with prefix and number if present, otherwise the number only.
    """
    unique_id = notion_property.get('unique_id')
    if unique_id is None:
        return ''
    if unique_id.get('prefix') is not None:
        return unique_id.get('prefix') + str(unique_id.get('number'))
    return unique_id.get('number')


def unique_id_write() -> tuple[str, bool]:
    """Placeholder for unsupported unique ID write functionality.

    Returns:
        str: A message indicating that the operation
         is not supported by the API.
    """
    return 'Not supported by the API.', False


def created_by_read(notion_property: dict) -> str:
    """Reads the ID of the creator from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The ID of the creator.
    """
    created_by = notion_property.get('created_by')
    if created_by is None:
        return ''
    return created_by.get('id')


def created_by_write() -> tuple[str, bool]:
    """Placeholder for unsupported created_by write functionality.

    Returns:
        str: A message indicating that the operation
         is not supported by the API.
    """
    return 'Not supported by the API.', False


def last_edited_time_read(notion_property: dict) -> str:
    """Reads the last edited time from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The last edited time of the property.
    """
    last_edited_time = notion_property.get('last_edited_time')
    return last_edited_time if last_edited_time is not None else ''


def last_edited_time_write() -> tuple[str, bool]:
    """Placeholder for unsupported last_edited_time write functionality.

    Returns:
        str: A message indicating that the operation
         is not supported by the API.
    """
    return 'Not supported by the API.', False


def string_read(notion_property: dict) -> str:
    """Reads the string value from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The string value from the property.
    """
    string = notion_property.get('string')
    return string if string is not None else ''


def string_write(row_value: str) -> tuple[dict, bool]:
    """Writes a string value to the Notion property dictionary format.

    Args:
        row_value (str): The string value to write.

    Returns:
        dict: A dictionary formatted for the Notion API with the string value,
        or `None` if the value is an empty string.
    """
    return ({'string': row_value}, True) if row_value != '' else ({'string': None}, True)


def boolean_read(notion_property: dict) -> bool:
    """Default implementation to read boolean property
    from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        bool: The value of the boolean property.
    """
    boolean = notion_property.get('boolean')
    return boolean if boolean is not None else False


def boolean_write(row_value: bool) -> tuple[dict, bool]:
    """Default implementation to write boolean property
    as a Notion property dictionary.

    Args:
        row_value (bool): The boolean value to be written.

    Returns:
        dict: A dictionary representing the checkbox property for Notion.
    """
    return {'boolean': row_value}, True


def last_edited_by_read(notion_property: dict) -> str:
    """Reads the ID of the last editor from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: The ID of the user who last edited the property.
    """
    last_edited_by = notion_property.get('last_edited_by')
    if last_edited_by is None:
        return ''
    return last_edited_by.get('id')


def last_edited_by_write() -> tuple[str, bool]:
    """Placeholder for unsupported last_edited_by write functionality.

    Returns:
        str: A message indicating that the operation is not supported by the API.
    """
    return 'Not supported by the API.', False


def button_read() -> str:
    """Placeholder for unsupported button read functionality.

    Returns:
        str: A message indicating that reading button properties is not supported by the API.
    """
    return 'Not supported by the API.'


def button_write() -> tuple[str, bool]:
    """Placeholder for unsupported button write functionality.

    Returns:
        str: A message indicating that writing button properties is not supported by the API.
    """
    return 'Not supported by the API.', False


def relation_read(notion_property: dict) -> str:
    """Reads relation IDs from a Notion property dictionary.

    Args:
        notion_property (dict): A dictionary representing a Notion property.

    Returns:
        str: A string representation of a list of relation IDs.
    """
    relations = notion_property.get('relation', [])
    relation_ids = [relation.get('id') for relation in relations]

    return str(relation_ids)


def relation_write(row_value: str) -> tuple[dict, bool]:
    """Formats a string of relation IDs for the Notion API.

    Args:
        row_value (str): A string representation of a list of relation IDs.

    Returns:
        dict: A dictionary formatted for the Notion API, containing the relation IDs.
    """
    if row_value == '':
        return {"relation": []}, True

    notion_relations = ast.literal_eval(row_value)
    relation_ids = [{"id": notion_relation} for
                    notion_relation in notion_relations]

    return {"relation": relation_ids}, True


def rollup_read(notion_property: dict, column_name: str, n2p) -> str:
    """Reads a rollup property from a Notion property
     dictionary based on its function type.

    Args:
        notion_property (dict): A dictionary representing a Notion property.
        column_name (str): The name of the Notion column.
        n2p (Notion2PandasClient): The current instance of Notion2PandasClient.

    Returns:
        str: The processed value of the rollup property as a string.
    """
    rollup = notion_property.get('rollup')
    if rollup is None:
        return ''
    rollup_function = rollup.get('function')
    value = rollup.get('number') if \
        rollup_function.startswith(('count', 'percent')) else \
        rollup.get('date')

    if rollup_function.startswith('count'):
        return str(value) if value is not None else ''
    if rollup_function.startswith('percent'):
        return f"{str(round(value * 100, 2))}%" if value is not None else ''
    if 'date' in rollup_function:
        if value is None:
            return ''
        if rollup_function == 'date_range':
            return read_value_from_notion(value, column_name, n2p, 'date_range')
        return read_value_from_notion(value, column_name, n2p)
    if rollup_function.startswith('show'):
        return str([read_value_from_notion(item, column_name, n2p)
                    for item in rollup.get('array')])

    if rollup.get('type') in rollup:
        return rollup.get(rollup.get('type'))

    return ''


def rollup_write() -> tuple[str, bool]:
    """Indicates that writing to a rollup property
     is not supported by the Notion API.

    Returns:
        str: A message stating the API does not support rollup writing.
    """
    return 'Not supported by the API.', False


def people_read(notion_property: dict) -> str:
    """Reads a list of people from a Notion property and returns their IDs as a string.

    Args:
        notion_property (dict): A dictionary representing a Notion property
         containing people information.

    Returns:
        str: A string representation of a list of people IDs.
    """
    people = notion_property.get('people')
    if people is None:
        return str([])  # or return an empty string if that's preferred

    return str([notion_person.get('id') for notion_person in people])


def people_write(row_value: str) -> tuple[dict, bool]:
    """Creates a dictionary for writing a list of people to a Notion property.

    Args:
        row_value (str): A string representation of a list of people IDs.

    Returns:
        dict: A dictionary with "people" keys containing user IDs.
    """
    if row_value == '':
        return {"people": []}, True
    people_list = ast.literal_eval(row_value)
    people = [{"id": notion_person, "object": "user"} for notion_person in people_list]
    return {"people": people}, True


def range_date_read(notion_property: dict) -> str:
    """Reads a date range from a Notion property and returns
     the duration between start and end dates.

    Args:
        notion_property (dict): A dictionary representing
         a Notion date range property with 'start' and 'end' dates.

    Returns:
        str: The duration between the start and end dates as a string.
    """
    start_date = parse_iso_date(notion_property['start'])
    end_date = parse_iso_date(notion_property['end'])
    delta = end_date - start_date
    return str(delta)


def range_date_write() -> tuple[str, bool]:
    """Indicates that writing to a date range property
     is not supported by the Notion API.

    Returns:
        str: A message stating the API does not support date range writing.
    """
    return 'Not supported by the API.', False


def parse_iso_date(iso_str: str) -> datetime:
    """Parses an ISO 8601 formatted string into a datetime object.

    Args:
        iso_str (str): A string in ISO 8601 format,
         expected to contain date and time up to seconds.

    Returns:
        datetime: A datetime object corresponding to the parsed date and time.
    """
    return datetime.strptime(iso_str[:19], '%Y-%m-%dT%H:%M:%S')
