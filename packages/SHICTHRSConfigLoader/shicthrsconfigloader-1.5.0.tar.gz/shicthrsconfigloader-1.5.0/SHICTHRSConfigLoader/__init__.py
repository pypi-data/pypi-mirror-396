# *-* coding: utf-8 *-*
# src\__init__.py
# SHICTHRS CONFIG LOADER
# AUTHOR : SHICTHRS-JNTMTMTM
# Copyright : © 2025-2026 SHICTHRS, Std. All rights reserved.
# lICENSE : GPL-3.0

import os
from colorama import init
init()
from .utils.SHRConfigLoader_readConfigFile import read_ini_file
from .utils.SHRConfigLoader_writeConfigFile import write_ini_file

__all__ = [
    'SHRConfigLoader_read_ini_file',
    'SHRConfigLoader_write_ini_file'
]

print('\033[1mWelcome to use SHRLogCore - ConfigLoader Config System\033[0m\n|  \033[1;34mGithub : https://github.com/JNTMTMTM/SHICTHRS_ConfigLoader\033[0m')
print('|  \033[1mAlgorithms = rule ; Questioning = approval\033[0m')
print('|  \033[1mCopyright : © 2025-2026 SHICTHRS, Std. All rights reserved.\033[0m\n')

class SHRConfigLoaderException(Exception):
    def __init__(self , message: str) -> None:
        self.message = message
    
    def __str__(self):
        return self.message

def SHRConfigLoader_read_ini_file(path : str) -> dict:
    try:
        if os.path.exists(path):
            if os.path.isfile(path) and path.endswith('.ini'):
                return read_ini_file(path)
            else:
                raise SHRConfigLoaderException(f"SHRConfigLoader [ERROR.1000] only ini file is supported not .{path.split('.')[-1]}. File Path : {path} NOT FOUND")
        else:
            raise SHRConfigLoaderException(f"SHRConfigLoader [ERROR.1001] unable to find config file. File Path : {path} NOT FOUND")
    except Exception as e:
        raise SHRConfigLoaderException(f"SHRConfigLoader [ERROR.1002] unable to read config file. File Path : {path} | {e}")

def SHRConfigLoader_write_ini_file(config_dict : dict , path : str) -> None:
    try:
        write_ini_file(config_dict , path)
    except Exception as e:
        raise SHRConfigLoaderException(f"SHRConfigLoader [ERROR.1003] unable to write config file. File Path : {path} | {e}")