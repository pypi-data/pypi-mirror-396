"""Module containing the logic for constant definition"""

import re
from enum import IntFlag


class ICSValue:
    """Treating value as ignore case and ignore space during evaluating
    string equality"""
    def __init__(self, value, *additions):
        self.value = value
        self.additions = additions

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            other_value = re.sub(' +', ' ', str(other.value).lower()).strip()
        else:
            other_value = re.sub(' +', ' ', str(other).lower()).strip()

        chk_lst = []
        for item in [self.value] + list(self.additions):
            value = re.sub(' +', ' ', str(item).lower()).strip()
            chk_lst.append(value)

        chk = other_value in chk_lst
        return chk

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


class ECODE(IntFlag):
    SUCCESS = 0
    BAD = 1


class FWTYPE:
    UNITTEST = ICSValue('unittest')
    PYTEST = ICSValue('pytest')
    ROBOTFRAMEWORK = ICSValue('robotframework', 'rf')


class FORMATTYPE:
    CSV = ICSValue('csv')
    JSON = ICSValue('json')
    YAML = ICSValue('yaml', 'yml')
    TEMPLATE = ICSValue('template')
