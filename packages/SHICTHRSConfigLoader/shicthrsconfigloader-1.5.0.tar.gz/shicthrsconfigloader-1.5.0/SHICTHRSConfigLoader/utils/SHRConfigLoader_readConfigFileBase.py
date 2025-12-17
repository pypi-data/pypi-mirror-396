
# src\utils\config\SHRLogCore_readConfigFileBase.py

import configparser

class CaseSensitiveConfigParser(configparser.RawConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def optionxform(self, optionstr):
        return optionstr