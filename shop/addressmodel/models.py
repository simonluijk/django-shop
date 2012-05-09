# -*- coding: utf-8 -*-
"""
Holds all the information relevant to the client (addresses for instance)
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

BASE_ADDRESS_TEMPLATE = \
_("""
Name: %(name)s,
Address: %(address)s,
Zip-Code: %(zipcode)s,
City: %(city)s,
State: %(state)s,
Country: %(country)s
""")

ADDRESS_TEMPLATE = getattr(settings, 'SHOP_ADDRESS_TEMPLATE',
                           BASE_ADDRESS_TEMPLATE)


class Country(models.Model):
    iso_alpha2 = models.CharField(unique=True, max_length=2)
    name = models.CharField(max_length=255)
    common = models.BooleanField(_(u'Common'), default=False)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta(object):
        ordering = ('name',)
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')


class Address(models.Model):
    user_shipping = models.OneToOneField(User, related_name='shipping_address',
                                         blank=True, null=True)
    user_billing = models.OneToOneField(User, related_name='billing_address',
                                        blank=True, null=True)

    name = models.CharField(_('Full name'), max_length=255)
    address = models.CharField(_('Address'), max_length=255)
    address2 = models.CharField(_('Address2'), max_length=255, blank=True)
    city = models.CharField(_('City/Town'), max_length=255)
    zip_code = models.CharField(_('Zip/Post Code'), max_length=20)
    state = models.CharField(_('State/County'), max_length=255, blank=True)
    country = models.ForeignKey(Country, verbose_name=_('Country'))

    class Meta(object):
        verbose_name = _('Address')
        verbose_name_plural = _("Addresses")

    def __unicode__(self):
        return '%s (%s, %s)' % (self.name, self.zip_code, self.city)

    def clone(self):
        new_kwargs = dict([(fld.name, getattr(self, fld.name))
                           for fld in self._meta.fields if fld.name != 'id'])
        return self.__class__.objects.create(**new_kwargs)

    def as_text(self):
        return ADDRESS_TEMPLATE % {
            'name': self.name,
            'address': '%s\n%s' % (self.address, self.address2),
            'zipcode': self.zip_code,
            'city': self.city,
            'state': self.state,
            'country': self.country,
        }

    def get_country_code(self):
        return self.country.iso_alpha2
