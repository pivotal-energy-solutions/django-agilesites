# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import os
import logging

from django.template.loaders.app_directories import Loader
from django.conf import settings

log = logging.getLogger(__name__)

class AgileSiteAppDirectoriesFinder(Loader):

    def __init__(self, site, *args, **kwargs):
        self.site = site

    def get_template_sources(self, template_name, template_dirs=None):
        site_prefixes = settings.SITE_FOLDERS[self.site.domain]
        if site_prefixes is not None:
            if not isinstance(site_prefixes, (list, tuple)):
                site_prefixes = [site_prefixes]
            for site_prefix in site_prefixes:
                template_name = os.path.join(site_prefix, template_name)
        return super(AgileSiteAppDirectoriesFinder, self).get_template_sources(template_name, template_dirs)
