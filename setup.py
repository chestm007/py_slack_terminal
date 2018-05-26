from distutils.core import setup

from setuptools import find_packages

setup(
    name='py_slack_term',
    version='0.1.3',
    packages=find_packages(),
    url='https://github.com/chestm007/py_slack_terminal',
    license='GPL-2.0',
    author='max',
    author_email='chestm007@hotmail.com',
    description='Terminal based client for Slack',
    install_requires=[
        "slackclient",
        "npyscreen",
        "pyyaml",
    ],
    entry_points="""
        [console_scripts]
        slack-term=py_slack_term.main:main
    """
)
