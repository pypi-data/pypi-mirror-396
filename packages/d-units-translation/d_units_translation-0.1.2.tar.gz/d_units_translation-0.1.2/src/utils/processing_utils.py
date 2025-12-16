from typing import Union

def extract_text_from_obj(obj: Union[str, dict, list]) -> str:
    """
    Recursively extracts and concatenates text content from a nested object.

    Args:
        obj: A string, dict, or list representing XML-like content.

    Returns:
        A string containing the extracted text.
    """
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, dict):
        return " ".join(extract_text_from_obj(v) for v in obj.keys())
    elif isinstance(obj, list):
        return " ".join(extract_text_from_obj(i) for i in obj)
    else:
        return ""