from __future__ import unicode_literals
from __future__ import print_function

import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import Q
from django.utils.cache import patch_vary_headers

from .utils import make_tls_property

SITE_ID = settings.__dict__['_wrapped'].__class__.SITE_ID = make_tls_property(settings.SITE_ID)

log = logging.getLogger(__name__)


class AgileSitesMiddleware(object):
    """
    Sets settings.SITE_ID based on request's domain.
    This supports hostname aliases.  Subdomains are not considered.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        domain = request.get_host().split(':')[0]
        self.site_aliases = getattr(settings, "SITE_ALIASES", {})

        query = Q(domain=domain)
        if domain in self.site_aliases:
            query |= Q(id=settings.SITE_ALIASES[domain])

        try:
            site = Site.objects.get(query)
        except Site.MultipleObjectsReturned:
            log.error('Multiple Sites found for query %r', query)
            if domain in self.site_aliases:
                site = Site.objects.get(id=settings.SITE_ALIASES[domain])
            else:
                site = Site.objects.get(domain=domain)
        except Site.DoesNotExist:
            site_id = getattr(settings, 'SITE_ID', 1)
            site, create = Site.objects.get_or_create(id=site_id, defaults={'domain': domain})
            create = "Creating" if create else "Using existing"
            log.error("Request on domain %s (%s) has no matching Site object. %s to %s",
                      "{}".format(domain), "{}".format(query), create, "{!r}".format(site))

        SITE_ID.value = site.id

        # Perform request
        response = self.get_response(request)

        # Process the response

        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))

        return response