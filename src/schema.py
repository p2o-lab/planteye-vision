from json import load
from jsonschema import validate, exceptions


def get_schema(schema_file):
    """
    This function returns the json config schema
    :return: Validation schema
    """
    with open(schema_file, 'r') as file:
        schema = load(file)
    return schema


def validate_cfg(json_data, json_schema):
    """
    This function validates config object against config schema
    :param json_schema: json schema to validate against
    :param json_data: config object
    :return: Validation status and message: True if config object is valid, otherwise False
    """

    # Load validation schema
    execute_api_schema = get_schema(json_schema)

    # Validation process
    try:
        validate(instance=json_data, schema=execute_api_schema)
    except exceptions.ValidationError as err:
        return False, err

    message = "Given JSON data is Valid"
    return True, message
