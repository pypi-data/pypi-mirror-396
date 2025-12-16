"""
File and Folder Operation Utilities

This module provides utilities for file and folder operations including creation,
manipulation, and archive handling. All functions include proper error handling
and support for various file operations.

Functions:
    upsert_folder: Create folder if it doesn't exist, with optional replacement
    upsert_file: Create or update file with content
    change_extension: Change file extension
    export_zip_binary_contents: Save binary content as zip file
    download_zip: Extract or save zip file contents

Exception Classes:
    FileOperationError: Raised when file operations fail

Example:
    >>> # Create folder and file
    >>> upsert_folder("/path/to/folder")
    >>> upsert_file("/path/to/file.txt", "Hello, World!")

    >>> # Change file extension
    >>> new_path = change_extension("/path/to/file.txt", ".md")
    >>> print(new_path)  # "/path/to/file.md"

    >>> # Handle zip files
    >>> files = download_zip("/output/folder", zip_bytes_content=zip_data)
"""

__all__ = [
    "upsert_folder",
    "upsert_file",
    "change_extension",
    "export_zip_binary_contents",
    "download_zip",
]


import io
import os
import pathlib
import shutil
import zipfile
from collections.abc import Callable

from .exceptions import FileOperationError


def upsert_folder(
    folder_path: str, debug_prn: bool = False, replace_folder: bool = False
) -> None:
    """
    Create folder if it doesn't exist, with optional replacement of existing folder.

    Args:
        folder_path (str): Path to folder to create or ensure exists
        debug_prn (bool): Print debug information if True
        replace_folder (bool): Remove and recreate folder if it exists

    Raises:
        FileOperationError: If folder creation fails

    Example:
        >>> upsert_folder("/path/to/new/folder")
        >>> upsert_folder("/path/to/folder", replace_folder=True)  # Recreates folder

    Note:
        If folder_path contains a filename, the directory portion is extracted.
        Creates all necessary parent directories.
    """
    try:
        # Extract directory path if a filename is included
        folder_path = os.path.dirname(folder_path)

        if (
            replace_folder
            and os.path.exists(folder_path)
            and os.path.isdir(folder_path)
        ):
            folder_path = os.path.join(folder_path, "")
            shutil.rmtree(folder_path)

        if debug_prn:
            print(
                {
                    "upsert_folder": os.path.abspath(folder_path),
                    "is_exist": os.path.exists(folder_path),
                }
            )

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    except (OSError, PermissionError) as e:
        raise FileOperationError("create folder", folder_path, str(e))


def upsert_file(
    file_path: str,
    content: object = None,
    write_fn: Callable = None,
    file_update_method: str = "w",
    encoding: str = "utf-8",
    debug_prn: bool = False,
    replace_folder: bool = False,
) -> bool:
    """
    Create or update file with specified content.

    Args:
        file_path (str): Path to file to create or update
        content (Any, optional): Content to write to file
        write_fn (Callable, optional): Custom function for writing content
        file_update_method (str): File open mode ('w', 'a', 'wb', etc.)
        encoding (str): Text encoding for file operations
        debug_prn (bool): Print debug information if True
        replace_folder (bool): Replace parent folder if it exists

    Returns:
        bool: True if operation succeeded

    Raises:
        FileOperationError: If file creation or writing fails

    Example:
        >>> # Simple file creation
        >>> upsert_file("/path/to/file.txt", "Hello, World!")
        True

        >>> # Custom write function
        >>> def custom_writer(file, content):
        ...     file.write(f"Custom: {content}")
        ...     return True
        >>> upsert_file("/path/to/file.txt", "data", write_fn=custom_writer)
        True

        >>> # Binary file
        >>> upsert_file("/path/to/file.bin", b"binary data", file_update_method="wb")
        True
    """
    try:
        upsert_folder(
            folder_path=file_path, debug_prn=debug_prn, replace_folder=replace_folder
        )

        with open(file_path, file_update_method, encoding=encoding) as file:
            if not write_fn:
                file.write(content or "")
                return True
            return write_fn(file=file, content=content)

    except (OSError, PermissionError, UnicodeError) as e:
        raise FileOperationError("create or write file", file_path, str(e))


def change_extension(file_path: str, new_extension: str) -> str:
    """
    Change the extension of a file path.

    Args:
        file_path (str): Original file path
        new_extension (str): New extension (with or without leading dot)

    Returns:
        str: File path with new extension

    Example:
        >>> change_extension("/path/to/file.txt", ".md")
        '/path/to/file.md'
        >>> change_extension("/path/to/file.txt", "json")
        '/path/to/file.json'
    """
    path = pathlib.PurePath(file_path)

    # Ensure extension starts with dot
    new_extension = (
        new_extension if new_extension.startswith(".") else "." + new_extension
    )

    new_file_path = path.with_suffix(new_extension)
    return str(new_file_path)


def export_zip_binary_contents(output_folder: str, zip_bytes_content: bytes) -> str:
    """
    Save binary zip content to a file.

    Args:
        output_folder (str): Path where zip file should be saved
        zip_bytes_content (bytes): Binary zip file content

    Returns:
        str: Success message with file location

    Raises:
        FileOperationError: If zip file creation fails

    Example:
        >>> with open("source.zip", "rb") as f:
        ...     zip_data = f.read()
        >>> result = export_zip_binary_contents("/output/archive", zip_data)
        >>> print(result)  # "successfully downloaded to /output/archive.zip"
    """
    try:
        output_folder = change_extension(output_folder, ".zip")
        upsert_folder(output_folder)

        with open(output_folder, "wb+") as f:
            f.write(zip_bytes_content)

        return f"successfully downloaded to {output_folder}"

    except (OSError, PermissionError) as e:
        raise FileOperationError("export zip content", output_folder, str(e))


def download_zip(
    output_folder: str,
    zip_bytes_content: bytes | None = None,
    existing_zip_file_path: str | None = None,
    is_unpack_archive: bool = True,
) -> str | list[str]:
    """
    Save bytes content to a zip file and optionally extract contents.

    Args:
        output_folder (str): Folder where files should be saved/extracted
        zip_bytes_content (bytes, optional): Zip file as bytes
        existing_zip_file_path (str, optional): Path to existing zip file
        is_unpack_archive (bool): Whether to extract the archive contents

    Returns:
        Union[str, list[str]]: Success message or list of extracted files

    Raises:
        FileOperationError: If zip operations fail
        ValueError: If neither zip_bytes_content nor existing_zip_file_path provided

    Example:
        >>> # Extract zip from bytes
        >>> files = download_zip("/output", zip_bytes_content=zip_data)
        >>> print(files)  # ['file1.txt', 'file2.txt', 'folder/']

        >>> # Just save zip file without extracting
        >>> result = download_zip("/output", zip_data, is_unpack_archive=False)
        >>> print(result)  # "successfully downloaded to /output.zip"

        >>> # Extract existing zip file
        >>> files = download_zip("/output", existing_zip_file_path="/path/to/archive.zip")
    """
    try:
        # Ensure output folder ends with slash for consistency
        output_folder = (
            output_folder if output_folder.endswith("/") else output_folder + "/"
        )

        # Handle case where we just want to save the zip file
        if not is_unpack_archive:
            if zip_bytes_content:
                return export_zip_binary_contents(
                    output_folder=output_folder, zip_bytes_content=zip_bytes_content
                )

            if existing_zip_file_path and os.path.exists(existing_zip_file_path):
                output_zip = os.path.join(output_folder, "archive.zip")
                upsert_folder(output_folder)
                shutil.copy(src=existing_zip_file_path, dst=output_zip)
                return f"zip available at {output_zip}"

        # Extract zip contents
        zip_file = None
        upsert_folder(output_folder)

        if zip_bytes_content:
            zip_file = zipfile.ZipFile(io.BytesIO(zip_bytes_content), "r")
        elif existing_zip_file_path and os.path.exists(existing_zip_file_path):
            zip_file = zipfile.ZipFile(existing_zip_file_path, "r")

        if not zip_file:
            raise ValueError(
                "Must provide either zip_bytes_content or existing_zip_file_path"
            )

        # Extract all files
        zip_file.extractall(output_folder)
        file_list = os.listdir(output_folder)
        zip_file.close()

        return file_list

    except (OSError, PermissionError, zipfile.BadZipFile) as e:
        raise FileOperationError("download and extract zip", output_folder, str(e))
    except ValueError as e:
        raise e  # Re-raise ValueError as-is
