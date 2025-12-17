import json
import os


def save_to_file(data, filename):
    """Saves data to a file in JSON format.

    Args:
        data (list): List of dictionaries to save.
        filename (str): Name of the file to save the data to.
    """
    directory_path = os.environ.get('SAVE_PATH_GPT_HISTORY', os.getcwd())
    directory_path = os.path.expanduser(directory_path)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    file_path = os.path.join(directory_path, filename)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_from_file(filename):
    """Loads data from a file in JSON format.

    Args:
        filename (str): Name of the file to load the data from.

    Returns:
        list of dicionary: List of dictionaries loaded from the file.
        If the file does not exist or is empty, returns an empty list.
    """

    directory_path = os.environ.get('SAVE_PATH_GPT_HISTORY', "~/")
    directory_path = os.path.expanduser(directory_path)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    file_path = os.path.join(directory_path, filename)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
