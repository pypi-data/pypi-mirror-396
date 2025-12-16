# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from .configuration import sel_adr_type


class Address(metaclass=PoolMeta):
    __name__ = 'party.address'

    vcard_type = fields.Selection(sel_adr_type,
        'VCard Type',
        help='Type of VCard used for this address.')

    @classmethod
    def default_vcard_type(cls):
        Configuration = Pool().get('party.configuration')
        cfg = Configuration(1)
        return cfg.adr_type

    @classmethod
    def write(cls, *args):
        pool = Pool()
        Party = pool.get('party.party')

        actions = iter(args)
        parties = set()
        for addr, values in zip(actions, actions):
            parties.add(addr[0].party)
        super().write(*args)
        for party in parties:
            party.ctag = party.increase_ctag(party.ctag)
        Party.save(parties)

    def vcard2values(self, adr):
        '''
        Convert adr from vcard to values for create or write
        '''
        pool = Pool()
        Country = pool.get('country.country')
        Subdivision = pool.get('country.subdivision')

        vals = {}
        vals['street'] = adr.value.street or ''
        vals['city'] = adr.value.city or ''
        vals['postal_code'] = adr.value.code or ''
        if adr.value.country:
            countries = Country.search([
                    ('rec_name', '=', adr.value.country),
                    ], limit=1)
            if countries:
                country, = countries
                vals['country'] = country.id
                if adr.value.region:
                    subdivisions = Subdivision.search([
                            ('rec_name', '=', adr.value.region),
                            ('country', '=', country.id),
                            ], limit=1)
                    if subdivisions:
                        subdivision, = subdivisions
                        vals['subdivision'] = subdivision.id
        return vals
