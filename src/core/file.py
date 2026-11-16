from os import environ

from dotenv import load_dotenv


def file_name() -> str:
    load_dotenv()
    file = environ.get("FILE_DATA", None)

    if file is None:
        raise ValueError("FILE_DATA environment variable is not set.")
    
    return file
