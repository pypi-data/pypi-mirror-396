def format_error_before_embedding(error_record: dict) -> str:
    """format the doc before embedding"""
    return "\n".join(error_record["errors"])


def format_valid_input_before_embedding(input_record: dict) -> str:
    """format the doc before embedding"""
    return input_record["input"]
