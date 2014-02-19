#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import cursor_pagination

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = cursor_pagination.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-cursor-pagination',
    version=version,
    description="""Your project description goes here""",
    long_description=readme + '\n\n' + history,
    author='Kevin Stone',
    author_email='kevinastone@gmail.com',
    url='https://github.com/kevinastone/django-cursor-pagination',
    packages=[
        'cursor_pagination',
    ],
    include_package_data=True,
    install_requires=[
        "django>=1.5",
        "django-model-utils",  # Django 1.7 adds native from_queryset support so this won't be needed
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-cursor-pagination',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)