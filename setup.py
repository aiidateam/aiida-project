from setuptools import setup, find_packages
from os import path

README_PATH = path.join(path.dirname(path.abspath(__file__)), 'README.rst')
with open(README_PATH, 'r') as readme:
    LONG_DESCRIPTION = readme.read()

VERSION = '0.0.1'

setup(
    name='aiida-project',
    version=VERSION,
    author='Rico Haeuselmann',
    license='MIT License',
    description='An AiiDA environment manager',
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    entry_points={
        'console_scripts': ['aipro = aiida_project.commands:main'],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta', 'Topic :: Software Development'
    ],
    install_requires=['click', 'py'],
    )
