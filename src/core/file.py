from os import environ

from dotenv import load_dotenv


def file_name() -> str:
    load_dotenv()
    file = environ.get("FILE_DATA", None)

    if file is None:
        raise ValueError("A variável de ambiente FILE_DATA não está configurada.")
    
    return file
