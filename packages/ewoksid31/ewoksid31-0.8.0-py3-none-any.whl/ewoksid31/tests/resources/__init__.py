import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


def resource_filename(*args) -> str:
    return os.path.join(ROOT_DIR, *args)
