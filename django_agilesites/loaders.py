# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import logging

from django.template.loaders import app_directories
from django.conf import settings

from django.utils._os import safe_join

log = logging.getLogger(__name__)


class AgileSiteAppDirectoriesFinder(app_directories.Loader):

    def __init__(self, engine=None, *args, **kwargs):
        self.engine = engine
        self.logged = False

    def get_template_sources(self, template_name, template_dirs=None):
        """This will append the site-prefix to every application template directory.  If
        SITE_ROOT is defined in settings it will scope to your application.  This is to enable
        the file finder to work correctly"""
        return super(AgileSiteAppDirectoriesFinder, self).get_template_sources(template_name)

