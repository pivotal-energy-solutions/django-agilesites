# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import logging
import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.utils.cache import patch_vary_headers

from .utils import make_tls_property

SITE_ID = settings.__dict__['_wrapped'].__class__.SITE_ID = make_tls_property()
TEMPLATE_LOADERS = settings.__dict__['_wrapped'].__class__.TEMPLATE_LOADERS = make_tls_property(settings.TEMPLATE_LOADERS)
STATIC_URL = settings.__dict__['_wrapped'].__class__.STATIC_URL = make_tls_property(settings.STATIC_URL)

# STATICFILES_FINDERS = settings.__dict__['_wrapped'].__class__.STATICFILES_FINDERS = make_tls_property(settings.STATICFILES_FINDERS)

log = logging.getLogger(__name__)


class AgileSitesMiddleware(object):
    """
    Sets settings.SITE_ID based on request's domain.
    Sets settings.TEMPLATE_LOADERS based on request's domain.
    TODO:
    Sets settings.STATICFILES_FINDERS based on request's domain.

    This supports hostname redirects.  Subdomains are not considered.
    """

    def setup_template_loaders(self, site):
        """Sets up the template loader path"""
        dynamic_loader = ("django_agilesites.loaders.AgileSiteAppDirectoriesFinder", site)
        if dynamic_loader[0] not in list(TEMPLATE_LOADERS.value):
            log.debug("Modifying settings.TEMPLATE_LOADERS to use site scope: %r", site)
            self._old_TEMPLATE_LOADERS = settings.TEMPLATE_LOADERS
            template_loaders = list(TEMPLATE_LOADERS.value)
            # Insert the dynamic loader just in front of the normal app_directories one.
            template_loaders.insert(
                template_loaders.index('django.template.loaders.app_directories.Loader'),
                dynamic_loader
            )
            TEMPLATE_LOADERS.value = template_loaders

    # def setup_static_finders(self, site):
    #     """Sets up the static file finder path"""
    #     dynamic_loader = "django_agilesites.finders.AgileSiteAppDirectoriesFinder"
    #     if dynamic_loader[0] not in list(STATICFILES_FINDERS.value):
    #         log.debug("Modifying settings.STATICFILES_FINDERS to use site scope: %r", site)
    #         static_finders = list(STATICFILES_FINDERS.value)
    #         # Insert the dynamic loader just in front of the normal app_directories one.
    #         # static_finders.insert(
    #             static_finders.index('django.contrib.staticfiles.finders.FileSystemFinder'),
    #             dynamic_loader
    #         )
    #         print(list(static_finders))
    #         STATICFILES_FINDERS.value = [dynamic_loader]


    def process_request(self, request):

        if request.is_ajax():
            return

        self._old_TEMPLATE_DIRS = getattr(settings, "TEMPLATE_DIRS", None)
        self._old_STATIC_URL = getattr(settings, "STATIC_URL", None)

        self.site_aliases =  getattr(settings, "SITE_ALIASES", {})
        self.default_site_domain =  getattr(settings, "DEFAULT_SITE_DOMAIN", None)

        if not self.default_site_domain:
            raise ImproperlyConfigured("You must have DEFAULT_SITE_DOMAIN defined in settings")

        domain = request.get_host().split(':')[0]


        if domain not in self.site_aliases:
            domain = settings.DEFAULT_SITE_DOMAIN
        else:
            # Convert an alias name into the major name that categorizes the site configuration.
            domain = settings.SITE_ALIASES[domain]

        try:
            site = Site.objects.get(domain=domain)
            log.debug("Using domain: {domain} to site {site!r}".format(domain=domain, site=site))
        except Site.DoesNotExist:
            site = Site.objects.get(id=settings.SITE_ID)
            log.error("Request on domain %r has no matching Site object.  Defaulting to "
                      "{site!r}.".format(site=site))

        SITE_ID.value = site.id

        # At this point the ID is set
        if request.is_ajax():
            return

        self.setup_template_loaders(site)

        if settings.SITE_FOLDERS.get(domain):
            url = os.path.join(self._old_STATIC_URL, settings.SITE_FOLDERS[domain])
            url += "/" if self._old_STATIC_URL.endswith("/") else ""
            log.debug("Using static url for: {domain} to site {url}".format(domain=domain, url=url))
            STATIC_URL.value = url

        # self.setup_static_finders(site)
        return None  # Continue normally


    def process_response(self, request, response):

        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))
        # reset TEMPLATE_DIRS because we unconditionally add to it when
        # processing the request

        try:
            if self._old_TEMPLATE_DIRS is not None:
                settings.TEMPLATE_DIRS = self._old_TEMPLATE_DIRS
        except AttributeError:
            pass

        try:
            if self._old_STATIC_URL is not None:
                settings.STATIC_URL = self._old_STATIC_URL
        except AttributeError:
            pass

        return response
