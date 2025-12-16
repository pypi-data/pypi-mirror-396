from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='error_helper_by_delica',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description="A Python package for checking input parameters and printing informative error messages",
    author="Delica Leboe-McGowan",
    author_email="stormindustries22@outlook.com",
    packages=['error_helper_by_delica'],
    install_requires=[

    ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
