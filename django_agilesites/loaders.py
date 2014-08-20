# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import os
import logging
from django.contrib.sites.models import Site

from django.template.loaders.app_directories import Loader, app_template_dirs
from django.core.cache import cache
from django.conf import settings
from django.utils._os import safe_join

log = logging.getLogger(__name__)


class AgileSiteAppDirectoriesFinder(Loader):

    def __init__(self, *args, **kwargs):
        self.logged = False

    def get_template_sources(self, template_name, template_dirs=None):

        site_id = settings.SITE_ID
        site_prefixes = settings.SITE_FOLDERS.get(site_id, [])

        if not self.logged:
            log.error("Getting sources = {} ({}) - {} {}".format(site_id,  site_prefixes,  template_name, template_dirs))
            self.logged = True

        if not isinstance(site_prefixes, (list, tuple)):
            site_prefixes = [site_prefixes]

        _app_template_dirs = []
        if not template_dirs:
            template_dirs = app_template_dirs

        for app_dir in template_dirs:
            for site_prefix in site_prefixes:
                _app_template_dirs.append(safe_join(app_dir, site_prefix))

        _app_template_dirs = tuple(_app_template_dirs) if len(_app_template_dirs) else None
        return super(AgileSiteAppDirectoriesFinder, self).get_template_sources(template_name, _app_template_dirs)

