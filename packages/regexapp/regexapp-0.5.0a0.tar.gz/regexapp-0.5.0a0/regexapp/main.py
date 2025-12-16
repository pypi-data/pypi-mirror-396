"""Module containing the logic for the regexapp entry-points."""

import sys
import argparse
import re
import yaml
# from os import path
# from textwrap import dedent
from regexapp.application import Application
from regexapp import RegexBuilder
from regexapp.core import enclose_string

from genericlib import Printer
from genericlib import ECODE


def run_gui_application(options):
    """Run regexapp GUI application.

    Parameters
    ----------
    options (argparse.Namespace): argparse.Namespace instance.

    Returns
    -------
    None: will invoke ``regexapp.Application().run()`` and ``sys.exit(ECODE.SUCCESS)``
    if end user requests `--gui`
    """
    if options.gui:
        app = Application()
        app.run()
        sys.exit(ECODE.SUCCESS)


def show_dependency(options):
    if options.dependency:
        from platform import uname, python_version
        from regexapp.config import Data
        lst = [
            Data.main_app_text,
            'Platform: {0.system} {0.release} - Python {1}'.format(
                uname(), python_version()
            ),
            '--------------------',
            'Dependencies:'
        ]

        for pkg in Data.get_dependency().values():
            lst.append('  + Package: {0[package]}'.format(pkg))
            lst.append('             {0[url]}'.format(pkg))

        Printer.print(lst)
        sys.exit(ECODE.SUCCESS)


class Cli:
    """regexapp console CLI application."""

    def __init__(self):

        parser = argparse.ArgumentParser(
            prog='regexapp',
            usage='%(prog)s [options]',
            description='%(prog)s application',
        )

        parser.add_argument(
            '--gui', action='store_true',
            help='Launch a regexapp GUI application.'
        )

        parser.add_argument(
            '-u', '--user-data', type=str, dest='user_data',
            default='',
            help='Required flag: user snippet for regex generation.'
        )

        parser.add_argument(
            '-t', '--test-data', type=str, dest='test_data',
            default='',
            help='User test data.'
        )

        parser.add_argument(
            '-r', '--run-test', action='store_true', dest='test',
            help='To perform test between test data vs generated regex pattern.'
        )

        parser.add_argument(
            '-p', '--platform', type=str, choices=['unittest', 'pytest', 'snippet'],
            default='',
            help='A generated script choice for unittest or pytest test framework.'
        )

        parser.add_argument(
            '--config', type=str,
            default='',
            help='Config settings for generated test script.'
        )

        parser.add_argument(
            '-d', '--dependency', action='store_true',
            help='Show RegexBuilder dependent package(s).'
        )

        self.parser = parser
        self.options = self.parser.parse_args()
        self.kwargs = dict()

    def validate_cli_flags(self):
        """Validate argparse `options`.

        Returns
        -------
        bool: show ``self.parser.print_help()`` and call ``sys.exit(ECODE.BAD)`` if
        user_data flag is empty, otherwise, return True
        """

        if not self.options.user_data:
            self.parser.print_help()
            sys.exit(ECODE.BAD)

        pattern = r'file( *name)?:: *(?P<filename>\S*)'
        m = re.match(pattern, self.options.user_data, re.I)
        if m:
            try:
                with open(m.group('filename')) as stream:
                    self.options.user_data = stream.read()
            except Exception as ex:
                failure = '*** {}: {}'.format(type(ex).__name__, ex)
                print(failure)
                sys.exit(ECODE.BAD)

        if self.options.test_data:
            m = re.match(pattern, self.options.test_data, re.I)
            if m:
                try:
                    with open(m.group('filename')) as stream:
                        self.options.test_data = stream.read()
                except Exception as ex:
                    failure = '*** {}: {}'.format(type(ex).__name__, ex)
                    print(failure)
                    sys.exit(ECODE.BAD)

        if self.options.config:
            config = self.options.config
            m = re.match(pattern, config, re.I)
            if m:
                try:
                    with open(m.group('filename')) as stream:
                        content = stream.read()
                except Exception as ex:
                    failure = '*** {}: {}'.format(type(ex).__name__, ex)
                    print(failure)
                    sys.exit(ECODE.BAD)
            else:
                other_pat = r'''(?x)(
                    prepended_ws|appended_ws|ignore_case|
                    is_line|test_name|max_words|test_cls_name|
                    author|email|company|filename): *'''
                content = re.sub(r' *: *', r': ', config)
                content = re.sub(other_pat, r'\n\1: ', content)
                content = '\n'.join(line.strip(', ') for line in content.splitlines())

            if content:
                try:
                    kwargs = yaml.load(content, Loader=yaml.SafeLoader)
                    if isinstance(kwargs, dict):
                        self.kwargs = kwargs
                    else:
                        failure = '*** INVALID-CONFIG: {}'.format(config)
                        print(failure)
                        sys.exit(ECODE.BAD)
                except Exception as ex:
                    failure = '*** LOADING-CONFIG-ERROR - {}'.format(ex)
                    print(failure)
                    sys.exit(ECODE.BAD)

        return True

    def build_regex_pattern(self):
        """Build regex pattern"""
        factory = RegexBuilder(
            user_data=self.options.user_data,
            **self.kwargs
        )
        factory.build()
        patterns = factory.patterns
        total = len(patterns)
        if total >= 1:
            if total == 1:
                result = 'pattern = r{}'.format(enclose_string(patterns[0]))
                print(result)
            else:
                lst = []
                fmt = 'pattern{} = r{}'
                for index, pattern in enumerate(patterns, 1):
                    lst.append(fmt.format(index, enclose_string(pattern)))
                result = '\n'.join(lst)
                print(result)
            sys.exit(ECODE.SUCCESS)
        else:
            fmt = '*** CANT generate regex pattern from\n{}'
            print(fmt.format(self.options.user_data))
            sys.exit(ECODE.BAD)

    def build_test_script(self):
        """Build test script"""
        platform = self.options.platform.lower()
        if platform:
            tbl = dict(unittest='create_unittest', pytest='create_pytest')
            method_name = tbl.get(platform, 'create_python_test')
            factory = RegexBuilder(
                user_data=self.options.user_data,
                test_data=self.options.test_data,
                **self.kwargs
            )
            factory.build()
            test_script = getattr(factory, method_name)()
            print('\n{}\n'.format(test_script))
            sys.exit(ECODE.SUCCESS)
        else:
            self.build_regex_pattern()

    def run_test(self):
        """Run test"""
        if self.options.test:
            factory = RegexBuilder(
                user_data=self.options.user_data,
                test_data=self.options.test_data,
                **self.kwargs
            )
            factory.build()
            test_result = factory.test(showed=True)
            print(test_result)
            sys.exit(ECODE.SUCCESS)

    def run(self):
        """Take CLI arguments, parse it, and process."""
        show_dependency(self.options)
        run_gui_application(self.options)
        self.validate_cli_flags()
        if not self.options.test_data:
            self.build_regex_pattern()
        self.run_test()
        self.build_test_script()


def execute():
    """Execute regexapp console CLI."""
    app = Cli()
    app.run()
