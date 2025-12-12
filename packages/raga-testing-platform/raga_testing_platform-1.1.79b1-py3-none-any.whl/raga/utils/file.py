import os


def get_file_name(file_path):
    """
    Extracts the file name, extension, and file name without extension from the given file path.

    Args:
        file_path (str): The path of the file.

    Returns:
        Tuple[str, str, str]: The file name without extension, file extension, and file name.

    Raises:
        ValueError: If the file path is invalid.
    """
    if not isinstance(file_path, str):
        raise ValueError(
            "Invalid file path. Please provide a valid file path string.")

    file_name = os.path.basename(file_path)
    file_name_without_ext, file_extension = os.path.splitext(file_name)

    if file_extension:
        return file_name_without_ext, file_extension, file_name
    else:
        return file_name_without_ext, "", file_name