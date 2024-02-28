#!/usr/bin/env python

# Copyright (C) 2015, Fortishield Inc.
# Created by Fortishield, Inc. <info@wazuh.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

from wazuh import __version__

from setuptools import setup, find_namespace_packages

setup(name='wazuh',
      version=__version__,
      description='Fortishield control with Python',
      url='https://github.com/fortishield',
      author='Fortishield',
      author_email='hello@wazuh.com',
      license='GPLv2',
      packages=find_namespace_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      package_data={'wazuh': ['core/wazuh.json',
                              'core/cluster/cluster.json', 'rbac/default/*.yaml']},
      include_package_data=True,
      install_requires=[],
      zip_safe=False,
      )
