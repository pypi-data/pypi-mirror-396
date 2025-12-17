# noirnote-cli/setup.py

from setuptools import setup, find_packages
import os

# Function to read the contents of the README file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='noirnote-cli',
    version='0.1.0',
    author='NoirNote',
    author_email='remikapler@gmail.com',
    description='A CLI for securely fetching secrets from the NoirNote application.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/sync0n/noirnote-cli', 
    license='MIT',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        'click>=8.0',
        'requests>=2.25',
        'pycryptodome>=3.10',
        'cryptography>=3.4',
        'pyrebase4>=4.7.1',
        'setuptools>=68.0',
        'keyring>=24.0.0',
        'keyrings.cryptfile>=1.3.4',
        'questionary>=2.0.0',
        'prompt_toolkit>=3.0.0',
        'rich>=12.0.0'  # <-- ADD THE NEW DEPENDENCY
    ],
    entry_points={
        'console_scripts': [
            'noirnote-cli = noirnote_cli.main:cli',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    python_requires='>=3.8',
)