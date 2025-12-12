# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import os
from decimal import Decimal

from lxml import etree

from trytond.modules.account.tests import create_chart, get_fiscalyear
from trytond.modules.account_invoice.tests import set_invoice_sequences
from trytond.modules.company.tests import create_company, set_company
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction


def create_invoice(company):
    pool = Pool()
    Account = pool.get('account.account')
    Journal = pool.get('account.journal')
    Invoice = pool.get('account.invoice')
    PaymentTerm = pool.get('account.invoice.payment_term')
    Tax = pool.get('account.tax')
    Country = pool.get('country.country')
    Subdivision = pool.get('country.subdivision')
    Party = pool.get('party.party')
    Address = pool.get('party.address')
    Identifier = pool.get('party.identifier')

    spain = Country()
    spain.name = 'Spain'
    spain.code = 'ES'
    spain.code3 = 'ESP'
    spain.save()
    subdivision = Subdivision()
    subdivision.country = spain
    subdivision.type = 'province'
    subdivision.name = 'Murcia'
    subdivision.code = 'ES-MUR'
    subdivision.save()

    address = Address()
    address.street = 'Cartagena 47'
    address.city = 'Ricote'
    address.postal_code = '25192'
    address.subdivision = subdivision
    address.country = spain
    identifier = Identifier()
    identifier.type = 'es_vat'
    identifier.code = 'A12345674'

    party = Party()
    party.name = 'Michael Scott'
    party.addresses = [address]
    party.identifiers = [identifier]
    party.save()

    company_address = company.party.addresses[0]
    company_address.street = 'Main Street 42'
    company_address.city = 'Ricote'
    company_address.postal_code = '08080'
    company_address.subdivision = subdivision
    company_address.country = spain
    company_address.save()
    identifier = Identifier()
    identifier.party = company.party
    identifier.type = 'es_vat'
    identifier.code = 'B25835794'
    identifier.save()

    journal, = Journal.search([
            ('type', '=', 'revenue'),
            ], limit=1)
    invoice_account = party.account_receivable_used
    line_account, = Account.search([
            ('type.revenue', '=', True),
            ], limit=1)
    tax, = Tax.search([
            ('company', '=', company.id),
            ('name', '=', 'IVA 21% (bienes)'),
            ('group.kind', '=', 'sale'),
            ])
    payment_term, = PaymentTerm.create([{
        'name': 'Test',
        'es_facturae_type': '01',
        'lines': [('create', [{}])],
        }])
    invoice, = Invoice.create([{
                'type': 'out',
                'company': company.id,
                'currency': company.currency.id,
                'party': party.id,
                'invoice_address': party.addresses[0].id,
                'journal': journal.id,
                'account': invoice_account.id,
                'payment_term': payment_term.id,
                'lines': [
                    ('create', [{
                                'currency': company.currency.id,
                                'account': line_account.id,
                                'quantity': 1,
                                'description': 'Description',
                                'unit_price': Decimal('100'),
                                'taxes': [('add', [tax.id])],
                                }, {
                                'currency': company.currency.id,
                                'account': line_account.id,
                                'quantity': 1,
                                'description': 'Description',
                                'unit_price': Decimal('0'),
                                'taxes': [('add', [tax.id])],
                                },
                                ]),
                    ],
                }])
    Invoice.post([invoice])
    return invoice


class EdocumentEsFacturaeTestCase(ModuleTestCase):
    "Test Edocument Es Facturae module"
    module = 'edocument_es_facturae'
    extras = ['account_invoice_stock']

    def _test_facturae(self, version, refund_reason=None):
        pool = Pool()
        Template = pool.get('edocument.es.facturae.invoice')
        FiscalYear = pool.get('account.fiscalyear')
        Corrective = pool.get('account.invoice.es_facturae_corrective_invoice')

        company = create_company()
        testdir = os.path.dirname(__file__)
        with open(os.path.join(testdir, 'key.pem'), 'rb') as key:
            company.es_facturae_private_key = key.read()
        with open(os.path.join(testdir, 'cert.pem'), 'rb') as cert:
            company.es_facturae_certificate = cert.read()
        company.save()
        with set_company(company):
            create_chart(company, chart='account_es.pgc_0_pyme')
            fiscalyear = set_invoice_sequences(get_fiscalyear(company))
            fiscalyear.save()
            FiscalYear.create_period([fiscalyear])
            invoice = create_invoice(company)

            if refund_reason:
                refund, = invoice.credit([invoice], refund=True)
                corrective = Corrective()
                corrective.invoice = refund
                corrective.corrective_invoice = invoice
                corrective.reason = refund_reason
                corrective.method = '01'
                corrective.save()
                # Test generating facturae for refunded invoice
                invoice = refund

            template = Template(invoice)
            invoice_string = template.render(version)
            schema_file = os.path.join(testdir, version, 'Facturae.xsd')
            schema = etree.XMLSchema(etree.parse(schema_file))
            schema.assertValid(etree.fromstring(invoice_string))

    @with_transaction()
    def test_facturae_v321(self):
        "Test Facturae Version 3.2.1"
        self._test_facturae('3.2.1')

    @with_transaction()
    def test_facturae_refund_v321(self):
        "Test Facturae Refund Version 3.2.1"
        self._test_facturae('3.2.1', refund_reason='01')

    @with_transaction()
    def test_facturae_v322(self):
        "Test Facturae Version 3.2.2"
        self._test_facturae('3.2.2')

    @with_transaction()
    def test_facturae_refund_v322(self):
        "Test Facturae Refund Version 3.2.2"
        self._test_facturae('3.2.2', refund_reason='01')


del ModuleTestCase
