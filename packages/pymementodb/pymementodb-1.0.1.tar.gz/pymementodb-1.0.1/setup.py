from setuptools import setup, find_packages
import pkg_resources
from os import path
from io import open
import pathlib

with pathlib.Path('requirements.txt').open() as requirements_txt:
    INSTALL_REQUIRES = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]

TEST_REQUIRES = []
SRC_DIR = 'pymementodb'

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

about = {}
with open(path.join(this_directory, SRC_DIR, '__version__.py'), mode='r', encoding='utf-8') as f:
    exec(f.read(), about)

setup(name=about['__title__'],
      version=about['__version__'],
      description=about['__description__'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=about['__author__'],
      author_email=about['__author_email__'],
      url=about['__url__'],
      download_url=about['__download_url__'],
      license=about['__license__'],
      packages=find_packages(),
      classifiers=[
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.10',
          'Topic :: Software Development :: Libraries :: Python Modules'
],
    install_requires=INSTALL_REQUIRES,
    tests_require=TEST_REQUIRES,
    include_package_data=True, # files from MANIFEST.in
    test_suite='test',
    project_urls={
        'Source': about['__url__'],
    }
)
