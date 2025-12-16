# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta


class Company(metaclass=PoolMeta):
    __name__ = 'company.company'

    es_facturae_private_key = fields.Binary("Facturae Private Key")
    es_facturae_certificate = fields.Binary("Facturae Certificate")
