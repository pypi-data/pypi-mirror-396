# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.model import ValueMixin
from trytond.pool import Pool, PoolMeta

sel_adr_type = [
    ('OTHER', 'Other'),
    ('WORK', 'Work'),
    ('HOME', 'Home'),
    ]

adr_type = fields.Selection(sel_adr_type,
    'VCard Type for Addresses',
    help='Type of VCard to use for new addresses.')
contact_type = fields.Selection(sel_adr_type,
    string='VCard Type for Contact Mechanisms',
    help='Type of VCard to use for new contact mechanisms.')
export_notes = fields.Boolean('Export Notes',
    help='Export notes to VCards.')


def default_func(field_name):
    @classmethod
    def default(cls, **pattern):
        return getattr(
            cls.multivalue_model(field_name),
            'default_%s' % field_name, lambda: None)()
    return default


class Configuration(metaclass=PoolMeta):
    'Party Configuration'
    __name__ = 'party.configuration'

    adr_type = fields.MultiValue(adr_type)
    contact_type = fields.MultiValue(contact_type)
    export_notes = fields.MultiValue(export_notes)

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field in ['adr_type', 'contact_type', 'export_notes']:
            return pool.get('party.configuration.vcard')
        return super().multivalue_model(field)

    default_adr_type = default_func('adr_type')
    default_contact_type = default_func('contact_type')
    default_export_notes = default_func('export_notes')


class ConfigurationVCard(ModelSQL, ValueMixin):
    'Party Configuration VCard'
    __name__ = 'party.configuration.vcard'

    adr_type = adr_type
    contact_type = contact_type
    export_notes = export_notes

    @classmethod
    def default_export_notes(cls):
        return True

    @classmethod
    def default_adr_type(cls):
        return 'WORK'

    @classmethod
    def default_contact_type(cls):
        return 'WORK'
