# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.utils.cache import patch_vary_headers

from .utils import make_tls_property

SITE_ID = settings.__dict__['_wrapped'].__class__.SITE_ID = make_tls_property(settings.SITE_ID)

log = logging.getLogger(__name__)


class AgileSitesMiddleware(object):
    """
    Sets settings.SITE_ID based on request's domain.
    Sets settings.TEMPLATE_LOADERS based on request's domain.
    This supports hostname aliases.  Subdomains are not considered.
    """

    def process_request(self, request):

        self.site_aliases = getattr(settings, "SITE_ALIASES", {})
        self.default_site_domain = getattr(settings, "DEFAULT_SITE_DOMAIN", None)

        if not self.default_site_domain:
            raise ImproperlyConfigured("You must have DEFAULT_SITE_DOMAIN defined in settings")

        base_domain = domain = dom = request.get_host().split(':')[0]

        if domain in self.site_aliases:
            domain = settings.SITE_ALIASES[domain]


        try:
            site = Site.objects.get(domain=domain)
            dom = "{base_domain} → {domain}".format(base_domain=base_domain, domain=domain)
            dom = dom if base_domain != domain else domain
            log.info("Using domain: {domain} to site {site!r}".format(domain=dom, site=site))
        except Site.DoesNotExist:
            try:
                site = Site.objects.get(id=settings.SITE_ID)
                log.error("Request on domain %r has no matching Site object.  "
                          "Defaulting to {site!r}.".format(site=site))
            except Site.DoesNotExist:
                site_id = getattr(settings, 'SITE_ID', 1)
                site, create = Site.objects.get_or_create(id=site_id, domain=domain)
                log.error("Request on domain %r has no matching Site object.  "
                          "Creating to {site!r}.".format(site=site))

        SITE_ID.value = site.id

        log.error("Using domain: {domain} to site {site!r} [{site_id}]".format(
            domain=dom,  site=site,  site_id=site.id))

        return None


    def process_response(self, request, response):

        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))

        return response
