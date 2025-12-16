# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from .configuration import sel_adr_type


class ContactMechanism(metaclass=PoolMeta):
    __name__ = 'party.contact_mechanism'

    vcard_type = fields.Selection(sel_adr_type,
        'VCard Type',
        help='Type of VCard used for this contact mechanism.')

    @classmethod
    def default_vcard_type(cls):
        Configuration = Pool().get('party.configuration')
        cfg = Configuration(1)
        return cfg.contact_type

    @classmethod
    def write(cls, *args):
        pool = Pool()
        Party = pool.get('party.party')

        actions = iter(args)
        parties = set()
        for cm, values in zip(actions, actions):
            parties.add(cm[0].party)
        super().write(*args)
        for party in parties:
            party.ctag = party.increase_ctag(party.ctag)
        Party.save(parties)
