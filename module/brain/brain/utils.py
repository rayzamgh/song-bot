
def trim_quotes(input_string: str) -> str:
    """
    Trims leading and trailing double quotes from the input string.

    Args:
        input_string (str): The string from which double quotes should be removed.

    Returns:
        str: The string after removing leading and trailing double quotes.
    """
    if input_string.startswith('"') and input_string.endswith('"'):
        return input_string[1:-1]
    return input_string