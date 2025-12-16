"""
Entry-point logic for the regexapp project.

This module provides the command-line interface (CLI) and GUI entry
points for regexapp. It defines helper functions and the `Cli` class
to parse arguments, validate user input, build regex patterns, generate
test scripts, run tests, and display dependency information.

The entry-points are designed to support both interactive GUI usage
and automated CLI workflows, ensuring flexibility for developers and
end users.
"""

import sys
import argparse
import re
import yaml
from regexapp.application import Application
from regexapp import RegexBuilder
from regexapp.core import enclose_string

from genericlib import ECODE


def run_gui_application(options):
    """
    Launch the regexapp GUI application if requested.

    Parameters
    ----------
    options : argparse.Namespace
        Parsed command-line options. Must contain the `gui` flag.

    Returns
    -------
    None
        Invokes ``Application().run()`` and exits with
        ``ECODE.SUCCESS`` if `--gui` is specified.
    """
    if options.gui:
        app = Application()
        app.run()
        sys.exit(ECODE.SUCCESS)


def show_dependency(options):
    """
    Display dependency information if requested.

    Parameters
    ----------
    options : argparse.Namespace
        Parsed command-line options. Must contain the `dependency` flag.

    Returns
    -------
    None
        Prints platform and dependency details to stdout and exits
        with ``ECODE.SUCCESS`` if `--dependency` is specified.
    """
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

        width = max(len(item) for item in lst)
        txt = '\n'.join('| {1:{0}} |'.format(width, item) for item in lst)
        print('+-{0}-+\n{1}\n+-{0}-+'.format(width * '-', txt))
        sys.exit(ECODE.SUCCESS)


def show_version(options):
    """
    Display the current regexapp version and exit.

    This function checks whether the `--version` flag was provided
    in the parsed CLI options. If so, it imports the `version`
    string from the `regexapp` package, prints it to stdout, and
    terminates the process with a success exit code.

    Parameters
    ----------
    options : argparse.Namespace
        Parsed command-line options. Must contain the `version` flag.

    Returns
    -------
    None
        Prints the application version and exits with
        ``ECODE.SUCCESS`` if `--version` is specified.
    """
    if options.version:
        from regexapp import version
        print(f'regexapp {version}')
        sys.exit(ECODE.SUCCESS)


class Cli:
    """
    Console interface for regexapp.

    This class encapsulates the command-line interface logic, including
    argument parsing, validation, regex pattern generation, test script
    creation, and test execution.

    Attributes
    ----------
    parser : argparse.ArgumentParser
        Argument parser configured with regexapp options.
    options : argparse.Namespace
        Parsed command-line arguments.
    kwargs : dict
        Additional keyword arguments loaded from configuration.
    """

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
            help='Show RegexApp dependent package(s).'
        )

        parser.add_argument(
            '-v', '--version', action='store_true',
            help='Show RegexApp version.'
        )

        self.parser = parser
        self.options = self.parser.parse_args()
        self.kwargs = dict()

    def validate_cli_flags(self):
        """
        Validate CLI flags and load external data if specified.

        Returns
        -------
        bool
            True if validation succeeds. If required flags are missing
            or files cannot be loaded, prints an error/help message and
            exits with ``ECODE.BAD``.
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
        """
        Build and print regex patterns from user data.

        Returns
        -------
        None
            Prints generated regex patterns to stdout and exits with
            ``ECODE.SUCCESS`` if successful. Exits with ``ECODE.BAD``
            if no patterns can be generated.
        """
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
        """
        Build and print a test script for the chosen platform.

        Returns
        -------
        None
            Generates an unittest/pytest/snippet script based on CLI
            options, prints it to stdout, and exits with ``ECODE.SUCCESS``.
            Falls back to regex pattern generation if no platform is set.
        """
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
        """
        Execute regex pattern tests against provided test data.

        Returns
        -------
        None
            Runs tests and prints results to stdout. Exits with
            ``ECODE.SUCCESS`` upon completion.
        """
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
        """
        Process CLI arguments and execute the requested workflow.

        Returns
        -------
        None
            Handles dependency display, GUI launch, validation,
            regex generation, test execution, and script creation
            based on CLI flags.
        """
        show_version(self.options)
        show_dependency(self.options)
        run_gui_application(self.options)
        self.validate_cli_flags()
        if not self.options.test_data:
            self.build_regex_pattern()
        self.run_test()
        self.build_test_script()


def execute():
    """
    Execute the regexapp CLI entry-point.

    Returns
    -------
    None
        Instantiates the `Cli` class and runs the application.
    """
    app = Cli()
    app.run()
