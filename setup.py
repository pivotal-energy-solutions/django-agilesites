# -*- coding: utf-8 -*-
"""setup.py: Django django-agilesites"""

from setuptools import find_packages, setup

setup(name='django-agilesites',
      version='1.0',
      description='This provides a django the ability of dynamic switching of templates and static directories based on host.',
      author='Steven Klass',
      author_email='sklass@pivotalenergysolutions.com',
      license='Apache License (2.0)',
      classifiers=[
           'Development Status :: 2 - Pre-Alpha',
           'Environment :: Web Environment',
           'Framework :: Django',
           'Intended Audience :: Developers',
           'License :: OSI Approved :: Apache Software License',
           'Operating System :: OS Independent',
           'Programming Language :: Python',
           'Topic :: Software Development',
      ],
      packages=find_packages(exclude=['tests', 'tests.*']),
      package_data={'django_agilesites': ['static/js/*.js', 'templates/appsearch/*.html']},
      include_package_data=True,
      requires=['django (>=1.5)'],
)
