from .directory_utils import find_py_directories as find_py_directories
from .symlink_cleaner import clean_existing_symlinks as clean_existing_symlinks

def deploy_to_py_folders() -> bool: ...
