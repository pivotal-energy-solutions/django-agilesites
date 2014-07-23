# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import os
import logging
from django.conf import settings
from django.contrib.sites.models import Site

from django.contrib.staticfiles.finders import AppDirectoriesFinder
from django.contrib.staticfiles.storage import AppStaticStorage
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import SortedDict
from django.utils.importlib import import_module
from django.utils._os import upath

log = logging.getLogger(__name__)


class AgileSiteAppStaticStorage(AppStaticStorage):
    """
    A file system storage backend that takes an app module and works
    for the ``static`` directory of it.
    """
    prefix = None
    source_dir = 'static'

    def __init__(self, app, *args, **kwargs):
        """
        Returns a static file storage if available in the given app.
        """
        # app is the actual app module
        mod = import_module(app)
        mod_path = os.path.dirname(upath(mod.__file__))
        location = os.path.join(mod_path, self.source_dir)
        try:
            self.site = Site.objects.get(pk=settings.SITE_ID)
        except:
            self.site = None
            log.warning("Site {} cannot be found".format(settings.SITE_ID))
        else:
            site_prefix = settings.SITE_FOLDERS.get(self.site.domain)
            if site_prefix is not None:
                location = os.path.join(mod_path, self.source_dir, site_prefix)
                log.debug("{site} Location: {location}".format(site=self.site,  location=location))
        super(AppStaticStorage, self).__init__(location, *args, **kwargs)


class AgileSiteAppDirectoriesFinder(AppDirectoriesFinder):
    """
    A static files finder that looks in the directory of each app as
    specified in the source_dir attribute of the given storage class.
    """
    storage_class = AgileSiteAppStaticStorage

    def __init__(self, apps=None, *args, **kwargs):
        # The list of apps that are handled
        print("Statics: {}".format(kwargs))
        self.apps = []
        # Mapping of app module paths to storage instances
        self.storages = SortedDict()
        if apps is None:
            apps = settings.INSTALLED_APPS
        for app in apps:
            app_storage = self.storage_class(app)
            if os.path.isdir(app_storage.location):
                self.storages[app] = app_storage
                if app not in self.apps:
                    self.apps.append(app)
        super(AgileSiteAppDirectoriesFinder, self).__init__(*args, **kwargs)

