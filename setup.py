#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='journal',
      version='0.1.0',
      description='Simple Journal Editor',
      author='Luyao Zou',
      packages=find_packages('.'),
      entry_points={
        'gui_scripts': [
            'journal = journal:launch',
        ]},
      install_requires=[
            'PyQt5>=5.10',
        ],
      extras_require={
        ':python_version<"3.7"': ['importlib_resources'],
      },
      license='MIT',
)
