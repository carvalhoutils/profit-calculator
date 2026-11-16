from os import environ


def file_name() -> str:
    file = environ.get("FILE_DATA", None)

    if file is None:
        raise ValueError("FILE_DATA environment variable is not set.")
    
    return file
