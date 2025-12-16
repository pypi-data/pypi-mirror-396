# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool

from . import address, configuration, contact_mechanism, party, user

__all__ = ['register']


def register():
    Pool.register(
        address.Address,
        configuration.Configuration,
        configuration.ConfigurationVCard,
        contact_mechanism.ContactMechanism,
        party.Party,
        party.ActionReport,
        party.PartyVCardCategory,
        user.User,
        user.VCardCategory,
        module='party_vcard', type_='model')
    Pool.register(
        party.VCard,
        module='party_vcard', type_='report')
