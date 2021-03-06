# -*- coding: utf-8 -*-
'''
Platform independent versions of some os/os.path functions. Gets around PY2's
lack of support for reading NTFS links.
'''

# Import python lib
from __future__ import absolute_import
import errno
import logging
import os
import re
import struct

# Import 3rd-party libs
import salt.utils
from salt.ext import six

try:
    import win32file
    from pywintypes import error as pywinerror
    HAS_WIN32FILE = True
except ImportError:
    HAS_WIN32FILE = False

log = logging.getLogger(__name__)


def islink(path):
    '''
    Equivalent to os.path.islink()
    '''
    if six.PY3 or not salt.utils.is_windows():
        return os.path.islink(path)

    if not HAS_WIN32FILE:
        log.error('Cannot check if %s is a link, missing required modules', path)

    if not _is_reparse_point(path):
        return False

    # check that it is a symlink reparse point (in case it is something else,
    # like a mount point)
    reparse_data = _get_reparse_data(path)

    # sanity check - this should not happen
    if not reparse_data:
        # not a reparse point
        return False

    # REPARSE_DATA_BUFFER structure - see
    # http://msdn.microsoft.com/en-us/library/ff552012.aspx

    # parse the structure header to work out which type of reparse point this is
    header_parser = struct.Struct('L')
    ReparseTag, = header_parser.unpack(reparse_data[:header_parser.size])
    # http://msdn.microsoft.com/en-us/library/windows/desktop/aa365511.aspx
    if not ReparseTag & 0xA000FFFF == 0xA000000C:
        return False
    else:
        return True


def readlink(path):
    '''
    Equivalent to os.readlink()
    '''
    if six.PY3 or not salt.utils.is_windows():
        return os.readlink(path)

    if not HAS_WIN32FILE:
        log.error('Cannot read %s, missing required modules', path)

    reparse_data = _get_reparse_data(path)

    if not reparse_data:
        # Reproduce *NIX behavior when os.readlink is performed on a path that
        # is not a symbolic link.
        raise OSError(errno.EINVAL, 'Invalid argument: \'{0}\''.format(path))

    # REPARSE_DATA_BUFFER structure - see
    # http://msdn.microsoft.com/en-us/library/ff552012.aspx

    # parse the structure header to work out which type of reparse point this is
    header_parser = struct.Struct('L')
    ReparseTag, = header_parser.unpack(reparse_data[:header_parser.size])
    # http://msdn.microsoft.com/en-us/library/windows/desktop/aa365511.aspx
    if not ReparseTag & 0xA000FFFF == 0xA000000C:
        raise OSError(
            errno.EINVAL,
            '{0} is not a symlink, but another type of reparse point '
            '(0x{0:X}).'.format(ReparseTag)
        )

    # parse as a symlink reparse point structure (the structure for other
    # reparse points is different)
    data_parser = struct.Struct('LHHHHHHL')
    ReparseTag, ReparseDataLength, Reserved, SubstituteNameOffset, \
    SubstituteNameLength, PrintNameOffset, \
    PrintNameLength, Flags = data_parser.unpack(reparse_data[:data_parser.size])

    path_buffer_offset = data_parser.size
    absolute_substitute_name_offset = path_buffer_offset + SubstituteNameOffset
    target_bytes = reparse_data[absolute_substitute_name_offset:absolute_substitute_name_offset+SubstituteNameLength]
    target = target_bytes.decode('UTF-16')

    if target.startswith('\\??\\'):
        target = target[4:]

    try:
        # comes out in 8.3 form; convert it to LFN to make it look nicer
        target = win32file.GetLongPathName(target)
    except pywinerror as exc:
        # If target is on a UNC share, the decoded target will be in the format
        # "UNC\hostanme\sharename\additional\subdirs\under\share". So, in
        # these cases, return the target path in the proper UNC path format.
        if target.startswith('UNC\\'):
            return re.sub(r'^UNC\\+', r'\\\\', target)
        # if file is not found (i.e. bad symlink), return it anyway like on *nix
        if exc.winerror == 2:
            return target
        raise

    return target


def _is_reparse_point(path):
    '''
    Returns True if path is a reparse point; False otherwise.
    '''
    result = win32file.GetFileAttributesW(path)

    if result == -1:
        return False

    return True if result & 0x400 else False


def _get_reparse_data(path):
    '''
    Retrieves the reparse point data structure for the given path.

    If the path is not a reparse point, None is returned.

    See http://msdn.microsoft.com/en-us/library/ff552012.aspx for details on the
    REPARSE_DATA_BUFFER structure returned.
    '''
    # ensure paths are using the right slashes
    path = os.path.normpath(path)

    if not _is_reparse_point(path):
        return None

    fileHandle = None
    try:
        fileHandle = win32file.CreateFileW(
            path,
            0x80000000,  # GENERIC_READ
            1,  # share with other readers
            None,  # no inherit, default security descriptor
            3,  # OPEN_EXISTING
            0x00200000 | 0x02000000  # FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS
        )

        reparseData = win32file.DeviceIoControl(
            fileHandle,
            0x900a8,  # FSCTL_GET_REPARSE_POINT
            None,  # in buffer
            16384  # out buffer size (MAXIMUM_REPARSE_DATA_BUFFER_SIZE)
        )

    finally:
        if fileHandle:
            win32file.CloseHandle(fileHandle)

    return reparseData


def safe_path(path, allow_path=None):
    r'''
    .. versionadded:: 2017.7.3

    Checks that the path is safe for modification by Salt. For example, you
    wouldn't want to have salt delete the contents of ``C:\Windows``. The
    following directories are considered unsafe:

    - C:\, D:\, E:\, etc.
    - \
    - C:\Windows

    Args:

        path (str): The path to check

        allow_paths (str, list): A directory or list of directories inside of
            path that may be safe. For example: ``C:\Windows\TEMP``

    Returns:
        bool: True if safe, otherwise False
    '''
    # Create regex definitions for directories that may be unsafe to modify
    system_root = os.environ.get('SystemRoot', 'C:\\Windows')
    deny_paths = (
        r'[a-z]\:\\$',  # C:\, D:\, etc
        r'\\$',  # \
        re.escape(system_root)  # C:\Windows
    )

    # Make allow_path a list
    if allow_path and not isinstance(allow_path, list):
        allow_path = [allow_path]

    # Create regex definition for directories we may want to make exceptions for
    allow_paths = list()
    if allow_path:
        for item in allow_path:
            allow_paths.append(re.escape(item))

    # Check the path to make sure it's not one of the bad paths
    good_path = True
    for d_path in deny_paths:
        if re.match(d_path, path, flags=re.IGNORECASE) is not None:
            # Found deny path
            good_path = False

    # If local_dest is one of the bad paths, check for exceptions
    if not good_path:
        for a_path in allow_paths:
            if re.match(a_path, path, flags=re.IGNORECASE) is not None:
                # Found exception
                good_path = True

    return good_path
