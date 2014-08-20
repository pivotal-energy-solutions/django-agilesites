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
    This supports hostname aliases.  Subdomains are not considered.
    """

    def process_request(self, request):

        domain = request.get_host().split(':')[0]
        self.site_aliases = getattr(settings, "SITE_ALIASES", {})

        query = {}
        if domain in self.site_aliases:
            domain_id = settings.SITE_ALIASES[domain]
            query['id'] = domain_id
        else:
            query['domain'] = domain

        try:
            site = Site.objects.get(**query)
            log.info("Using domain: {domain} ({query}) site {site!r}".format(
                domain=domain, query=query, site=site))
        except Site.DoesNotExist:
            site_id = getattr(settings, 'SITE_ID', 1)
            site, create = Site.objects.get_or_create(id=site_id, defaults={'domain':domain})
            create = "Creating" if create else "Using existing"
            log.error("Request on domain {domain} ({query}) has no matching Site object.  "
                      "{create} to {site!r}.".format(domain=domain, query=query, site=site,
                                                     create=create))

        SITE_ID.value = site.id
        return None


    def process_response(self, request, response):

        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))

        return response
