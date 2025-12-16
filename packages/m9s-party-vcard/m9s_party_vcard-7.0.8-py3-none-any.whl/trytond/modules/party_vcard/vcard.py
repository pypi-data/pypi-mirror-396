# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import uuid

import vobject

from trytond import __version__
from trytond.model import Unique, fields
from trytond.pool import Pool, PoolMeta
from trytond.report import Report

class VCardCategory(ModelSQL, ModelView):
    'VCard Category'
    __name__ = 'party_vcard4.cvcard'

    category = fields.Many2One(
        'party.category', 'Category', required=True,
        ondelete='CASCADE', readonly=True
    )
    vcard_data = fields.Text('VCard', readonly=True)
    uuid = fields.Char('UUID', readonly=True)
    etag = fields.Char('ETag', readonly=True)
    last_modified = fields.DateTime('Last Modified', readonly=True)
    state = fields.Selection(sel_vcard_state, 'State', readonly=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints.extend([
            ('uuid_uniq', Unique(t, t.uuid), 'UUID must be unique'),
            ('category_uniq', Unique(t, t.category), 'Category must be unique'),
        ])
        cls._sql_indexes.update({
            Index(t, (t.category, Index.Equality())),
            Index(t, (t.state, Index.Equality())),
        })

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('uuid'):
                values['uuid'] = str(uuid.uuid4())
        return super().create(vlist)
