# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval


class TaxTemplate(metaclass=PoolMeta):
    __name__ = 'account.tax.template'

    es_facturae_type = fields.Selection(
            'get_es_facturae_types', "Facturae Type")

    @classmethod
    def get_es_facturae_types(cls):
        pool = Pool()
        Tax = pool.get('account.tax')
        field_name = 'es_facturae_type'
        return Tax.fields_get([field_name])[field_name]['selection']

    def _get_tax_value(self, tax=None):
        values = super()._get_tax_value(tax)
        if not tax or tax.es_facturae_type != self.es_facturae_type:
            values['es_facturae_type'] = self.es_facturae_type
        return values


class Tax(metaclass=PoolMeta):
    __name__ = 'account.tax'

    es_facturae_type = fields.Selection([
        (None, ''),
        ('01', "Value-Added Tax"),
        ('02', "Taxes on production, services and imports in Ceuta and "
            "Melilla"),
        ('03', "IGIC: Canaries General Indirect Tax"),
        ('04', "IRPF: Personal Income Tax"),
        ('05', "Other"),
        ('06', "ITPAJD: Tax on wealth transfers and stamp duty"),
        ('07', "IE: Excise duties and consumption taxes"),
        ('08', "Ra: Customs duties"),
        ('09', "IGTECM: Sales tax in Ceuta and Melilla"),
        ('10', "IECDPCAC: Excise duties on oil derivates in Canaries"),
        ('11', "IIIMAB: Tax on premises that affect the environment in the "
            "Balearic Islands"),
        ('12', "ICIO: Tax on construction, installation and works"),
        ('13', "IMVDN: Local tax on unoccupied homes in Navarre"),
        ('14', "IMSN: Local tax on building plots in Navarre"),
        ('15', "IMGSN: Local sumptuary tax in Navarre"),
        ('16', "IMPN: Local tax on advertising in Navarre"),
        ('17', "REIVA: Special VAT for travel agencies"),
        ('18', "REIGIC: Special IGIC: for travel agencies"),
        ('19', "REIPSI: Special IPSI for travel agencies"),
        ('20', "IPS: Insurance premiums Tax"),
        ('21', "SWUA: Surcharge for Winding Up Activity"),
        ('22', "IVPEE: Tax on the value of electricity generation"),
        ('23', "Tax on the production of spent nuclear fuel and radioactive "
            "waste from the generation of nuclear electric power"),
        ('24', "Tax on the storage of spent nuclear energy and radioactive "
            "waste in centralised facilities"),
        ('25', "IDEC: Tax on bank deposits"),
        ('26', "Excise duty applied to manufactured tobacco in Canaries"),
        ('27', "IGFEI: Tax on Fluorinated Greenhouse Gases"),
        ('28', "IRNR: Non-resident Income Tax"),
        ('29', "Corporation Tax"),
        ], "Facturae Type",
        states={
        'readonly': (Bool(Eval('template', -1))
            & ~Eval('template_override', False)),
        })


class PaymentTerm(metaclass=PoolMeta):
    __name__ = 'account.invoice.payment_term'

    es_facturae_type = fields.Selection([
        (None, ''),
        ('01', 'In Cash'),
        ('02', 'Direct debit'),
        ('03', 'Receipt'),
        ('04', 'Credit transfer'),
        ('05', 'Accepted bill of exchange'),
        ('06', 'Documentary credit'),
        ('07', 'Contract award'),
        ('08', 'Bill of exchange'),
        ('09', 'Transferable promissory note'),
        ('10', 'Non transferable promissory note'),
        ('11', 'Cheque'),
        ('12', 'Open account reimbursement'),
        ('13', 'Special payment'),
        ('14', 'Set-off by reciprocal credits'),
        ('15', 'Payment by postgiro'),
        ('16', 'Certified cheque'),
        ('17', 'Banker’s draft'),
        ('18', 'Cash on delivery'),
        ('19', 'Payment by card'),
        ], "Facturae Type")


class InvoiceAdministrativeCenter(ModelSQL):
    "Invoice - Administrative Center"
    __name__ = 'account.invoice.es_facturae_administrative_center'

    invoice = fields.Many2One('account.invoice', "Invoice",
        ondelete='CASCADE', required=True)
    administrative_center = fields.Many2One(
        'edocument.es_facturae.administrative_center', "Administrative Center",
        ondelete='RESTRICT', required=True)


class InvoiceCorrectiveInvoice(ModelSQL, ModelView):
    "Invoice - Correction Invoice"
    __name__ = 'account.invoice.es_facturae_corrective_invoice'

    invoice = fields.Many2One('account.invoice', "Invoice",
        ondelete='CASCADE', required=True)
    corrective_invoice = fields.Many2One(
        'account.invoice', "Correction Invoice", ondelete='CASCADE',
        domain=[
            ('state', '!=', 'draft'),
            ('id', '!=', Eval('invoice', 0)),
            ],
        required=True)
    reason = fields.Selection([
        ('01', "Invoice number"),
        ('02', "Invoice serial number"),
        ('03', "Issue date"),
        ('04', "Name and surnames/Corporate name – Issuer (Sender)"),
        ('05', "Name and surnames/Corporate name - Receiver"),
        ('06', "Issuer's Tax Identification Number"),
        ('07', "Receiver's Tax Identification Number"),
        ('08', "Issuer's address"),
        ('09', "Receiver's address"),
        ('10', "Item Line"),
        ('11', "Applicable Tax Rate"),
        ('12', "Applicable Tax Amount"),
        ('13', "Applicable Date/Period"),
        ('14', "Invoice Class"),
        ('15', "Applicable Date/Period"),
        ('16', "Taxable Base"),
        ('80', "Calculation of tax outputs"),
        ('81', "Calculation of tax inputs"),
        ('82', "Taxable Base modified due to return of packages and packaging "
        "materials"),
        ('83', "Taxable Base modified due to discounts and rebates"),
        ('84', "Taxable Base modified due to firm court ruling or "
        "administrative decision"),
        ('85', "Taxable Base modified due to unpaid outputs where there is a "
        "judgement opening insolvency proceedings"),
        ], "Reason", required=True)
    method = fields.Selection([
        ('01', "Full Items"),
        ('02', "Corrected Items Only"),
        ('03', "Bulk deal in a given period"),
        ('04', "Authorized by the Tax Agency"),
        ], "Method", required=True)

    @property
    def invoice_number(self):
        return self.corrective_invoice.number

    @property
    def invoice_series_code(self):
        return ''

    @property
    def tax_period_start_date(self):
        return (self.corrective_invoice.accounting_date
            or self.corrective_invoice.invoice_date)

    @property
    def tax_period_end_date(self):
        return (self.corrective_invoice.accounting_date
            or self.corrective_invoice.invoice_date)

    @property
    def corrective_invoice_issue_date(self):
        return self.corrective_invoice.invoice_date

    @property
    def reason_description(self):
        return {
            '01': "Número de la factura",
            '02': "Serie de la factura",
            '03': "Fecha expedición",
            '04': "Nombre y apellidos/Razón Social-Emisor",
            '05': "Nombre y apellidos/Razón Social-Receptor",
            '06': "Identificación fiscal Emisor/obligado",
            '07': "Identificación fiscal Receptor",
            '08': "Domicilio Emisor/Obligado",
            '09': "Domicilio Receptor",
            '10': "Detalle Operación",
            '11': "Porcentaje impositivo a aplicar",
            '12': "Cuota tributaria a aplicar",
            '13': "Fecha/Periodo a aplicar",
            '14': "Clase de factura",
            '15': "Literales legales",
            '16': "Base imponible",
            '80': "Cálculo de cuotas repercutidas",
            '81': "Cálculo de cuotas retenidas",
            '82': "Base imponible modificada por devolución de envases / "
            "embalajes",
            '83': "Base imponible modificada por descuentos y bonificaciones",
            '84': "Base imponible modificada por resolución firme, judicial "
            "o administrativa",
            '85': "Base imponible modificada cuotas repercutidas no "
            "satisfechas. Auto de declaración de concurso",
            }.get(self.reason, self.reason)

    @property
    def method_description(self):
        return {
            '01': "Rectificación íntegra",
            '02': "Rectificación por diferencias",
            '03': "Rectificación por descuento por volumen de operaciones "
            "durante un periodo",
            '04': "Autorizadas por la Agencia Tributaria",
            }.get(self.method, self.method)


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    es_facturae_administrative_centers = fields.Many2Many(
        'account.invoice.es_facturae_administrative_center', 'invoice',
        'administrative_center', "Administrative Centers",
        domain=[
            ('party', '=', Eval('party')),
            ])
    es_facturae_corrective_invoices = fields.One2Many(
        'account.invoice.es_facturae_corrective_invoice', 'invoice',
        "Corrective Invoices")

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._check_modify_exclude.add('es_facturae_administrative_centers')
        cls._check_modify_exclude.add('es_facturae_corrective_invoices')

    @fields.depends('party', 'es_facturae_administrative_centers')
    def on_change_party(self):
        super().on_change_party()
        if self.party:
            centers = []
            roles = set()
            for c in self.party.es_facturae_administrative_centers:
                if c.role not in roles:
                    centers.append(c.id)
                    roles.add(c.role)
            self.es_facturae_administrative_centers = centers
