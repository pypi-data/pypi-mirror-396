import re
from os import path

from setuptools import setup, find_packages


def read(*paths):
    filename = path.join(path.abspath(path.dirname(__file__)), *paths)
    with open(filename, 'r') as f:
        return f.read()


def find_version(*paths):
    contents = read(*paths)
    match = re.search(r'^__version__ = [\'"]([^\'"]+)[\'"]', contents, re.M)
    if not match:
        raise RuntimeError('Unable to find version string.')
    return match.group(1)


setup(
    name='GEDataSdk',
    version=find_version('gesdk', 'sdk.py'),
    description='Official GEData Analytics library for Python',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='',
    license='Apache',
    author='GEData',
    author_email='pony@gravity-engine.com',
    packages=find_packages(),
    platforms=["all"],
    install_requires=['requests'],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
)
