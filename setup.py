# -*- coding: utf-8 -*-
"""setup.py: Django django-agilesites"""

from setuptools import find_packages, setup
from django_agilesites import __name__, __version__, __author__

base_url = 'https://github.com/pivotal-energy-solutions/django-agilesites'

setup(
    name=__name__,
    version=__version__,
    description='Simple-history: History for Django Models',
    long_description=open('README.md').read(),
    author=__author__,
    author_email='sklass@pivotalenergysolutions.com',
    url=base_url,
    download_url='{0}/archive/{1}-{1}.tar.gz'.format(base_url, __name__, __version__),
    license='Apache License (2.0)',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={'django_agilesites': ['static/js/*.js']},
    include_package_data=True,
    requires=['django (>=1.5)'])
