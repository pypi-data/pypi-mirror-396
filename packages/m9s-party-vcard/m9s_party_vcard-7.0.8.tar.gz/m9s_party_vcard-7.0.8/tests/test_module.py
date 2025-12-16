# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction


class PartyVcardTestCase(ModuleTestCase):
    "Test Party Vcard module"
    module = 'party_vcard'
    extras = ['dav_client']

    @with_transaction()
    def test_party_vcard_report(self):
        'Test Party VCARD report'
        pool = Pool()
        Party = pool.get('party.party')
        VCardReport = pool.get('party_vcard.party.vcard', type='report')

        party1, = Party.create([{
                    'name': 'Party 1',
                    }])
        oext, content, _, _ = VCardReport.execute([party1.id], {})
        self.assertEqual(oext, 'vcf')
        self.assertIn('FN:Party 1', str(content))



del ModuleTestCase
