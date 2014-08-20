# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import os
import logging

from django.template.loaders.app_directories import Loader, app_template_dirs
from django.conf import settings
from django.utils._os import safe_join

log = logging.getLogger(__name__)

class AgileSiteAppDirectoriesFinder(Loader):

    def __init__(self, site, *args, **kwargs):
        self.site = site

    def get_template_sources(self, template_name, template_dirs=None):
        site_prefixes = settings.SITE_FOLDERS.get(self.site.domain)

        _app_template_dirs = None
        if site_prefixes is not None:
            if not isinstance(site_prefixes, (list, tuple)):
                site_prefixes = [site_prefixes]
            _app_template_dirs = []
            for app_dir in app_template_dirs:
                for site_prefix in site_prefixes:
                    _app_template_dirs.append(safe_join(app_dir, site_prefix))
            _app_template_dirs = tuple(_app_template_dirs)
        return super(AgileSiteAppDirectoriesFinder, self).get_template_sources(
            template_name, _app_template_dirs)
