# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from trytond.pool import Pool

from . import account, account_invoice_stock, company, edocument, party

__all__ = ['register']


def register():
    Pool.register(
        account.TaxTemplate,
        account.Tax,
        account.PaymentTerm,
        account.InvoiceAdministrativeCenter,
        account.InvoiceCorrectiveInvoice,
        account.Invoice,
        company.Company,
        party.AdministrativeCenter,
        party.Party,
        party.Address,
        party.Identifier,
        edocument.Invoice,
        module='edocument_es_facturae', type_='model')
    Pool.register(
        account_invoice_stock.InvoiceStock,
        module='edocument_es_facturae', type_='model',
        depends=['account_invoice_stock'])
