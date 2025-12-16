import inspect
import os
import sys
import warnings
from typing import Callable, List


MAX_DEPTH = 50


class FolderNotFoundError(OSError):
    pass


def lsdir(
    path: str,
    return_full_path: bool = True,
    files: bool = True,
    folders: bool = True,
    filter: Callable = None
) -> List[str]:
    """
    Retrieves a list of file/folder names from a specified directory path. 

    Parameters
    ----------
    path: str
        The directory path from which to retrieve file/folder names.
        
    return_full_path: bool, optional
        If `True`, the function will return the full path for each file/folder.
        If `False`, it will return just the file/folder names. Default value is `True`.
        
    files: bool, optional
        If `True`, the function will include files in the returned list.
        If `False`, it will not include any files. Default value is `True`.
        
    folders: bool, optional
        If `True`, the function will include folder names in the returned list.
        If `False`, it will not include any folder names. Default value is `True`.
        
    filter: Callable, optional
        If specified, this function will be applied to filter the returned list.
        The function should take a string parameter (the file/folder name or full path, 
        depending on `return_full_path`) and return a boolean value.

    Returns
    -------
    List[str]
        A sorted list of file and/or folder names (or path depending upon return_full_path attribute) from the specified 
        directory that meet any specified filter condition.

    Raises
    ----------
    NotADirectoryError: if the specified path does not exist or is not a directory.
    
    ValueError: if `files`, `folders`, and `filter` are all `False` or `None`, as this would result in no output.
    
    Warning: if both `files` and `folders` are `True` and a `filter` function is also specified.
    """
    real_path = os.path.realpath(path)
    if not os.path.isdir(real_path):
        raise NotADirectoryError(f"'{path}' (searched as '{real_path}')")
    if not (files or folders or filter):
        raise ValueError("Asking for no files or folders, and with no filter?")
    elif (files or folders) and filter:
        warnings.warn(
            "a custom filter was specified but files "
            "and folders parameters are still set to `True`."
        )
    full_paths = [
        os.path.join(real_path if return_full_path else path, object)
        for object in os.listdir(real_path)
    ]
    return sorted([
        full_path for full_path in full_paths
        if (
            (files and os.path.isfile(full_path))
            or (folders and os.path.isdir(full_path))
            or filter is not None and filter(full_path)
        )
    ])


def midir(path: str) -> str:
    """
    Returns the directory name of the given path

    Parameters
    ----------
    path: str
        Path to a file or a directory 

    Returns
    -------
    str: Directory name of the given path
    """
    return os.path.dirname(path)


def get_caller() -> str:
    """
    Returns the filename of the caller

    Returns
    -------
    str: The name of the file that contains the current execution point 
    """
    return inspect.stack()[2].filename


def mipath(path: str = None) -> str:
    """
    Returns the canonical path

    Parameters
    ----------
    path: (str, optional)
        File or directory path. Defaults to None.

    Returns
    -------
    str: Canonical path of the current execution point or given path
    """
    if path is None:
        return os.path.realpath(get_caller())
    else:
        return os.path.realpath(path)


def midir(path: str = None) -> str:
    """
    Returns the directory name from the given path

    Parameters
    ----------
    path: str, optional
        File or directory path. Defaults to None.

    Returns
    -------
    str: Directory name of the current execution point or given path
    """
    if path is None:
        return os.path.dirname(get_caller())
    else:
        return os.path.dirname(path)


def root_levels(levels: int = 1) -> None:
    """
    Adds directories to sys.path
    Starts from the directory of the caller file and move up the directory hierarchy.
    Number of levels to move up is determined by input argument.

    Parameters
    ----------
    levels: int
        Levels to move up the directory hierarchy. Defaults to 1.
    
    Raises
    ------
    TypeError
    ValueError
    """
    folder = midir(get_caller())
    if not isinstance(levels, int):
        raise TypeError(levels)
    elif levels < 0:
        raise ValueError(f'Expects a positive integer: {levels}')
    while levels:
        if folder not in sys.path:
            sys.path.append(folder)
        folder = os.path.dirname(folder)
        levels -= 1


def root_suffix(
    suffix: str,
    max_depth: int = MAX_DEPTH
) -> str:
    """
    Adds directories to sys.path
    Starts from the directory of the caller, moves up the directory hierarchy 
    and adds the first folder with the given suffix to sys.path.

    Parameters
    ----------
    suffix: str
        Suffix to match

    Raises
    ------
    TypeError
    ValueError
    FolderNotFoundError: if no folder with the given suffix is found
    """
    if not isinstance(suffix, str):
        raise TypeError(suffix)
    elif not suffix.strip():
        raise ValueError(f'Expects a non-null string: {suffix}')
    folder = midir(get_caller())
    depth = 0
    while depth <= max_depth:
        if (
            os.path.basename(folder).endswith(suffix)
            and folder not in sys.path
        ):
            sys.path.append(folder)
            return folder
        folder = os.path.dirname(folder)
        if folder == '/' or depth == max_depth:
            return scan_downwards(suffix, max_depth)
        depth += 1
    raise FolderNotFoundError(suffix)


def scan_downwards(
    suffix: str,
    max_depth: int
) -> str:
    calldir = midir(get_caller())
    folders = lsdir(calldir, files=False)
    depth = 0
    while folders and depth <= max_depth:
        _folders = []
        broken = False
        for folder in folders:
            if folder.endswith(suffix):
                if folder not in sys.path:
                    sys.path.append(folder)
                broken = True
                break
            else:
                _folders += lsdir(folder, files=False)
        if broken:
            return folder
        folders = _folders
        depth += 1
    raise FolderNotFoundError(suffix)
