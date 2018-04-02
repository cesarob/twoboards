from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='twoboards',
    description='Syncs two trello boards',
    packages=find_packages(exclude=('test')),
    install_requires=requirements
)
