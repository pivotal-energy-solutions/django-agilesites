# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.utils.cache import patch_vary_headers

from .utils import make_tls_property

SITE_ID = settings.__dict__['_wrapped'].__class__.SITE_ID = make_tls_property()
TEMPLATE_LOADERS = settings.__dict__['_wrapped'].__class__.TEMPLATE_LOADERS = make_tls_property(settings.TEMPLATE_LOADERS)

log = logging.getLogger(__name__)


class AgileSitesMiddleware(object):
    """
    Sets settings.SITE_ID based on request's domain.
    Sets settings.TEMPLATE_LOADERS based on request's domain.
    This supports hostname aliases.  Subdomains are not considered.
    """

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

        # At this point the ID is set so leave if we are only ajax.
        if request.is_ajax():
            return

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

        return None


    def process_response(self, request, response):

        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))

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
