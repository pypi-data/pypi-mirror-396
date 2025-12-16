"""Module containing the attributes for regexapp."""

from os import path

from pathlib import Path
from pathlib import PurePath

import yaml

from genericlib import version as gtlib_version
from genericlib import File

__version__ = '0.5.1a1'
version = __version__
__edition__ = 'Community'
edition = __edition__

__all__ = [
    'version',
    'edition',
    'Data'
]


class Data:
    # app yaml files
    system_reference_filename = str(
        PurePath(
            Path(__file__).parent,
            'system_references.yaml'
        )
    )
    symbol_reference_filename = str(
        PurePath(
            Path(__file__).parent,
            'symbols.yaml'
        )
    )
    sample_user_keywords_filename = str(
        PurePath(
            Path(__file__).parent,
            'sample_user_keywords.yaml'
        )
    )
    user_reference_filename = str(
        PurePath(
            Path.home(),
            '.geekstrident',
            'regexapp',
            'user_references.yaml'
        )
    )

    app_version = version

    # main app
    main_app_text = f'RegexApp v{version}'

    # packages
    pyyaml_text = f'pyyaml v{yaml.__version__}'
    pyyaml_link = 'https://pypi.org/project/PyYAML/'

    gtgenlib_text = f"genericlib v{gtlib_version}"
    gtgenlib_link = "https://pypi.org/project/genericlib/"

    # company
    company = 'Geeks Trident LLC'
    company_full_name = company
    company_name = "Geeks Trident"
    company_url = 'https://www.geekstrident.com/'

    # URL
    repo_url = 'https://github.com/Geeks-Trident-LLC/regexapp'
    documentation_url = path.join(repo_url, 'blob/develop/README.md')
    license_url = path.join(repo_url, 'blob/develop/LICENSE')

    # License
    years = '2022'
    license_name = f'{company_name} License'
    copyright_text = f'Copyright \xa9 {years}'
    with open("LICENSE", encoding="utf-8") as f:
        license = f.read()

    @classmethod
    def get_dependency(cls):
        dependencies = dict(
            pyyaml=dict(
                package=cls.pyyaml_text,
                url=cls.pyyaml_link
            ),
            gtgenlib=dict(
                package=cls.gtgenlib_text,
                url=cls.gtgenlib_link
            )
        )
        return dependencies

    @classmethod
    def get_app_keywords(cls):
        with open(cls.system_reference_filename) as stream:
            content = stream.read()
            return content

    @classmethod
    def get_defined_symbols(cls):
        with open(cls.symbol_reference_filename) as stream:
            content = stream.read()
            return content

    @classmethod
    def get_user_custom_keywords(cls):
        filename = cls.user_reference_filename
        sample_file = cls.sample_user_keywords_filename
        if not File.is_exist(filename):
            File.create(filename)
            File.copy_file(sample_file, filename)

        with open(filename) as stream:
            content = stream.read()
            return content
