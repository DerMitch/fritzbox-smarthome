
from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fritzhome",
    version="1.0.0b1",

    description="Query information from your FRITZ!Box (mostly energy)",
    long_description=long_description,

    url="https://github.com/DerMitch/fritzbox-smarthome",

    author="Michael Mayr",
    author_email="michael@dermitch.de",

    license="MIT",

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    keywords="fritzbox smarthome avm energy",

    packages=["fritzhome"],

    install_requires=[
        'requests>=2.7.0',
        'click>=4.0.0',
    ],

    entry_points={
        'console_scripts': [
            'fritzhome=fritzhome.__main__:cli',
        ],
    }
)
