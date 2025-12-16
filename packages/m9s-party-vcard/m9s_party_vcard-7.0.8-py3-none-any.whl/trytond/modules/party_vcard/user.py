# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import Index, ModelSQL, ModelView, Unique, fields
from trytond.pool import PoolMeta


class User(metaclass=PoolMeta):
    __name__ = "res.user"
    vcard_categories = fields.One2Many('webdav.vcard_category',
        'user', 'VCard Categories (Contact Groups)')


class VCardCategory(ModelSQL, ModelView):
    'VCard Category'
    __name__ = 'webdav.vcard_category'
    user = fields.Many2One('res.user', 'User', required=True,
        ondelete='CASCADE')
    name = fields.Char("Name", required=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints.extend([
                ('name_uniq', Unique(t, t.user, t.name),
                    'Name must be unique per  user'),
        ])
        cls._sql_indexes.update({
            Index(t, (t.user, Index.Equality())),
            Index(t, (t.name, Index.Equality())),
        })
