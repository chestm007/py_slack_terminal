import time
from distutils.core import setup
import os

from setuptools import find_packages

VERSION = os.environ.get('CIRCLE_TAG') or '0.0.1-post{}'.format(int(time.time()))

setup(
    name='py_slack_term',
    version=VERSION,
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
        'websocket-client==0.48.0'
    ],
    entry_points="""
        [console_scripts]
        slack-term=py_slack_term.main:main
    """
)
