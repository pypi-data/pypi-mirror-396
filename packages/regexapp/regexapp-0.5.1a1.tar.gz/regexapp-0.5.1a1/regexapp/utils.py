"""Module containing the logic for utilities."""

import re

from argparse import ArgumentParser

from genericlib import DotObject


class MiscArgs:
    @classmethod
    def get_parsed_result_as_data_or_file(cls, *kwflags, data=''):
        parser = ArgumentParser(exit_on_error=False)
        parser.add_argument('val1', nargs='*')
        parser.add_argument('--file', type=str, default='')
        parser.add_argument('--filename', type=str, default='')
        parser.add_argument('--file-name', type=str, default='')
        for flag in kwflags:
            parser.add_argument(flag, type=str, default='')
        parser.add_argument('val2', nargs='*')

        data = str(data).strip()
        first_line = '\n'.join(data.splitlines()[:1])
        pattern = '(?i)file(_?name)?$'

        result = DotObject(
            is_parsed=False, is_data=False, data=data,
            is_file=False, filename='', failure=''
        )

        try:
            options = parser.parse_args(re.split(r' +', first_line))
            result.is_parsed = True
            for flag, val in vars(options).items():
                if re.match(pattern, flag) and val.strip():
                    result.is_file = True
                    result.filename = val.strip()
                else:
                    if flag != 'val1' or flag != 'val2':
                        if val.strip():
                            result.is_data = True
                            result.data = val.strip()
                            return result

            if result.val1 or result.val2:
                result.is_data = True
                return result
            else:
                result.is_parsed = False
                result.failure = 'Invalid data'
                return result

        except Exception as ex:
            result.failure = '{}: {}'.format(type(ex).__name__, ex)
            result.is_parsed = False
            return result

