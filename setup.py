from setuptools import setup, find_packages
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('s3aads/__init__.py').read(),
    re.M
    ).group(1)

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

for name in ['s3aads', 's3-as-a-datastore']:
  setup(
    name=name,
    packages=find_packages(), # this must be the same as the name above
    version=version,
    description='S3-as-a-datastore is a library that lives on top of botocore and boto3, as a way to use S3 as a key-value datastore instead of a real datastore',
    long_description = long_description,
    author='joeyism',
    author_email='joeyism@gmail.com',
    url='https://github.com/joeyism/s3-as-a-datastore', # use the URL to the github repo
    download_url='https://github.com/joeyism/s3-as-a-datastore/archive/{}.tar.gz'.format(version),
    keywords=['aws', 's3', 'datastore'], 
    install_requires=[package.split("\n")[0] for package in open("requirements.txt", "r").readlines()],
    classifiers=[],
    )
