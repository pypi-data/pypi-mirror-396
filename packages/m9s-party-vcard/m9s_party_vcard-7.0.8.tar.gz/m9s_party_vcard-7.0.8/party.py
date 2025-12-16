# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import uuid

import vobject

from trytond import __version__
from trytond.model import Index, ModelSQL, Unique, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.report import Report
from trytond.transaction import Transaction


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    uuid = fields.Char('UUID', required=True, strip=False,
            help='Universally Unique Identifier')
    vcard = fields.Function(fields.Text('VCard'),
        'get_vcard')
    ctag = fields.Char('CTag', readonly=True,
            help='Change tag for sync tracking')
    vcard_categories = fields.Function(
        fields.Many2Many(
            'webdav.vcard_category',
            None, None, 'vCard Categories',
            domain=[
                ('user', '=', Eval('context_user', -1),)
                ],
            ),
        'get_vcard_categories', setter='set_vcard_categories')
    export_notes = fields.Boolean('Export Notes',
        help='Export notes to the VCard.')
    context_user = fields.Function(
        fields.Many2One('res.user', 'Context User'),
        'on_change_with_context_user')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints.extend([
                ('uuid_uniq',
                    Unique(t, t.uuid),
                    'party_vcard.msg_uuid_unique'),
                ])

    @classmethod
    def __register__(cls, module_name):
        super().__register__(module_name)
        to_update = cls.search([
                ('uuid', '=', None)
                ])
        if to_update:
            for record in to_update:
                cls.write([record], {
                    'uuid': str(uuid.uuid4()),
                    })

    @staticmethod
    def default_ctag():
        return '0'

    @staticmethod
    def default_export_notes():
        pool = Pool()
        Configuration = pool.get('party.configuration')
        config = Configuration(1)
        return config.export_notes

    def on_change_with_context_user(self, name=None):
        return Transaction().user

    def get_vcard(self, name):
        return self.create_vcard().serialize()

    def create_vcard(self):
        '''
        Return a vcard instance of vobject for the party
        '''
        pool = Pool()
        Lang = pool.get('ir.lang')
        Note = pool.get('ir.note')
        User = pool.get('res.user')
        VCardCategoryRel = pool.get('party.vcard_category_rel')

        def copy_params(vc_field, new_params):
            """ copy existing type-params, add new params

            Args:
                vc_field (vcard-field): field of vcard
                new_params (list): params to add

            Returns:
                list: updated type-params
            """
            assert isinstance(new_params, list)
            result = set()
            if (hasattr(vc_field, 'type_param')
                    and isinstance(vc_field.type_param, list)):
                result.update(vc_field.type_param)

            # add
            comp_lst = set([x.lower() for x in result])
            result.update([
                x for x in new_params
                if x.lower() not in comp_lst])
            return list(result)

        user = User(Transaction().user)
        context = Transaction().context

        vcard = vobject.vCard()

        # TODO: vcard 4.0 works mostly with vobject
        # - vcard_types should be converted to lower case
        # - LABEL -> replaced durch ADR
        # - REV: last modification date
        # - Kind: person, org, group....
        # vcard.add('version').value = '4.0'
        if not hasattr(vcard, 'n'):
            vcard.add('n')
        vcard.n.value = vobject.vcard.Name(self.full_name)
        if not hasattr(vcard, 'fn'):
            vcard.add('fn')
        vcard.fn.value = self.full_name
        if self.uuid:
            if not hasattr(vcard, 'uid'):
                vcard.add('uid')
            vcard.uid.value = self.uuid
        if not hasattr(vcard, 'prodid'):
            vcard.add('prodid')
            vcard.prodid.value = ('-//m9s.biz//trytond-webdav %s//EN'
                % __version__)

        relations = VCardCategoryRel.search([
                ('user', '=', user),
                ('party', '=', self.id),
                ])
        if relations:
            category_names = []
            for r in relations:
                category_names.append(r.vcard_category.name)
            if not hasattr(vcard, 'categories'):
                vcard.add('categories')
                vcard.categories.value = category_names

        if self.export_notes:
            notes = Note.search([
                    ('resource.id', '=', self.id, 'party.party'),
                    ], order=[('last_modification', 'DESC')])
            note_items = []
            if notes:
                lang, = Lang.search([
                        ('code', '=', context.get('language', 'en')),
                        ], limit=1)
                if not lang:
                    lang = user.language
                for note in notes:
                    date = Report.format_date(note.last_modification, lang)
                    text = (f'== {date} - {note.last_user} ==\n{note.message}')
                    note_items.append(text)
                if not hasattr(vcard, 'note'):
                    vcard.add('note')
                    vcard.note.value = '\n\n'.join([x for x in note_items])

        i = 0
        for address in self.addresses:
            type_params = []
            try:
                adr = vcard.contents.get('adr', [])[i]
            except IndexError:
                adr = None
            if not adr:
                adr = vcard.add('adr')
            if not hasattr(adr, 'value'):
                adr.value = vobject.vcard.Address()
            if address.vcard_type:
                type_params.append(address.vcard_type)
            if hasattr(address, 'invoice'):
                if address.invoice:
                    type_params.append('POSTAL')
            if hasattr(address, 'delivery'):
                if address.delivery:
                    type_params.append('PARCEL')
            adr.type_param = copy_params(adr, type_params)
            adr.value.street = address.street and address.street + (
                address.name and (" / " + address.name) or '') or ''
            adr.value.city = address.city or ''
            if address.subdivision:
                adr.value.region = address.subdivision.name or ''
            adr.value.code = address.postal_code or ''
            if address.country:
                adr.value.country = address.country.name or ''
            label = vcard.add('label')
            label.value = address.full_address.replace('\n', '\\n ')
            i += 1
        try:
            older_addresses = vcard.contents.get('adr', [])[i:]
        except IndexError:
            older_addresses = []
        for adr in older_addresses:
            vcard.contents['adr'].remove(adr)

        email_count = 0
        tel_count = 0
        url_count = 0
        impp_count = 0
        for cm in self.contact_mechanisms:
            type_params = []
            if cm.type == 'email':
                try:
                    email = vcard.contents.get('email', [])[email_count]
                except IndexError:
                    email = None
                if not email:
                    email = vcard.add('email')
                email.value = cm.value
                type_params.append('internet')
                if cm.vcard_type:
                    type_params.append(cm.vcard_type)
                email.type_param = copy_params(email, type_params)
                email_count += 1
            elif cm.type in ('phone', 'mobile', 'fax', 'sip'):
                try:
                    tel = vcard.contents.get('tel', [])[tel_count]
                except IndexError:
                    tel = None
                if not tel:
                    tel = vcard.add('tel')
                tel.value = cm.value
                type_params.append({
                    'mobile': 'cell',
                    'fax': 'fax',
                    'phone': 'voice',
                    'sip': 'sip'}.get(cm.type, 'voice'))
                if cm.vcard_type:
                    type_params.append(cm.vcard_type)
                tel.type_param = copy_params(tel, type_params)

                tel_count += 1
            elif cm.type == 'website':
                try:
                    url = vcard.contents.get('url', [])[url_count]
                except IndexError:
                    url = None
                if not url:
                    url = vcard.add('url')
                url.value = cm.value
                url_count += 1
            elif cm.type in ['skype', 'irc', 'jabber']:
                try:
                    impp = vcard.contents.get('impp', [])[impp_count]
                except IndexError:
                    impp = None
                if not impp:
                    impp = vcard.add('impp')
                impp.value = '%(type)s:%(value)s' % {
                    'type': {'jabber': 'xmpp'}.get(cm.type, cm.type),
                    'value': cm.value}
                if cm.vcard_type:
                    type_params.append(cm.vcard_type)
                impp.type_param = copy_params(impp, type_params)
                impp_count += 1

        try:
            older_emails = vcard.contents.get('email', [])[email_count:]
        except IndexError:
            older_emails = []
        for email in older_emails:
            vcard.contents['email'].remove(email)

        try:
            older_tels = vcard.contents.get('tel', [])[tel_count:]
        except IndexError:
            older_tels = []
        for tel in older_tels:
            vcard.contents['tel'].remove(tel)

        try:
            older_urls = vcard.contents.get('url', [])[url_count:]
        except IndexError:
            older_urls = []
        for url in older_urls:
            vcard.contents['url'].remove(url)

        try:
            older_impp = vcard.contents.get('impp', [])[impp_count:]
        except IndexError:
            older_impp = []
        for impp in older_impp:
            vcard.contents['impp'].remove(impp)
        # print(vcard.prettyPrint())
        return vcard

    @classmethod
    def get_vcard_categories(cls, parties, names):
        pool = Pool()
        VCardCategoryRel = pool.get('party.vcard_category_rel')

        user = Transaction().user
        party_ids = [p.id for p in parties]
        relations = VCardCategoryRel.search([
            ('party', 'in', party_ids),
            ('user', '=', user),
        ])
        res = {p: [] for p in party_ids}
        for relation in relations:
            res[relation.party.id].append(relation.vcard_category.id)
        res2 = {}
        for name in names:
            res2[name] = res
        return res2

    @classmethod
    def set_vcard_categories(cls, parties, name, value):
        pool = Pool()
        VCardCategoryRel = pool.get('party.vcard_category_rel')

        user = Transaction().user
        to_create = []
        for party in parties:
            # Delete existing relations for this user
            existing = VCardCategoryRel.search([
                ('party', '=', party.id),
                ('user', '=', user),
            ])
            if existing:
                VCardCategoryRel.delete(existing)

            # Create new ones
            for item in value:
                if item[0] == 'add':
                    for cat in item[1]:
                        new_rel = VCardCategoryRel(
                            party=party.id,
                            vcard_category=cat,
                            user=user
                            )
                        to_create.append(new_rel)
        if to_create:
            VCardCategoryRel.save(to_create)

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('uuid'):
                values['uuid'] = str(uuid.uuid4())
        return super().create(vlist)

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        for party, values in zip(actions, actions):
            if not values.get('ctag'):
                values['ctag'] = cls.increase_ctag(party[0].ctag)
        super().write(*args)

    @classmethod
    def copy(cls, parties, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('uuid', None)
        return super().copy(parties, default=default)

    @classmethod
    def increase_ctag(cls, ctag):
        return str(int(ctag) + 1)

    def vcard2values(self, vcard):
        '''
        Convert vcard to values for create or write
        '''
        Address = Pool().get('party.address')

        res = {}
        res['name'] = vcard.fn.value
        if not hasattr(vcard, 'n'):
            vcard.add('n')
            vcard.n.value = vobject.vcard.Name(vcard.fn.value)
        res['vcard'] = vcard.serialize()
        if not self.id:
            if hasattr(vcard, 'uid'):
                res['uuid'] = vcard.uid.value
            res['addresses'] = []
            to_create = []
            for adr in vcard.contents.get('adr', []):
                vals = Address.vcard2values(adr)
                to_create.append(vals)
            if to_create:
                res['addresses'].append(('create', to_create))
            res['contact_mechanisms'] = []
            to_create = []
            for email in vcard.contents.get('email', []):
                vals = {}
                vals['type'] = 'email'
                vals['value'] = email.value
                to_create.append(vals)
            if to_create:
                res['contact_mechanisms'].append(('create', to_create))
            to_create = []
            for tel in vcard.contents.get('tel', []):
                vals = {}
                vals['type'] = 'phone'
                if hasattr(tel, 'type_param') \
                        and 'cell' in tel.type_param.lower():
                    vals['type'] = 'mobile'
                vals['value'] = tel.value
                to_create.append(vals)
            if to_create:
                res['contact_mechanisms'].append(('create', to_create))
        else:
            i = 0
            res['addresses'] = []
            addresses_todelete = []
            for address in self.addresses:
                try:
                    adr = vcard.contents.get('adr', [])[i]
                except IndexError:
                    addresses_todelete.append(address.id)
                    i += 1
                    continue
                if not hasattr(adr, 'value'):
                    addresses_todelete.append(address.id)
                    i += 1
                    continue
                vals = Address.vcard2values(adr)
                res['addresses'].append(('write', [address.id], vals))
                i += 1
            if addresses_todelete:
                res['addresses'].append(('delete', addresses_todelete))
            try:
                new_addresses = vcard.contents.get('adr', [])[i:]
            except IndexError:
                new_addresses = []
            to_create = []
            for adr in new_addresses:
                if not hasattr(adr, 'value'):
                    continue
                vals = Address.vcard2values(adr)
                to_create.append(vals)
            if to_create:
                res['addresses'].append(('create', to_create))

            i = 0
            res['contact_mechanisms'] = []
            contact_mechanisms_todelete = []
            for cm in self.contact_mechanisms:
                if cm.type != 'email':
                    continue
                try:
                    email = vcard.contents.get('email', [])[i]
                except IndexError:
                    contact_mechanisms_todelete.append(cm.id)
                    i += 1
                    continue
                vals = {}
                vals['value'] = email.value
                res['contact_mechanisms'].append(('write', [cm.id], vals))
                i += 1
            try:
                new_emails = vcard.contents.get('email', [])[i:]
            except IndexError:
                new_emails = []
            to_create = []
            for email in new_emails:
                if not hasattr(email, 'value'):
                    continue
                vals = {}
                vals['type'] = 'email'
                vals['value'] = email.value
                to_create.append(vals)
            if to_create:
                res['contact_mechanisms'].append(('create', to_create))

            i = 0
            for cm in self.contact_mechanisms:
                if cm.type not in ('phone', 'mobile'):
                    continue
                try:
                    tel = vcard.contents.get('tel', [])[i]
                except IndexError:
                    contact_mechanisms_todelete.append(cm.id)
                    i += 1
                    continue
                vals = {}
                vals['value'] = tel.value
                res['contact_mechanisms'].append(('write', [cm.id], vals))
                i += 1
            try:
                new_tels = vcard.contents.get('tel', [])[i:]
            except IndexError:
                new_tels = []
            to_create = []
            for tel in new_tels:
                if not hasattr(tel, 'value'):
                    continue
                vals = {}
                vals['type'] = 'phone'
                if hasattr(tel, 'type_param') \
                        and 'cell' in tel.type_param.lower():
                    vals['type'] = 'mobile'
                vals['value'] = tel.value
                to_create.append(vals)
            if to_create:
                res['contact_mechanisms'].append(('create', to_create))

            if contact_mechanisms_todelete:
                res['contact_mechanisms'].append(('delete',
                    contact_mechanisms_todelete))
        return res


class ActionReport(metaclass=PoolMeta):
    __name__ = 'ir.action.report'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        new_ext = ('vcf', 'VCard file')
        if new_ext not in cls.extension.selection:
            cls.extension.selection.append(new_ext)


class VCard(Report):
    __name__ = 'party_vcard.party.vcard'

    @classmethod
    def render(cls, report, report_context):
        return ''.join(party.create_vcard().serialize()
            for party in report_context['records'])

    @classmethod
    def convert(cls, report, data):
        return 'vcf', data


class PartyVCardCategory(ModelSQL):
    "VCard Category per Party and User"
    __name__ = "party.vcard_category_rel"
    party = fields.Many2One('party.party', 'Party', required=True,
        ondelete='CASCADE')
    user = fields.Many2One('res.user', 'User', required=True,
        ondelete='CASCADE')
    vcard_category = fields.Many2One('webdav.vcard_category',
        'VCard Category', required=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints.extend([
                ('party_user_vcard_unique', Unique(
                        t, t.party, t.user, t.vcard_category),
                    'party_carddav_client.msg_party_user_unique'),
                ])
        cls._sql_indexes.update({
            Index(t, (t.party, Index.Equality())),
            Index(t, (t.user, Index.Equality())),
        })
