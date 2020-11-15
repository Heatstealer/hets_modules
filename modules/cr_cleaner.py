"""
This module can read text or binary files to find CR-sign (/r).
Use it to clear files created in Windows with /r/n endlines
to avoid some interpretation issues, such as:
 >>> /usr/bin/env: ‘python\r’: No such file or directory

Module include walker which can find all files from start dir.
Walker will follow setting and options.
To customise the settings you can edit available files extentions.
Add your extensions into TARGET_FILE list.
Also you can ignore some folders from walker.
Add your dir names into IGNORE_FOLDERS list.

Run the script with some flags below (-a or -f) and extra options:
    -a  run the searching of all files and sub-dirs
                    in current file location;
    -f <dir_path>   run the searching of all files and sub-dirs
                    in received dir;
    -f <file_path>  run the searching for selected file
                    It can check all files (not only TARGET_FILES)
                    Also this function can check binary files.
Extra options:
    -v  verbose mode, will print all cr lines which will be found;
    -s  safe mode, will ask about each file to re-write CR signs;
    -i  inspect mode, will only search CR signs without replacing
"""

import os
import sys


TARGET_FILES = ['.py', ]
IGNORE_FOLDERS = ['site-packages', 'node_modules', '.git',
                  'venv', '.env', '.vscode', '.idea']


def is_valid_path(filepath: str) -> bool:
    """
    Return False if dir name in IGNORE_FOLDERS 
    """
    for ign_dir in IGNORE_FOLDERS:
        if ign_dir in filepath:
            return False
    return True


def is_valid(filename: str) -> bool:
    """
    Return False if filename is current module or
    if file extention not in TARGET_FILES
    """
    app_file_name = os.path.split(__file__)[1]
    if filename == app_file_name:
        return False

    file_ext = os.path.splitext(filename)[1]

    if file_ext in TARGET_FILES:
        return True


def walker(init_path: str) -> str:
    """
    Walk all nested dirs from init path
    Yield all allowed files pathes
    """
    for (cur_dir, sub_dirs, sub_files) in os.walk(init_path):
        if not is_valid_path(cur_dir):
            continue
        for fname in sub_files:
            if is_valid(fname):
                yield(os.path.join(cur_dir, fname))


def cr_infile_searching(file_name: str, verbose=True) -> bool:
    """
    Read received file by lines
    :param verbose (bool): if True will print all lines where CR exists
    :return: True if CR sign had been found
    """
    has_cr = False
    try:
        with open(file_name, 'rb') as f:
            for i, line in enumerate(f.readlines()):
                if line.endswith(b'\r\n'):
                    has_cr = True
                    if verbose:
                        print(f'Win32 style file: {file_name}. LINE #{i}: {line}')
                    else:
                        return has_cr
        return has_cr

    except Exception as e:
        print(f'Cant read file: {file_name}.\n', e)


def cr_cleaner(file_name: str, safe_mode=False) -> str:
    """
    Rewrite (binary) received file line by line
    and replace /r/n ends to /n.
    :param safe_mode (bool): if True will ask every file
                             need or not replace CR
    """
    if safe_mode:
        a = input(f'Clear CR from: {f}? [Y / N]')
        if a.lower()[:1] != 'y':
            return
    with open(file_name,"r+b") as f:
        new_f = f.readlines()
        f.seek(0)
        for line in new_f:
            if line.endswith(b'\r\n'):
                line = line.replace(b'\r\n', b'\n')
            f.write(line)
        f.truncate()


def cr_finder(init_dir: str, only_inspect=True,
              verbose=True, safe_mode=False):
    """
    Start walker for received dir
    For each file run inspector and cleaner
    based on params and settings
    :param safe_mode (bool): if True will ask every file
                             need or not replace CR
    :return: True if CR sign had been found
    """
    for file_path in walker(init_dir):
        has_cr = cr_infile_searching(file_path, verbose=verbose)
        if has_cr and not only_inspect:
            cr_cleaner(file_path, safe_mode=safe_mode)


def usage() -> None:
    """Print module documentation"""
    print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        verbose = safe_mode = only_inspect = False
        clear_task_flag = False
        cwd = ''
        for i, arg in enumerate(sys.argv[1:]):
            if arg.lower() == '-a' or arg == '--all':
                if clear_task_flag:
                    print('Can not setup -a and -f flags for 1 command')
                current_file = os.path.abspath(__file__)
                cwd = os.path.split(current_file)[0]
                clear_task_flag = True
            elif arg.lower() == '-f' or arg == '--file':
                if clear_task_flag:
                    print('Can not setup -a and -f flags for 1 command')
                cwd = sys.argv[i+2]
                clear_task_flag = True
                if not os.path.exists(cwd):
                    raise FileNotFoundError(f'Can\'t find path: {cwd}.')
            elif arg.lower() == '-v' or arg == '--verbose':
                verbose = True
            elif arg.lower() == '-s' or arg == '--safe_mode':
                safe_mode = True
            elif arg.lower() == '-i' or arg == '--inspect':
                only_inspect = True
                verbose = True
        if os.path.isdir(cwd):
            cr_finder(
                cwd, only_inspect=only_inspect,
                verbose=verbose, safe_mode=safe_mode)
        else:
            if verbose:
                cr_infile_searching(cwd, verbose=verbose)
            if not only_inspect:
                cr_cleaner(cwd, safe_mode=safe_mode)
    else:
        usage()
